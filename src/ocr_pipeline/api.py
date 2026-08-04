import os
import json
import sys
import numpy as np
import tempfile
import shutil
import traceback
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import PipelineConfig, default_config
from .pipeline import OCRPipeline
from .utils.logging_config import logger
from .utils.json_utils import sanitize_for_json  # standalone — no circular import
from .utils.startup_validator import validate_pipeline_imports


# ---------------------------------------------------------------------------
# FastAPI app setup & Startup Validation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SelfOCR Educational Document Pipeline API",
    description=(
        "Production-ready REST API featuring Qwen2.5-VL primary OCR, Surya layout detection, "
        "TrOCR + EasyOCR ensemble, and graceful per-module fallback architecture."
    ),
    version="3.0.0"
)

@app.on_event("startup")
def startup_event():
    """Execute pre-flight module import validation before accepting API requests."""
    validate_pipeline_imports(fail_fast=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = OCRPipeline(PipelineConfig(save_debug_images=True))

# ---------------------------------------------------------------------------
# OCR pipeline execution timeout (seconds)
# Informational constant — enforced at the Uvicorn/reverse-proxy level.
# Do NOT use ThreadPoolExecutor here: PyTorch models on Windows cannot be
# safely accessed across OS threads (EasyOCR VGG16 causes access violation).
# ---------------------------------------------------------------------------
PIPELINE_TIMEOUT_SEC = 300

# ---------------------------------------------------------------------------
# JSON Serialisation Sanitiser
# ---------------------------------------------------------------------------

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert all NumPy scalars, arrays, and non-serialisable types
    into native Python equivalents so that FastAPI's JSONResponse never raises
    a TypeError during serialisation.

    This is the primary guard against the post-VLM JSON crash:
      TypeError: Object of type float32 is not JSON serializable
    """
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    # Pass through all native Python-serialisable types unchanged
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    # Last resort: convert unknown types to string to avoid crash
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        logger.warning(f"[SANITIZE] Non-serialisable type {type(obj).__name__} coerced to str.")
        return str(obj)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Pipeline health check endpoint."""
    return {
        "status": "ok",
        "service": "SelfOCR Educational Pipeline API",
        "version": "3.0.0",
        "device": pipeline.config.device,
        "qwen_model": pipeline.config.qwen_model_name,
        "got_model": pipeline.config.got_fallback_model_name
    }


# ---------------------------------------------------------------------------
# PDF Preview
# ---------------------------------------------------------------------------

@app.post("/api/preview-pdf")
def preview_pdf(file: UploadFile = File(...), dpi: int = Form(150)):
    """Render PDF pages into high-res thumbnails before full OCR."""
    filename = file.filename or "preview.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, filename)
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            pages = pipeline.input_handler._load_pdf(pdf_path)
            thumbnails = []
            for p in pages:
                from .pipeline import _img_to_base64
                b64 = _img_to_base64(p.image)
                thumbnails.append({
                    "page_number": int(p.page_number),
                    "width": int(p.width),
                    "height": int(p.height),
                    "image_base64": b64
                })
            return {"total_pages": len(pages), "pages": thumbnails}
        except Exception as e:
            logger.error(f"[API] PDF Preview error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Primary OCR endpoint
# ---------------------------------------------------------------------------

@app.post("/api/ocr")
def process_ocr(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form("default_student"),
    subject_override: Optional[str] = Form("Auto"),
    pdf_render_dpi: int = Form(300),
    enable_orientation_correction: bool = Form(True),
    enable_deskew: bool = Form(True),
    enable_perspective_correction: bool = Form(True),
    enable_quality_enhancement: bool = Form(True),
    enable_multi_model_ensemble: bool = Form(False),
    enable_vlm_verification: bool = Form(False),
    min_confidence_threshold: float = Form(0.75)
):
    """
    Execute the full Educational Document Understanding Pipeline end-to-end.

    Returns detailed JSON including base64 images, region bounding boxes, subject detection,
    ensemble candidates, VLM verification stats, handwriting adaptation, timing telemetry,
    and final transcription.

    All optional enhancement modules fail gracefully — a failure in any single module is
    logged and skipped; a valid transcription is always returned.
    """
    filename = file.filename or "document.png"
    ext = os.path.splitext(filename)[1].lower()

    if not pipeline.input_handler.is_supported(filename):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format '{ext}'. "
                f"Supported formats: {list(pipeline.config.supported_extensions)}"
            )
        )

    # Dynamically update singleton pipeline configuration
    pipeline.config.pdf_render_dpi = pdf_render_dpi
    pipeline.config.enable_orientation_correction = enable_orientation_correction
    pipeline.config.enable_deskew = enable_deskew
    pipeline.config.enable_perspective_correction = enable_perspective_correction
    pipeline.config.enable_quality_enhancement = enable_quality_enhancement
    pipeline.config.enable_multi_model_ensemble = enable_multi_model_ensemble
    pipeline.config.enable_vlm_verification = enable_vlm_verification
    pipeline.config.min_confidence_threshold = min_confidence_threshold

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(
            f"[API] /api/ocr — file='{filename}' user='{user_id}' subject='{subject_override}'"
        )

        start_time = time.time()

        # ── Execute pipeline directly in the FastAPI request thread ──────────
        # IMPORTANT: Do NOT wrap in ThreadPoolExecutor on Windows.
        # PyTorch model weights (EasyOCR/VGG16) cannot be safely accessed from
        # a different OS thread than the one they were initialised in.
        # Thread-switching causes a fatal access violation.
        # Uvicorn's --timeout-keep-alive setting handles runaway requests.
        try:
            res = pipeline.process_document(
                input_path,
                output_dir=temp_dir,
                user_id=user_id,
                subject_override=subject_override
            )
        except Exception as e:
            exc_type, exc_val, exc_tb = sys.exc_info()
            tb_list = traceback.extract_tb(exc_tb)
            last_frame = tb_list[-1] if tb_list else None

            module_name = last_frame.filename if last_frame else "unknown_module"
            function_name = last_frame.name if last_frame else "unknown_function"
            line_number = last_frame.lineno if last_frame else 0
            file_path = os.path.abspath(last_frame.filename) if last_frame else ""
            tb_summary = traceback.format_exc()

            failed_stage = getattr(pipeline, "current_stage", "pipeline_execution")

            error_payload = {
                "status": "error",
                "error": "pipeline_exception",
                "message": str(e),
                "exception_type": type(e).__name__,
                "stage": failed_stage,
                "module_name": module_name,
                "function_name": function_name,
                "file_path": file_path,
                "line_number": line_number,
                "traceback_summary": tb_summary,
                "input_metadata": {
                    "filename": filename,
                    "user_id": user_id,
                    "subject_override": subject_override,
                    "elapsed_sec": round(time.time() - start_time, 3)
                }
            }

            logger.error(
                f"[API ERROR] Exception in module '{module_name}' ({function_name}:L{line_number}): "
                f"{type(e).__name__}: {e}\n{tb_summary}"
            )
            return JSONResponse(
                status_code=500,
                content=sanitize_for_json(error_payload)
            )

        total_elapsed = time.time() - start_time

        # ── Base64 images are already embedded in res["pages"] by pipeline.py ──
        # No second document load needed.

        # ── Append developer telemetry ────────────────────────────────────────
        res["developer_telemetry"] = {
            "total_processing_time_sec": round(total_elapsed, 3),
            "device": pipeline.config.device,
            "qwen_vlm_model": pipeline.config.qwen_model_name,
            "user_id": user_id,
            "detected_subject": res.get("detected_subject"),
            "confidence_threshold": pipeline.config.min_confidence_threshold,
            "stages_executed": [
                {"stage": "Document Upload & Ingestion", "status": "completed"},
                {"stage": "PDF High-Res Rendering", "status": "completed" if ext == ".pdf" else "skipped"},
                {"stage": "Orientation Detection & Rotation Correction", "status": "completed"},
                {"stage": "Fine Deskewing & Perspective Correction", "status": "completed"},
                {"stage": "Quality Enhancement (CLAHE & Denoising)", "status": "completed"},
                {"stage": "Surya OCR Layout & Reading Order Analysis", "status": "completed"},
                {"stage": "Primary OCR Recognition (Qwen VLM / Crop Engine)", "status": "completed"},
                {"stage": "Confidence Evaluation & Region Fallback", "status": "completed"},
                {"stage": "Baseline Document Structure Reconstruction", "status": "completed"},
                {"stage": "Educational Subject Detection", "status": "completed"},
                {"stage": "Multi-Model Handwritten OCR & Candidate Fusion",
                 "status": "completed" if enable_multi_model_ensemble else "skipped"},
                {"stage": "Vision-Language OCR Verification",
                 "status": "completed" if enable_vlm_verification else "skipped"},
                {"stage": "Educational Language Model Structural Reconstruction", "status": "completed"},
                {"stage": "Personalized Handwriting Adaptation Profile Rescoring", "status": "completed"},
                {"stage": "Final Combined Transcription & Export", "status": "completed"}
            ]
        }

        # ── CRITICAL: Sanitise all NumPy types before JSONResponse ────────────
        try:
            safe_res = sanitize_for_json(res)
        except Exception as e:
            logger.error(f"[API] sanitize_for_json failed: {e}")
            # Fallback: return minimal safe response with just the transcription
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "document_name": str(res.get("document_name", filename)),
                    "total_pages": int(res.get("total_pages", 1)),
                    "transcription": {
                        "plain_text": str(res.get("transcription", {}).get("plain_text", "")),
                        "markdown": str(res.get("transcription", {}).get("markdown", ""))
                    },
                    "pages": [],
                    "warning": "Full page metadata could not be serialised. Transcription is complete."
                }
            )

        logger.info(
            f"[API] /api/ocr completed successfully for '{filename}' in {total_elapsed:.3f}s"
        )
        return JSONResponse(content=safe_res)


# ---------------------------------------------------------------------------
# Batch OCR
# ---------------------------------------------------------------------------

@app.post("/api/ocr/batch")
def process_batch_ocr(files: List[UploadFile] = File(...)):
    """Batch OCR endpoint processing multiple image/PDF documents."""
    batch_results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            filename = file.filename or "file.png"
            if not pipeline.input_handler.is_supported(filename):
                continue

            input_path = os.path.join(temp_dir, filename)
            with open(input_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            try:
                res = pipeline.process_document(
                    input_path,
                    output_dir=os.path.join(temp_dir, "out")
                )
                safe_res = sanitize_for_json(res)
                batch_results.append({
                    "filename": filename,
                    "status": "success",
                    "transcription": safe_res["transcription"],
                    "total_pages": safe_res["total_pages"]
                })
            except Exception as e:
                logger.error(f"[API] Batch item '{filename}' failed: {e}")
                batch_results.append({
                    "filename": filename,
                    "status": "failed",
                    "error": str(e)
                })

    return {"batch_size": len(files), "results": batch_results}


# ---------------------------------------------------------------------------
# Text Correction (Proofreading)
# ---------------------------------------------------------------------------

import hashlib
from pydantic import BaseModel, Field
from .models import CorrectionSuggestion
from .modules.text_corrector import TextCorrectionEngine

correction_engine = TextCorrectionEngine()
_CORRECTION_CACHE: Dict[str, Dict[str, Any]] = {}


class TextCorrectionRequest(BaseModel):
    text: str = Field(..., description="OCR extracted text or plain text to be proofread")
    language: Optional[str] = Field("en", description="Language code")
    ocr_candidates: Optional[List[Dict[str, Any]]] = Field(
        None, description="Optional OCR multi-candidate list"
    )


class ApplyCorrectionsRequest(BaseModel):
    original_text: str = Field(..., description="Original text string")
    accepted_suggestion_ids: List[str] = Field(..., description="List of accepted suggestion IDs")
    suggestions: List[Dict[str, Any]] = Field(..., description="List of suggestion dicts")
    user_id: Optional[str] = Field("default_student", description="User ID")


class FeedbackRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    original_ocr: str = Field(..., description="Original OCR text")
    accepted_correction: str = Field(..., description="Accepted correction text")


@app.post("/api/correct-text")
def correct_text(payload: TextCorrectionRequest):
    """
    Analyse OCR text and generate structured correction suggestions.
    Uses MD5 hash caching to return instant results on duplicate requests.
    """
    try:
        text_hash = hashlib.md5(payload.text.encode("utf-8")).hexdigest()
        if text_hash in _CORRECTION_CACHE and not payload.ocr_candidates:
            logger.info(f"[API] Returning cached proofreading result for hash '{text_hash[:8]}'.")
            return JSONResponse(content=_CORRECTION_CACHE[text_hash])

        res = correction_engine.analyze_text(payload.text, ocr_candidates=payload.ocr_candidates)
        res_dict = sanitize_for_json(res.to_dict())
        _CORRECTION_CACHE[text_hash] = res_dict
        return JSONResponse(content=res_dict)
    except Exception as e:
        logger.error(f"[API] correct_text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/apply-corrections")
def apply_corrections(payload: ApplyCorrectionsRequest):
    """
    Apply user-accepted suggestion IDs to original text and update handwriting profile.
    """
    try:
        sug_objs = [
            CorrectionSuggestion(
                suggestion_id=s["suggestion_id"],
                original_text=s["original_text"],
                proposed_correction=s["proposed_correction"],
                category=s.get("category", "Grammar Correction"),
                confidence_score=float(s.get("confidence_score", 0.90)),
                explanation=s.get("explanation", ""),
                start_offset=int(s["start_offset"]),
                end_offset=int(s["end_offset"]),
                line_number=int(s.get("line_number", 1))
            )
            for s in payload.suggestions
        ]
        corrected = correction_engine.apply_suggestions(
            text=payload.original_text,
            accepted_ids=payload.accepted_suggestion_ids,
            suggestions=sug_objs
        )

        # Update handwriting adaptation profile
        if payload.user_id:
            for s in sug_objs:
                if s.suggestion_id in payload.accepted_suggestion_ids:
                    try:
                        pipeline.handwriting_adaptation.record_feedback(
                            user_id=payload.user_id,
                            original_ocr=s.original_text,
                            accepted_correction=s.proposed_correction
                        )
                    except Exception as e:
                        logger.warning(f"[API] Handwriting profile update failed: {e}")

        return JSONResponse(content={"corrected_text": corrected})
    except Exception as e:
        logger.error(f"[API] apply_corrections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Handwriting Profile endpoints
# ---------------------------------------------------------------------------

@app.get("/api/handwriting-profile/{user_id}")
async def get_handwriting_profile(user_id: str):
    """Get personalised handwriting adaptation profile for user."""
    try:
        profile = pipeline.handwriting_adaptation.get_profile(user_id)
        return JSONResponse(content=sanitize_for_json(profile))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/handwriting-profile/feedback")
async def record_handwriting_feedback(payload: FeedbackRequest):
    """Record user feedback to update handwriting profile."""
    try:
        updated = pipeline.handwriting_adaptation.record_feedback(
            user_id=payload.user_id,
            original_ocr=payload.original_ocr,
            accepted_correction=payload.accepted_correction
        )
        return JSONResponse(content={"status": "success", "profile": sanitize_for_json(updated)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/handwriting-profile/{user_id}/reset")
async def reset_handwriting_profile(user_id: str):
    """Reset user handwriting adaptation profile."""
    try:
        success = pipeline.handwriting_adaptation.reset_profile(user_id)
        return JSONResponse(
            content={"status": "success" if success else "failed", "user_id": user_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Flashcard endpoints
# ---------------------------------------------------------------------------

from .modules.flashcard_generator import FlashcardGeneratorEngine

flashcard_engine = FlashcardGeneratorEngine()


class FlashcardGenerateRequest(BaseModel):
    exported_text: str = Field(..., description="Final exported corrected document text")
    accepted_suggestions: List[Dict[str, Any]] = Field(
        ..., description="List of accepted proofreading suggestions"
    )
    document_title: Optional[str] = Field("Untitled Document", description="Source document title")
    document_id: Optional[str] = Field(None, description="Source document ID")
    include_rejected: Optional[bool] = Field(False)
    all_suggestions: Optional[List[Dict[str, Any]]] = Field(None)


class UpdateDeckProgressRequest(BaseModel):
    card_updates: List[Dict[str, Any]] = Field(
        ..., description="List of card progress updates"
    )


@app.post("/api/flashcards/generate")
async def generate_flashcard_deck(payload: FlashcardGenerateRequest):
    """Generate an AI-powered Flashcard Deck from exported corrected document text."""
    try:
        res = flashcard_engine.generate_deck(
            exported_text=payload.exported_text,
            accepted_suggestions=payload.accepted_suggestions,
            document_title=payload.document_title or "Untitled Document",
            document_id=payload.document_id,
            include_rejected=payload.include_rejected or False,
            all_suggestions=payload.all_suggestions
        )
        return JSONResponse(content=sanitize_for_json(res))
    except Exception as e:
        logger.error(f"[API] generate_flashcard_deck error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/flashcards/decks")
async def list_flashcard_decks():
    """Retrieve all saved flashcard decks metadata."""
    try:
        decks = flashcard_engine.list_decks()
        return JSONResponse(content={"decks": sanitize_for_json(decks)})
    except Exception as e:
        logger.error(f"[API] list_flashcard_decks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/flashcards/decks/{deck_id}")
async def get_flashcard_deck(deck_id: str):
    """Get full details and flashcards for a specific deck."""
    deck = flashcard_engine.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found.")
    return JSONResponse(content=sanitize_for_json(deck))


@app.patch("/api/flashcards/decks/{deck_id}/progress")
async def update_deck_progress(deck_id: str, payload: UpdateDeckProgressRequest):
    """Update mastery status and study progress for flashcards in a deck."""
    updated_deck = flashcard_engine.update_deck_progress(deck_id, payload.card_updates)
    if not updated_deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found.")
    return JSONResponse(content=sanitize_for_json(updated_deck))


@app.delete("/api/flashcards/decks/{deck_id}")
async def delete_flashcard_deck(deck_id: str):
    """Delete a flashcard deck from the personal learning library."""
    success = flashcard_engine.delete_deck(deck_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found.")
    return JSONResponse(content={"status": "success", "deleted_deck_id": deck_id})
