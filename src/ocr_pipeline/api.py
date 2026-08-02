import os
import tempfile
import shutil
import base64
import time
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import PipelineConfig, default_config
from .pipeline import OCRPipeline
from .utils.logging_config import logger

app = FastAPI(
    title="VLM-First Modular OCR API",
    description="Production-ready REST API featuring Qwen2.5-VL primary OCR, Surya layout detection, GOT-OCR 2.0 fallback, and adaptive image preprocessing.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = OCRPipeline(PipelineConfig(save_debug_images=True))

def numpy_to_base64(img: np.ndarray) -> str:
    """Convert RGB NumPy image array to Base64 PNG data URI string."""
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if len(img.shape) == 3 else img
    _, buffer = cv2.imencode(".png", bgr)
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

def draw_bounding_boxes(image: np.ndarray, regions: List[Dict[str, Any]]) -> np.ndarray:
    """
    Draw color-coded region bounding boxes:
    - Blue (0, 120, 255): Primary VLM high confidence text/header
    - Green (0, 200, 100): High confidence title/section
    - Orange (255, 140, 0): GOT-OCR 2.0 fallback reprocessed region
    """
    annotated = image.copy()
    for reg in regions:
        bbox = reg["bbox"]
        xmin, ymin, xmax, ymax = bbox
        reg_type = reg.get("region_type", "Text")
        fallback = reg.get("fallback_triggered", False)

        if fallback:
            color = (255, 140, 0)  # Orange
        elif reg_type in ("Title", "Section-header"):
            color = (0, 200, 100)  # Green
        else:
            color = (0, 120, 255)  # Blue

        cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), color, 2)
        label = f"#{reg['region_id']} [{reg_type}] {int(reg['confidence']*100)}%"
        cv2.putText(annotated, label, (xmin, max(12, ymin - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    return annotated

@app.get("/health")
def health_check():
    """Pipeline health check endpoint."""
    return {
        "status": "ok",
        "service": "VLM OCR Pipeline API",
        "version": "2.0.0",
        "device": pipeline.config.device,
        "qwen_model": pipeline.config.qwen_model_name,
        "got_model": pipeline.config.got_fallback_model_name
    }

@app.post("/api/preview-pdf")
async def preview_pdf(file: UploadFile = File(...), dpi: int = Form(150)):
    """Render PDF pages into high-res page thumbnails before full OCR."""
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
                b64 = numpy_to_base64(p.image)
                thumbnails.append({
                    "page_number": p.page_number,
                    "width": p.width,
                    "height": p.height,
                    "image_base64": b64
                })
            return {"total_pages": len(pages), "pages": thumbnails}
        except Exception as e:
            logger.error(f"PDF Preview error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr")
async def process_ocr(
    file: UploadFile = File(...),
    pdf_render_dpi: int = Form(300),
    enable_orientation_correction: bool = Form(True),
    enable_deskew: bool = Form(True),
    enable_perspective_correction: bool = Form(True),
    enable_quality_enhancement: bool = Form(True),
    min_confidence_threshold: float = Form(0.75)
):
    """
    Execute full VLM OCR pipeline end-to-end.
    Returns detailed JSON with base64 images, region bounding boxes, timing telemetry, and transcription.
    """
    filename = file.filename or "document.png"
    ext = os.path.splitext(filename)[1].lower()

    if not pipeline.input_handler.is_supported(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported: {pipeline.config.supported_extensions}"
        )

    custom_config = PipelineConfig(
        pdf_render_dpi=pdf_render_dpi,
        enable_orientation_correction=enable_orientation_correction,
        enable_deskew=enable_deskew,
        enable_perspective_correction=enable_perspective_correction,
        enable_quality_enhancement=enable_quality_enhancement,
        min_confidence_threshold=min_confidence_threshold,
        save_debug_images=True
    )
    req_pipeline = OCRPipeline(custom_config)

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            start_time = time.time()
            res = req_pipeline.process_document(input_path, output_dir=temp_dir)
            total_elapsed = time.time() - start_time

            # Add base64 images to page results for direct UI rendering
            doc_pages = req_pipeline.input_handler.load_document(input_path)
            for page_idx, p_meta in enumerate(res["pages"]):
                doc_page = doc_pages[page_idx]
                
                p_meta["original_image_base64"] = numpy_to_base64(doc_page.image)

                corrected_img, _ = req_pipeline.orientation_corrector.process(doc_page.image)
                preprocessed_img, _ = req_pipeline.preprocessor.process(corrected_img)
                p_meta["preprocessed_image_base64"] = numpy_to_base64(preprocessed_img)

                annotated_img = draw_bounding_boxes(preprocessed_img, p_meta["regions"])
                p_meta["annotated_image_base64"] = numpy_to_base64(annotated_img)

            res["developer_telemetry"] = {
                "total_processing_time_sec": round(total_elapsed, 3),
                "device": req_pipeline.config.device,
                "qwen_vlm_model": custom_config.qwen_model_name,
                "got_fallback_model": custom_config.got_fallback_model_name,
                "confidence_threshold": custom_config.min_confidence_threshold,
                "stages_executed": [
                    {"stage": "Document Upload & Ingestion", "status": "completed"},
                    {"stage": "PDF High-Res Rendering", "status": "completed" if ext == ".pdf" else "skipped"},
                    {"stage": "Orientation Detection & Rotation Correction", "status": "completed"},
                    {"stage": "Fine Deskewing & Perspective Correction", "status": "completed"},
                    {"stage": "Quality Enhancement (CLAHE & Denoising)", "status": "completed"},
                    {"stage": "Surya OCR Layout & Reading Order Analysis", "status": "completed"},
                    {"stage": "Qwen2.5-VL Primary Page Transcription", "status": "completed"},
                    {"stage": "Confidence Evaluation & GOT-OCR 2.0 Fallback", "status": "completed"},
                    {"stage": "Document Structure Reconstruction & Export", "status": "completed"}
                ]
            }

            return JSONResponse(content=res)

        except Exception as e:
            logger.error(f"API process_ocr failure: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr/batch")
async def process_batch_ocr(files: List[UploadFile] = File(...)):
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
                res = pipeline.process_document(input_path, output_dir=os.path.join(temp_dir, "out"))
                batch_results.append({
                    "filename": filename,
                    "status": "success",
                    "transcription": res["transcription"],
                    "total_pages": res["total_pages"]
                })
            except Exception as e:
                logger.error(f"Batch item '{filename}' failed: {e}")
                batch_results.append({
                    "filename": filename,
                    "status": "failed",
                    "error": str(e)
                })

    return {"batch_size": len(files), "results": batch_results}

import hashlib
from pydantic import BaseModel, Field
from .modules.text_corrector import TextCorrectionEngine

correction_engine = TextCorrectionEngine()
_CORRECTION_CACHE: Dict[str, Dict[str, Any]] = {}

class TextCorrectionRequest(BaseModel):
    text: str = Field(..., description="OCR extracted text or plain text to be proofread")
    language: Optional[str] = Field("en", description="Language code")
    ocr_candidates: Optional[List[Dict[str, Any]]] = Field(None, description="Optional OCR multi-candidate list")

class ApplyCorrectionsRequest(BaseModel):
    original_text: str = Field(..., description="Original text string")
    accepted_suggestion_ids: List[str] = Field(..., description="List of suggestion_ids accepted by user")
    suggestions: List[Dict[str, Any]] = Field(..., description="List of suggestion dict objects")

@app.post("/api/correct-text")
async def correct_text(payload: TextCorrectionRequest):
    """
    Analyze OCR text output and generate structured correction suggestions.
    Uses MD5 text hash caching to return instant results on duplicate requests.
    """
    try:
        text_hash = hashlib.md5(payload.text.encode("utf-8")).hexdigest()
        if text_hash in _CORRECTION_CACHE and not payload.ocr_candidates:
            logger.info(f"Returning server-side cached proofreading result for text hash '{text_hash[:8]}'.")
            return JSONResponse(content=_CORRECTION_CACHE[text_hash])

        res = correction_engine.analyze_text(payload.text, ocr_candidates=payload.ocr_candidates)
        res_dict = res.to_dict()
        _CORRECTION_CACHE[text_hash] = res_dict
        return JSONResponse(content=res_dict)
    except Exception as e:
        logger.error(f"API correct_text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/apply-corrections")
async def apply_corrections(payload: ApplyCorrectionsRequest):
    """
    Apply user-accepted suggestion IDs to original text while preserving document structure.
    """
    try:
        from .models import CorrectionSuggestion
        sug_objs = [
            CorrectionSuggestion(
                suggestion_id=s["suggestion_id"],
                original_text=s["original_text"],
                proposed_correction=s["proposed_correction"],
                category=s.get("category", "Grammar Correction"),
                confidence_score=s.get("confidence_score", 0.90),
                explanation=s.get("explanation", ""),
                start_offset=s["start_offset"],
                end_offset=s["end_offset"],
                line_number=s.get("line_number", 1)
            )
            for s in payload.suggestions
        ]
        corrected = correction_engine.apply_suggestions(
            text=payload.original_text,
            accepted_ids=payload.accepted_suggestion_ids,
            suggestions=sug_objs
        )
        return JSONResponse(content={"corrected_text": corrected})
    except Exception as e:
        logger.error(f"API apply_corrections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from .modules.flashcard_generator import FlashcardGeneratorEngine

flashcard_engine = FlashcardGeneratorEngine()

class FlashcardGenerateRequest(BaseModel):
    exported_text: str = Field(..., description="Final exported corrected document text")
    accepted_suggestions: List[Dict[str, Any]] = Field(..., description="List of accepted proofreading suggestions")
    document_title: Optional[str] = Field("Untitled Document", description="Source document title")
    document_id: Optional[str] = Field(None, description="Source document ID")
    include_rejected: Optional[bool] = Field(False, description="Optionally include unaccepted suggestions")
    all_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Full list of all suggestions")

class UpdateDeckProgressRequest(BaseModel):
    card_updates: List[Dict[str, Any]] = Field(..., description="List of card progress updates (id, is_mastered, is_bookmarked, needs_review)")

@app.post("/api/flashcards/generate")
async def generate_flashcard_deck(payload: FlashcardGenerateRequest):
    """
    Generate an AI-powered Flashcard Deck from exported corrected document and accepted proofreading history.
    Exclusively processes text without invoking OCR or model pipelines again.
    """
    try:
        res = flashcard_engine.generate_deck(
            exported_text=payload.exported_text,
            accepted_suggestions=payload.accepted_suggestions,
            document_title=payload.document_title or "Untitled Document",
            document_id=payload.document_id,
            include_rejected=payload.include_rejected or False,
            all_suggestions=payload.all_suggestions
        )
        return JSONResponse(content=res)
    except Exception as e:
        logger.error(f"API generate_flashcard_deck error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flashcards/decks")
async def list_flashcard_decks():
    """
    Retrieve all saved flashcard decks metadata from user's personal learning library.
    """
    try:
        decks = flashcard_engine.list_decks()
        return JSONResponse(content={"decks": decks})
    except Exception as e:
        logger.error(f"API list_flashcard_decks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flashcards/decks/{deck_id}")
async def get_flashcard_deck(deck_id: str):
    """
    Get full details and flashcards for a specific deck.
    """
    deck = flashcard_engine.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found in learning library.")
    return JSONResponse(content=deck)

@app.patch("/api/flashcards/decks/{deck_id}/progress")
async def update_deck_progress(deck_id: str, payload: UpdateDeckProgressRequest):
    """
    Update mastery status and study progress for flashcards in a deck.
    """
    updated_deck = flashcard_engine.update_deck_progress(deck_id, payload.card_updates)
    if not updated_deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found in learning library.")
    return JSONResponse(content=updated_deck)

@app.delete("/api/flashcards/decks/{deck_id}")
async def delete_flashcard_deck(deck_id: str):
    """
    Delete a flashcard deck from the personal learning library.
    """
    success = flashcard_engine.delete_deck(deck_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found.")
    return JSONResponse(content={"status": "success", "deleted_deck_id": deck_id})


