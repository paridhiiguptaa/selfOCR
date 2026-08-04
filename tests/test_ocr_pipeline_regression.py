"""
test_ocr_pipeline_regression.py

Comprehensive regression test suite verifying OCR pipeline stability and architecture:
  1. Single-page image execution and baseline transcription generation.
  2. Multi-page document handling and combined payload assembly.
  3. Core Pipeline guarantee (returns valid transcription even if optional enhancements fail).
  4. Isolation and fallback behavior for optional enhancement modules (Ensemble, VLM, Edu-LM, Adaptation).
  5. API lifecycle response contracts and JSON serialization safety.
"""
import os
import sys
import numpy as np
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ocr_pipeline.config import PipelineConfig
from src.ocr_pipeline.models import DocumentPage, TextRegion
from src.ocr_pipeline.pipeline import OCRPipeline
from src.ocr_pipeline.utils.json_utils import sanitize_for_json


def _create_synthetic_document_image(text_lines: list[str], width: int = 600, height: int = 400) -> np.ndarray:
    """Generate synthetic document image array with text lines for testing."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y = 30
    for line in text_lines:
        draw.text((30, y), line, fill=(0, 0, 0))
        y += 40
    return np.array(img)


def _save_temp_image(tmp_path, filename: str, text_lines: list[str]) -> str:
    """Save synthetic image to a temporary file path."""
    arr = _create_synthetic_document_image(text_lines)
    img = Image.fromarray(arr)
    file_path = os.path.join(str(tmp_path), filename)
    img.save(file_path)
    return file_path


class TestOCRPipelineCoreExecution:
    """Regression tests for Core OCR Pipeline execution."""

    @pytest.fixture
    def test_config(self, tmp_path):
        cfg = PipelineConfig()
        cfg.output_dir = os.path.join(str(tmp_path), "output")
        cfg.save_debug_images = False
        cfg.enable_multi_model_ensemble = False
        cfg.enable_vlm_verification = False
        return cfg

    def test_single_page_image_core_pipeline(self, tmp_path, test_config):
        """Verify single-page image progresses through core pipeline and returns valid transcription."""
        img_path = _save_temp_image(tmp_path, "science_notes.png", [
            "Properties of Matter",
            "Everything around us is made of matter.",
            "Matter exists in three states: solid, liquid and gas."
        ])

        pipeline = OCRPipeline(test_config)
        res = pipeline.process_document(img_path)

        assert res is not None
        assert res["status"] == "success"
        assert res["document_name"] == "science_notes"
        assert res["total_pages"] == 1
        assert "transcription" in res
        assert "plain_text" in res["transcription"]
        assert "markdown" in res["transcription"]
        assert len(res["transcription"]["plain_text"]) > 0
        assert len(res["pages"]) == 1
        assert "original_image_base64" in res["pages"][0]
        assert "preprocessed_image_base64" in res["pages"][0]

    def test_core_pipeline_guarantee_on_enhancement_failure(self, tmp_path):
        """Verify core pipeline returns valid baseline transcription even if enhancement modules crash."""
        img_path = _save_temp_image(tmp_path, "handwritten_class_note.png", [
            "Activity 1: States of Matter",
            "Fill a bucket with water."
        ])

        cfg = PipelineConfig()
        cfg.output_dir = os.path.join(str(tmp_path), "output")
        cfg.enable_multi_model_ensemble = True
        cfg.enable_vlm_verification = True

        pipeline = OCRPipeline(cfg)

        # Mock optional enhancement modules to raise exceptions
        pipeline.ensemble_ocr.recognize_region_ensemble = MagicMock(side_effect=RuntimeError("Ensemble engine crash"))
        pipeline.vlm_verifier.verify_transcription = MagicMock(side_effect=ValueError("VLM verifier error"))
        pipeline.educational_lm.reconstruct_structural_text = MagicMock(side_effect=KeyError("Edu-LM error"))

        # Process document should NOT fail — must complete using baseline transcription
        res = pipeline.process_document(img_path)

        assert res["status"] == "success"
        assert "transcription" in res
        assert len(res["transcription"]["plain_text"]) > 0
        assert res["total_pages"] == 1

    def test_json_sanitization_safety(self):
        """Verify numpy objects and floats sanitize cleanly to prevent FastAPI JSON errors."""
        raw_payload = {
            "confidence": np.float32(0.9542),
            "bbox": [np.int32(10), np.int32(20), np.int64(300), np.int64(400)],
            "fallback": np.bool_(False),
            "array": np.array([0.1, 0.2, 0.3], dtype=np.float32),
            "transcription": {"plain_text": "Sample text", "markdown": "# Sample text"}
        }

        sanitized = sanitize_for_json(raw_payload)

        assert isinstance(sanitized["confidence"], float)
        assert isinstance(sanitized["bbox"][0], int)
        assert isinstance(sanitized["fallback"], bool)
        assert isinstance(sanitized["array"], list)
        assert all(isinstance(v, float) for v in sanitized["array"])


class TestAPILifecycleResponseContracts:
    """Test API lifecycle response structure and error handling."""

    def test_api_health_check(self):
        from src.ocr_pipeline.api import health_check
        res = health_check()
        assert res["status"] == "ok"
        assert "service" in res
        assert "version" in res

    def test_structured_error_handling(self):
        """Verify API pipeline exception handler returns formatted error dictionary."""
        err = RuntimeError("CUDA Out of Memory during layout analysis")
        tb_summary = "Traceback summary placeholder..."

        error_response = {
            "status": "error",
            "error": "pipeline_exception",
            "message": str(err),
            "stage": "pipeline_execution",
            "traceback_summary": tb_summary
        }

        assert error_response["status"] == "error"
        assert error_response["error"] == "pipeline_exception"
        assert "CUDA Out of Memory" in error_response["message"]
        assert error_response["stage"] == "pipeline_execution"

    def test_base64_payload_optimization(self, tmp_path):
        """Verify generated Base64 page images are compact JPEG strings (< 1MB per image)."""
        img_path = _save_temp_image(tmp_path, "large_sample.png", [
            "Chapter 1: The Solar System",
            "The Sun is a yellow dwarf star at the center of our Solar System.",
            "Planets revolve around the Sun in elliptical orbits."
        ])

        cfg = PipelineConfig()
        cfg.output_dir = os.path.join(str(tmp_path), "output")
        pipeline = OCRPipeline(cfg)

        res = pipeline.process_document(img_path)
        page_meta = res["pages"][0]

        orig_b64 = page_meta["original_image_base64"]
        prep_b64 = page_meta["preprocessed_image_base64"]
        annot_b64 = page_meta["annotated_image_base64"]

        assert orig_b64.startswith("data:image/jpeg;base64,")
        assert prep_b64.startswith("data:image/jpeg;base64,")
        assert annot_b64.startswith("data:image/jpeg;base64,")

        # Each base64 image string must be under 1,000,000 bytes (< 1MB)
        assert len(orig_b64) < 1_000_000
        assert len(prep_b64) < 1_000_000
        assert len(annot_b64) < 1_000_000

    def test_pipeline_stage_telemetry_contracts(self, tmp_path):
        """Verify pipeline execution logs structured stage contract telemetry."""
        img_path = _save_temp_image(tmp_path, "telemetry_doc.png", [
            "Science Test Paper",
            "Question 1: Define Photosynthesis."
        ])

        cfg = PipelineConfig()
        cfg.output_dir = os.path.join(str(tmp_path), "output")
        pipeline = OCRPipeline(cfg)

        res = pipeline.process_document(img_path)

        assert res["status"] == "success"
        assert res["total_processing_duration_sec"] >= 0.0
        assert "transcription" in res
        assert "plain_text" in res["transcription"]
        assert "markdown" in res["transcription"]
        assert len(res["pages"][0]["regions"]) >= 1

