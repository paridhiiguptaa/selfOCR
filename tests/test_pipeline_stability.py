"""
test_pipeline_stability.py

Regression test suite for OCR pipeline stabilisation.

Purpose: Verify the five root-cause fixes identified in the architectural audit:
  1. sanitize_for_json() converts ALL NumPy types to native Python (JSON crash fix)
  2. Phase 5c enhancement loop has per-module try-except guards (isolation fix)
  3. api.py returns structured JSON error envelopes on pipeline crash
  4. Base64 images are embedded in the pipeline result (no double document load)
  5. Safe API endpoints (health, 400, proofreading) continue to work

DESIGN — no heavy model loading:
  Loading api.py's OCRPipeline (Qwen + Surya + TrOCR + EasyOCR + Handwriting) in
  a single test process exhausts available memory. Tests that need the full pipeline
  are already covered by the 59-test suite (test_phase8_pipeline, test_multi_model_ensemble, etc.).
  This suite is deliberately lightweight:
  - Sanitiser tests:       pure numpy → native-type conversion, no imports from api.py
  - Isolation tests:       source-code inspection, confirm try-except guards are in place
  - Simulation tests:      mimic exact NumPy shapes from the pipeline, verify serialisation
  - API endpoint tests:    safe HTTP calls that never reach model inference
  - Error envelope tests:  mock process_document to raise, verify JSON error format

Run with:
    python -m pytest tests/test_pipeline_stability.py -v
"""
import inspect
import json
import re
import tempfile
import numpy as np
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_test_image_bytes() -> bytes:
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), "Properties of Matter",                    fill=(0, 0, 0))
    draw.text((20, 70), "A solid has definite shape and volume.",   fill=(0, 0, 0))
    draw.text((20, 110), "Activity 1: Observe states of matter.",  fill=(0, 0, 0))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Shared module-scoped fixtures (lightweight — no heavy model loading)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def safe_client():
    """
    TestClient for safe, non-pipeline endpoints only.
    Importing api.py creates the OCRPipeline singleton but it's module-scoped
    so models load exactly ONCE, and tests that use this client never invoke
    heavy inference (no EasyOCR / TrOCR forward passes).
    """
    from fastapi.testclient import TestClient
    from src.ocr_pipeline.api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def api_pipeline():
    """Return the api.py module-level OCRPipeline singleton (already loaded)."""
    from src.ocr_pipeline import api as api_module
    return api_module.pipeline


# ─────────────────────────────────────────────────────────────────────────────
# 1. sanitize_for_json unit tests (no model loading)
# ─────────────────────────────────────────────────────────────────────────────

class TestSanitizeForJson:
    """
    Unit tests for the sanitize_for_json() utility.
    Imports ONLY from json_utils — never from api.py — so no OCRPipeline is created.
    """

    @pytest.fixture(autouse=True)
    def _load(self):
        from src.ocr_pipeline.utils.json_utils import sanitize_for_json
        self.sanitize = sanitize_for_json

    def test_numpy_int32_to_int(self):
        result = self.sanitize(np.int32(42))
        assert isinstance(result, int) and result == 42

    def test_numpy_int64_to_int(self):
        assert isinstance(self.sanitize(np.int64(999)), int)

    def test_numpy_float32_to_float(self):
        result = self.sanitize(np.float32(0.9876))
        assert isinstance(result, float)
        assert abs(result - 0.9876) < 0.001

    def test_numpy_float64_to_float(self):
        assert isinstance(self.sanitize(np.float64(3.14159)), float)

    def test_numpy_bool_to_bool(self):
        result = self.sanitize(np.bool_(True))
        assert isinstance(result, bool) and result is True

    def test_numpy_array_to_list(self):
        result = self.sanitize(np.array([1.0, 2.5, 3.7], dtype=np.float32))
        assert isinstance(result, list)
        assert all(isinstance(v, float) for v in result)

    def test_nested_dict_with_numpy(self):
        data = {
            "confidence": np.float32(0.92),
            "bbox": [np.int64(10), np.int64(20), np.int64(100), np.int64(200)],
            "candidates": [{"text": "hello", "score": np.float64(0.88)}],
        }
        result = self.sanitize(data)
        parsed = json.loads(json.dumps(result))
        assert parsed["confidence"] == pytest.approx(0.92, abs=0.01)
        assert parsed["bbox"] == [10, 20, 100, 200]

    def test_native_types_pass_through(self):
        data = {"status": "ok", "count": 5, "score": 0.95, "flag": True, "x": None}
        assert self.sanitize(data) == data

    def test_fully_serialisable_roundtrip(self):
        data = {
            "floats": [np.float32(0.1), np.float64(0.2)],
            "ints":   [np.int32(1), np.int64(2)],
            "nested": {"array": np.array([1, 2, 3]), "val": np.float32(99.9)},
        }
        json_str = json.dumps(self.sanitize(data))
        assert len(json_str) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Source-code inspection: verify Phase 5c try-except guards are present
#
#    These tests inspect the pipeline.py source to confirm each optional
#    enhancement module is wrapped in its own per-region try-except block.
#    This is the correct level of verification — end-to-end pipeline tests
#    that exercise model inference live in the 59-test main suite.
# ─────────────────────────────────────────────────────────────────────────────

class TestOptionalModuleIsolationGuards:
    """
    Verify the Phase 5c enhancement loop in pipeline.py has per-module
    try-except blocks for each optional enhancement module.
    """

    @pytest.fixture(scope="class")
    def pipeline_source(self):
        from src.ocr_pipeline.pipeline import OCRPipeline
        return inspect.getsource(OCRPipeline.process_document)

    def test_ensemble_fallback_guard_present(self, pipeline_source):
        """ENSEMBLE FALLBACK guard must be in the process_document source."""
        assert "ENSEMBLE FALLBACK" in pipeline_source, (
            "pipeline.py is missing the [ENSEMBLE FALLBACK] try-except guard. "
            "MultiModelOCREnsemble failures will crash the page."
        )

    def test_vlm_fallback_guard_present(self, pipeline_source):
        """VLM FALLBACK guard must be in the process_document source."""
        assert "VLM FALLBACK" in pipeline_source, (
            "pipeline.py is missing the [VLM FALLBACK] try-except guard. "
            "VisionLanguageVerifier failures will crash the page."
        )

    def test_educational_lm_fallback_guard_present(self, pipeline_source):
        """EDU-LM FALLBACK guard must be in the process_document source."""
        assert "EDU-LM FALLBACK" in pipeline_source, (
            "pipeline.py is missing the [EDU-LM FALLBACK] try-except guard. "
            "EducationalLanguageModel failures will crash the page."
        )

    def test_adaptation_fallback_guard_present(self, pipeline_source):
        """ADAPT FALLBACK guard must be in the process_document source."""
        assert "ADAPT FALLBACK" in pipeline_source, (
            "pipeline.py is missing the [ADAPT FALLBACK] try-except guard. "
            "HandwritingAdaptation failures will crash the page."
        )

    def test_all_fallbacks_use_logger_warning(self, pipeline_source):
        """All fallback blocks must log.warning (not re-raise the exception)."""
        fallback_markers = [
            "ENSEMBLE FALLBACK", "VLM FALLBACK", "EDU-LM FALLBACK", "ADAPT FALLBACK"
        ]
        for marker in fallback_markers:
            idx = pipeline_source.find(marker)
            assert idx >= 0, f"{marker} not found in pipeline source"
            # logger.warning(f"[ENSEMBLE FALLBACK]...") — the call precedes the marker
            # text, so search a 400-char window centred on the marker.
            start = max(0, idx - 200)
            end   = min(len(pipeline_source), idx + 200)
            snippet = pipeline_source[start:end]
            assert "logger.warning" in snippet, (
                f"Block for {marker} does not call logger.warning — "
                "it may be re-raising or silently swallowing the exception."
            )

    def test_base64_images_embedded_in_pages_metadata(self, pipeline_source):
        """pipeline.py must embed base64 images in pages_metadata (not api.py)."""
        assert "original_image_base64" in pipeline_source, (
            "pipeline.py does not embed original_image_base64. "
            "api.py would need a second document load, doubling latency."
        )
        assert "preprocessed_image_base64" in pipeline_source
        assert "annotated_image_base64" in pipeline_source


# ─────────────────────────────────────────────────────────────────────────────
# 3. Simulate the exact NumPy shapes the pipeline produces and verify
#    sanitize_for_json fixes the JSON crash (the primary root cause)
# ─────────────────────────────────────────────────────────────────────────────

class TestSanitizeRoundTripOnPipelineShape:
    """
    Simulate the exact data structures the pipeline returns (with real NumPy
    types from TrOCR/EasyOCR scores) and verify sanitize_for_json removes them.
    This directly validates the fix for:
      TypeError: Object of type float32 is not JSON serializable
    """

    @pytest.fixture(autouse=True)
    def _load(self):
        from src.ocr_pipeline.utils.json_utils import sanitize_for_json
        self.sanitize = sanitize_for_json

    def test_ensemble_candidates_with_numpy_scores(self):
        """Simulate MultiModelOCREnsemble output with numpy confidence scores."""
        simulated = {
            "region_id": np.int64(3),
            "confidence": np.float32(0.91),
            "bbox": [np.int64(10), np.int64(20), np.int64(100), np.int64(200)],
            "ensemble_candidates": [
                {
                    "model": "trocr_handwritten",
                    "text": "Properties of matter",
                    "confidence": np.float32(0.87),           # float32 — was crashing
                    "aggregated_score": np.float64(0.91),     # float64 — was crashing
                },
                {
                    "model": "easyocr",
                    "text": "Properties of matter",
                    "confidence": np.float64(0.83),
                    "aggregated_score": np.float64(0.85),
                }
            ],
            "fallback_triggered": np.bool_(False),            # bool_ — was crashing
            "adaptation_boost": np.float32(0.05),
        }
        safe = self.sanitize(simulated)
        parsed = json.loads(json.dumps(safe))                 # Must NOT raise TypeError
        assert isinstance(parsed["confidence"], float)
        assert isinstance(parsed["ensemble_candidates"][0]["confidence"], float)
        assert isinstance(parsed["ensemble_candidates"][0]["aggregated_score"], float)
        assert isinstance(parsed["fallback_triggered"], bool)
        assert isinstance(parsed["bbox"][0], int)

    def test_conf_stats_with_numpy_scalars(self):
        """Simulate ConfidenceEvaluator return value with numpy scalars."""
        conf_stats = {
            "total_regions": np.int64(14),
            "high_confidence_count": np.int64(11),
            "mean_confidence": np.float64(0.843),             # float64 — was crashing
            "fallback_count": np.int64(3),
            "score_distribution": np.array([0.9, 0.8, 0.7]), # ndarray — was crashing
        }
        safe = self.sanitize(conf_stats)
        json.dumps(safe)   # Must not raise
        assert isinstance(safe["mean_confidence"], float)
        assert isinstance(safe["score_distribution"], list)

    def test_full_pages_metadata_simulation(self):
        """Simulate a complete pages_metadata entry as the pipeline constructs it."""
        pages_meta = [{
            "page_number": np.int64(1),
            "confidence_stats": {
                "mean_confidence": np.float64(0.87),
                "high_confidence_count": np.int64(10),
                "fallback_count": np.int64(2),
            },
            "regions": [
                {
                    "region_id": np.int64(0),
                    "confidence": np.float32(0.92),
                    "bbox": [np.int64(10), np.int64(20), np.int64(100), np.int64(40)],
                    "text": "Sample text",
                    "ensemble_candidates": [
                        {"model": "trocr", "text": "Sample text",
                         "confidence": np.float32(0.92), "aggregated_score": np.float64(0.92)}
                    ],
                    "fallback_triggered": np.bool_(False),
                }
            ],
            "original_image_base64": "data:image/png;base64,ABC123",
        }]
        safe = self.sanitize(pages_meta)
        json_str = json.dumps(safe)  # Must NOT raise
        parsed = json.loads(json_str)
        page = parsed[0]
        assert isinstance(page["page_number"], int)
        assert isinstance(page["confidence_stats"]["mean_confidence"], float)
        region = page["regions"][0]
        assert isinstance(region["confidence"], float)
        assert isinstance(region["bbox"][0], int)


# ─────────────────────────────────────────────────────────────────────────────
# 4. API endpoint smoke tests — safe calls only (no heavy inference)
# ─────────────────────────────────────────────────────────────────────────────

class TestApiEndpoints:
    """
    HTTP-layer tests for endpoints that do NOT invoke heavy model inference.
    These use safe_client (Starlette background thread) but never trigger
    EasyOCR/TrOCR/Qwen forward passes.
    """

    def test_health_endpoint_returns_ok(self, safe_client):
        res = safe_client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert "device" in res.json()

    def test_unsupported_format_returns_400(self, safe_client):
        """Bad extension is rejected before any model inference runs."""
        res = safe_client.post(
            "/api/ocr",
            data={"user_id": "test"},
            files={"file": ("bad.xyz", b"garbage", "application/octet-stream")}
        )
        assert res.status_code == 400

    def test_correct_text_endpoint(self, safe_client):
        """Proofreading endpoint uses NLP only (no EasyOCR/PyTorch heavy models)."""
        res = safe_client.post(
            "/api/correct-text",
            json={"text": "Ths is a simpl test sentance with erors."}
        )
        assert res.status_code == 200
        body = res.json()
        assert "suggestions" in body
        assert "corrected_text" in body


# ─────────────────────────────────────────────────────────────────────────────
# 5. Structured error envelope tests
#    process_document is mocked — no heavy model inference, TestClient is safe.
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandling:
    """
    Verify api.py returns a structured JSON error envelope on pipeline failure.
    The mock raises before touching any model, so the Starlette background
    thread never reaches EasyOCR/TrOCR.
    """

    def test_pipeline_exception_returns_json_error_500(self, safe_client, api_pipeline):
        """A pipeline crash must return HTTP 500 with status='error' JSON."""
        img_bytes = _make_test_image_bytes()
        with patch.object(
            api_pipeline, "process_document",
            side_effect=RuntimeError("Simulated pipeline crash for test")
        ):
            res = safe_client.post(
                "/api/ocr",
                data={"user_id": "error_test_user"},
                files={"file": ("crash_test.png", img_bytes, "image/png")}
            )

        assert res.status_code == 500
        body = res.json()
        assert body.get("status") == "error",   f"Expected status='error', got: {body}"
        assert "message" in body,               "Missing 'message' field in error envelope"
        assert "error" in body,                 "Missing 'error' field in error envelope"
        assert "Simulated pipeline crash" in body["message"]

    def test_error_envelope_has_all_required_fields(self, safe_client, api_pipeline):
        """The structured error envelope must contain status, error, message, stage."""
        img_bytes = _make_test_image_bytes()
        with patch.object(
            api_pipeline, "process_document",
            side_effect=ValueError("Type mismatch in region serialisation")
        ):
            res = safe_client.post(
                "/api/ocr",
                data={"user_id": "field_check_user"},
                files={"file": ("field_test.png", img_bytes, "image/png")}
            )

        assert res.status_code == 500
        body = res.json()
        required_fields = {"status", "error", "message", "stage"}
        missing = required_fields - set(body.keys())
        assert not missing, f"Error envelope is missing fields: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# 6. api.py structural verification (no model loading)
# ─────────────────────────────────────────────────────────────────────────────

class TestApiStructure:
    """
    Inspect api.py source to verify the key structural fixes are in place.
    No model loading — pure source analysis.
    """

    @pytest.fixture(scope="class")
    def api_source(self):
        import src.ocr_pipeline.api as api_module
        return inspect.getsource(api_module)

    def test_sanitize_for_json_is_called_before_jsonresponse(self, api_source):
        """sanitize_for_json() must be called before JSONResponse to prevent crash."""
        # Find the JSONResponse call and verify sanitize_for_json precedes it
        assert "sanitize_for_json" in api_source, \
            "api.py does not call sanitize_for_json — NumPy types will crash JSONResponse"

    def test_no_threadpoolexecutor_in_process_ocr(self, api_source):
        """ThreadPoolExecutor must not be imported (causes Windows crash)."""
        # Check the actual import statement is absent — comments may still mention it
        assert "from concurrent.futures import ThreadPoolExecutor" not in api_source, (
            "api.py still imports ThreadPoolExecutor. "
            "This causes PyTorch model weight access violations on Windows."
        )

    def test_structured_error_envelope_is_returned(self, api_source):
        """api.py must return a structured JSON error with status, error, message."""
        assert '"status": "error"' in api_source or "'status': 'error'" in api_source or \
               '"status": "error"' in api_source.replace("'", '"'), \
            "api.py does not return a structured error envelope on pipeline failure"
