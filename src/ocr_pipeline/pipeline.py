import os
import cv2
import time
import base64
import traceback
import sys
import numpy as np
from typing import Dict, Any, List, Optional

from .config import PipelineConfig, default_config
from .models import (
    DocumentPage, TextRegion,
    IngestionOutput, PreprocessingOutput, LayoutOutput,
    PrimaryOCROutput, ConfidenceOutput, TranscriptionOutput, EnhancementOutput
)
from .utils.logging_config import logger, Timer
from .utils.image_utils import save_image
from .modules.input_handler import InputHandler
from .modules.orientation_corrector import OrientationCorrector
from .modules.image_preprocessor import ImagePreprocessor
from .modules.document_analyzer import DocumentAnalyzer
from .modules.surya_layout_analyzer import SuryaLayoutAnalyzer
from .modules.qwen_vlm_ocr import QwenVLMOCR
from .modules.confidence_evaluator import ConfidenceEvaluator
from .modules.layout_reconstructor import LayoutReconstructor
from .modules.exporter import Exporter

from .modules.text_corrector import TextCorrectionEngine
from .modules.subject_detection import SubjectDetectionModule
from .modules.educational_language_model import EducationalLanguageModel
from .modules.handwriting_adaptation import HandwritingAdaptationModule
from .modules.crop_ocr_engine import CropOCREngine
from .modules.multi_model_ocr_ensemble import MultiModelOCREnsemble
from .modules.vlm_verifier import VisionLanguageVerifier


def _get_memory_mb() -> float:
    """Helper to retrieve current process RSS RAM usage in MB."""
    try:
        import psutil
        return round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
    except Exception:
        return 0.0


def _img_to_base64(img: np.ndarray, max_dim: int = 1280) -> str:
    """
    Convert RGB NumPy array to compact Base64 JPEG data URI.
    Downscales large high-res images to max_dim (1280px) and applies JPEG quality 80
    to optimize network payload size from ~30MB to <1MB per page.
    """
    if img is None or img.size == 0:
        return ""
    try:
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if len(img.shape) == 3 else img
        success, buffer = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not success:
            return ""
        b64 = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        logger.warning(f"[PIPELINE] Base64 image encoding failed: {e}")
        return ""


def _draw_bounding_boxes(image: np.ndarray, regions: List[Dict[str, Any]]) -> np.ndarray:
    """Draw color-coded region bounding boxes on a copy of the image."""
    annotated = image.copy()
    for reg in regions:
        try:
            bbox = reg["bbox"]
            xmin, ymin, xmax, ymax = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            reg_type = reg.get("region_type", "Text")
            fallback = reg.get("fallback_triggered", False)
            if fallback:
                color = (255, 140, 0)
            elif reg_type in ("Title", "Section-header"):
                color = (0, 200, 100)
            else:
                color = (0, 120, 255)
            cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), color, 2)
            label = f"#{reg['region_id']} [{reg_type}] {int(float(reg['confidence'])*100)}%"
            cv2.putText(annotated, label, (xmin, max(12, ymin - 4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
        except Exception:
            pass
    return annotated


def _log_stage_telemetry(stage_name: str, duration_sec: float, input_desc: str, output_desc: str):
    """Helper to log structured stage telemetry including RAM usage and object sizes."""
    rss_mb = _get_memory_mb()
    logger.info(
        f"[STAGE TELEMETRY] {stage_name} | Duration: {duration_sec:.3f}s | "
        f"RAM: {rss_mb} MB | In: {input_desc} | Out: {output_desc}"
    )


class OCRPipeline:
    """
    Production-ready Educational Document Understanding Pipeline.

    Architecture:
      1. CORE PIPELINE (Always executed to produce guaranteed baseline transcription):
         Phase 1: Ingestion & Rendering
         Phase 2: Orientation Correction & Preprocessing
         Phase 3: Layout Detection (Surya OCR)
         Phase 4: Primary OCR Recognition (Qwen VLM / Crop Fallback)
         Phase 5: Confidence Scoring & Region Fallback
         Phase 6: Baseline Layout & Final Transcription Assembly

      2. OPTIONAL ENHANCEMENT PIPELINE (Executed after baseline transcription exists):
         Phase 7: Educational Subject Detection
         Phase 8: Isolated Region Enhancements (Multi-Model Ensemble, VLM Verification, Edu-LM, Adaptation)
         Phase 9: Result Serialization & Export

    All optional enhancement modules run with explicit time budgets and fallback safety.
    """

    # Maximum time budget (seconds) allowed for optional enhancement modules per document
    MAX_ENHANCEMENT_BUDGET_SEC = 15.0

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.config.validate()

        logger.info(
            f"[PIPELINE] Initializing Educational Document Understanding Platform "
            f"(Device: {self.config.device})..."
        )

        # --- Baseline Core modules (always required) ---
        self.input_handler = InputHandler(self.config)
        self.orientation_corrector = OrientationCorrector(
            enable_perspective=self.config.enable_perspective_correction
        )
        self.preprocessor = ImagePreprocessor(self.config)
        self.document_analyzer = DocumentAnalyzer(self.config)
        self.layout_analyzer = SuryaLayoutAnalyzer(self.config)
        self.qwen_vlm = QwenVLMOCR(self.config)
        self.confidence_evaluator = ConfidenceEvaluator(self.config)
        self.reconstructor = LayoutReconstructor()
        self.text_corrector = TextCorrectionEngine()
        self.exporter = Exporter()

        # --- Optional enhancement modules ---
        self.crop_ocr = CropOCREngine()
        self.ensemble_ocr = MultiModelOCREnsemble(self.config)
        self.vlm_verifier = VisionLanguageVerifier(self.config)
        self.subject_detector = SubjectDetectionModule()
        self.educational_lm = EducationalLanguageModel()
        self.handwriting_adaptation = HandwritingAdaptationModule(self.config)

        logger.info("[PIPELINE] All modules initialized successfully.")

    def process_document(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        user_id: Optional[str] = None,
        subject_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an image or multi-page PDF end-to-end with strict Core vs Optional pipeline isolation.
        """
        out_dir = output_dir or self.config.output_dir
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        start_pipeline_time = time.time()
        active_user_id = user_id or self.config.default_user_id

        logger.info("═══════════════════════════════════════════════════════════")
        logger.info(f"[PIPELINE CORE] Starting document processing: '{base_name}' | User: '{active_user_id}'")

        # --- Phase 0: Load handwriting adaptation profile (Optional) ---
        user_profile: Dict[str, Any] = {}
        try:
            user_profile = self.handwriting_adaptation.get_profile(active_user_id)
            logger.info(f"[PIPELINE CORE] Phase 0: Handwriting profile loaded for '{active_user_id}'.")
        except Exception as e:
            logger.warning(f"[PIPELINE CORE] Phase 0: Handwriting profile load failed ({e}). Using empty profile.")

        with Timer(f"Document Processing ({base_name})", logger):

            # ──────────────────────────────────────────────────────────────────
            # Phase 1: Document Ingestion & Rendering (CORE)
            # ──────────────────────────────────────────────────────────────────
            phase_start = time.time()
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input document path does not exist: {input_path}")

            pages: List[DocumentPage] = self.input_handler.load_document(input_path)
            if not pages:
                raise ValueError(f"Document Ingestion produced no valid pages for file: {input_path}")

            ingestion_output = IngestionOutput(
                pages=pages,
                total_pages=len(pages),
                duration_sec=time.time() - phase_start
            )
            _log_stage_telemetry(
                stage_name="Phase 1: Ingestion & Rendering",
                duration_sec=ingestion_output.duration_sec,
                input_desc=f"path='{input_path}'",
                output_desc=f"{ingestion_output.total_pages} page(s)"
            )

            pages_metadata: List[Dict[str, Any]] = []
            all_plain_texts: List[str] = []
            all_md_texts: List[str] = []

            for page in pages:
                logger.info(f"[PIPELINE CORE] ─── Processing Page {page.page_number}/{page.total_pages} ───")
                page_start_time = time.time()

                # ──────────────────────────────────────────────────────────────
                # Phase 2: Orientation Correction & Preprocessing (CORE)
                # ──────────────────────────────────────────────────────────────
                phase_start = time.time()
                if page.image is None or page.image.size == 0:
                    raise ValueError(f"Invalid image array for page {page.page_number}")

                corrected_img, orient_meta = self.orientation_corrector.process(page.image)
                preprocessed_img, prep_meta = self.preprocessor.process(corrected_img)

                doc_class = "mixed_content"
                doc_analysis_meta: Dict[str, Any] = {}
                try:
                    doc_class, doc_analysis_meta = self.document_analyzer.analyze_page(preprocessed_img)
                    page.document_classification = doc_class
                except Exception as e:
                    logger.warning(f"[PIPELINE CORE] Phase 2b document analysis notice: {e}")
                    page.document_classification = doc_class

                prep_output = PreprocessingOutput(
                    corrected_image=corrected_img,
                    preprocessed_image=preprocessed_img,
                    orientation_meta=orient_meta,
                    preprocessing_meta=prep_meta,
                    document_classification=doc_class,
                    duration_sec=time.time() - phase_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 2: Orientation & Preprocessing (Page {page.page_number})",
                    duration_sec=prep_output.duration_sec,
                    input_desc=f"raw_shape={page.image.shape}",
                    output_desc=f"prep_shape={preprocessed_img.shape}, class='{doc_class}'"
                )

                debug_img_path: Optional[str] = None
                if self.config.save_debug_images:
                    try:
                        debug_img_path = os.path.join(
                            out_dir, "debug",
                            f"{base_name}_p{page.page_number}_preprocessed.png"
                        )
                        save_image(preprocessed_img, debug_img_path)
                    except Exception as e:
                        logger.warning(f"[PIPELINE CORE] Debug image save failed: {e}")

                # ──────────────────────────────────────────────────────────────
                # Phase 3: Layout Detection & Reading Order (CORE)
                # ──────────────────────────────────────────────────────────────
                phase_start = time.time()
                layout_regions, layout_meta = self.layout_analyzer.analyze(preprocessed_img)
                layout_output = LayoutOutput(
                    regions=layout_regions,
                    layout_meta=layout_meta,
                    duration_sec=time.time() - phase_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 3: Surya Layout Analysis (Page {page.page_number})",
                    duration_sec=layout_output.duration_sec,
                    input_desc=f"image={preprocessed_img.shape}",
                    output_desc=f"{len(layout_regions)} region(s) detected"
                )

                # ──────────────────────────────────────────────────────────────
                # Phase 4: Primary OCR Recognition (CORE)
                # ──────────────────────────────────────────────────────────────
                phase_start = time.time()
                qwen_md, vlm_regions, vlm_meta = self.qwen_vlm.transcribe_page(
                    image=preprocessed_img,
                    layout_regions=layout_regions
                )
                primary_ocr_output = PrimaryOCROutput(
                    full_markdown=qwen_md,
                    regions=vlm_regions,
                    vlm_meta=vlm_meta,
                    duration_sec=time.time() - phase_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 4: Primary OCR Recognition (Page {page.page_number})",
                    duration_sec=primary_ocr_output.duration_sec,
                    input_desc=f"regions={len(layout_regions)}",
                    output_desc=f"md_len={len(qwen_md)} chars, model='{vlm_meta.get('model')}'"
                )

                # ──────────────────────────────────────────────────────────────
                # Phase 5: Confidence Scoring & Region Fallback Recovery (CORE)
                # ──────────────────────────────────────────────────────────────
                phase_start = time.time()
                final_regions, conf_stats = self.confidence_evaluator.evaluate_and_recover(
                    image=preprocessed_img,
                    regions=vlm_regions
                )
                confidence_output = ConfidenceOutput(
                    final_regions=final_regions,
                    conf_stats=conf_stats,
                    duration_sec=time.time() - phase_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 5: Confidence Scoring & Fallback (Page {page.page_number})",
                    duration_sec=confidence_output.duration_sec,
                    input_desc=f"vlm_regions={len(vlm_regions)}",
                    output_desc=f"final_regions={len(final_regions)}, high_conf={conf_stats.get('high_confidence_count', 0)}"
                )

                # ──────────────────────────────────────────────────────────────
                # Phase 6: Baseline Layout & Final Transcription Assembly (CORE)
                # GUARANTEED SUCCESS: Baseline transcription is assembled immediately
                # ──────────────────────────────────────────────────────────────
                phase_start = time.time()
                baseline_page_transcription = self.reconstructor.reconstruct(final_regions)
                page_md = qwen_md.strip() if qwen_md.strip() else baseline_page_transcription["markdown"]
                page_plain = baseline_page_transcription["plain_text"] or qwen_md
                
                transcription_output = TranscriptionOutput(
                    plain_text=page_plain,
                    markdown=page_md,
                    duration_sec=time.time() - phase_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 6: Baseline Final Transcription (Page {page.page_number})",
                    duration_sec=transcription_output.duration_sec,
                    input_desc=f"regions={len(final_regions)}",
                    output_desc=f"plain_len={len(page_plain)} chars, md_len={len(page_md)} chars"
                )

                # ──────────────────────────────────────────────────────────────
                # Phase 7 & 8: OPTIONAL ENHANCEMENT PIPELINE
                # Runs ONLY after baseline transcription is securely generated.
                # Enforces a total time budget limit to prevent timeouts.
                # ──────────────────────────────────────────────────────────────
                enhancement_start = time.time()
                subject_info: Dict[str, Any] = {
                    "subject": "General",
                    "display_name": "General",
                    "confidence": 0.5,
                    "keywords": [],
                    "sample_patterns": []
                }

                ensemble_telemetry: List[Dict[str, Any]] = []
                vlm_verification_telemetry: List[Dict[str, Any]] = []
                struct_counts: Dict[str, int] = {}

                try:
                    # Phase 7: Subject Detection
                    raw_page_text = " ".join([r.text for r in final_regions if r.text]) or qwen_md
                    if subject_override and subject_override != "Auto":
                        subject_info = {
                            "subject": subject_override,
                            "display_name": f"{subject_override} (User Override)",
                            "confidence": 1.0,
                            "keywords": [],
                            "sample_patterns": []
                        }
                    elif self.config.enable_subject_detection:
                        subject_info = self.subject_detector.detect_subject(
                            text=raw_page_text,
                            document_title=base_name
                        )
                except Exception as e:
                    logger.warning(f"[PIPELINE ENHANCEMENT] Phase 7 Subject Detection notice: {e}")

                page.detected_subject = subject_info.get("subject", "General")
                page.subject_confidence = float(subject_info.get("confidence", 0.5))
                page.subject_keywords = list(subject_info.get("keywords", []))

                # Phase 8: Per-Region Optional Enhancements (with budget guard)
                run_ensemble = self.config.enable_multi_model_ensemble
                run_vlm_verifier = self.config.enable_vlm_verification

                for reg in final_regions:
                    # Budget Check: If optional enhancements exceed budget, exit loop early
                    if (time.time() - enhancement_start) > self.MAX_ENHANCEMENT_BUDGET_SEC:
                        logger.warning(
                            f"[PIPELINE ENHANCEMENT] Time budget exceeded ({self.MAX_ENHANCEMENT_BUDGET_SEC}s). "
                            f"Skipping remaining optional region enhancements."
                        )
                        break

                    xmin, ymin, xmax, ymax = (
                        int(reg.bbox[0]), int(reg.bbox[1]),
                        int(reg.bbox[2]), int(reg.bbox[3])
                    )
                    crop_img = preprocessed_img[ymin:ymax, xmin:xmax]

                    if crop_img.size > 0:
                        # ── Optional Enhancement 1: Multi-Model Ensemble ──
                        if run_ensemble:
                            try:
                                ens_res = self.ensemble_ocr.recognize_region_ensemble(
                                    crop=crop_img,
                                    full_image=preprocessed_img,
                                    bbox=reg.bbox,
                                    subject_keywords=page.subject_keywords,
                                    adaptation_boosts=user_profile.get("custom_vocabulary", {})
                                )
                                if ens_res.get("selected_text", "").strip():
                                    reg.text = ens_res["selected_text"]
                                    reg.confidence = float(
                                        max(float(reg.confidence), float(ens_res.get("confidence", 0.0)))
                                    )
                                    reg.ensemble_candidates = [
                                        {
                                            "model": str(c.get("model", "")),
                                            "text": str(c.get("text", "")),
                                            "confidence": float(c.get("confidence", 0.0)),
                                            "aggregated_score": float(c.get("aggregated_score", 0.0))
                                        }
                                        for c in ens_res.get("candidates", [])
                                    ]
                                    reg.fallback_model = str(ens_res.get("selected_model", "ensemble"))
                            except Exception as e:
                                logger.warning(f"[ENSEMBLE FALLBACK] Region #{reg.region_id}: {e}")

                        # ── Optional Enhancement 2: Vision-Language Verification ──
                        if run_vlm_verifier:
                            try:
                                v_res = self.vlm_verifier.verify_transcription(
                                    image_crop=crop_img,
                                    candidate_text=reg.text,
                                    subject=page.detected_subject
                                )
                                if v_res.get("verified_text", "").strip():
                                    reg.vlm_verified_text = str(v_res["verified_text"])
                                    reg.text = str(v_res["verified_text"])
                                    reg.verification_changes = [
                                        {"original": str(c.get("original", "")),
                                         "verified": str(c.get("verified", ""))}
                                        for c in v_res.get("changes_made", [])
                                    ]
                                    vlm_verification_telemetry.append({
                                        "region_id": int(reg.region_id),
                                        "original_candidate": str(reg.text),
                                        "verified_text": str(v_res["verified_text"]),
                                        "changes": len(reg.verification_changes)
                                    })
                            except Exception as e:
                                logger.warning(f"[VLM FALLBACK] Region #{reg.region_id}: {e}")

                    # ── Optional Enhancement 3: Educational Language Model ──
                    struct_tag = "Text"
                    lm_boost = 0.0
                    try:
                        recon_text, struct_tag, lm_boost = self.educational_lm.reconstruct_structural_text(
                            text=reg.text,
                            subject=page.detected_subject,
                            candidates=reg.candidates
                        )
                        reg.text = recon_text
                        reg.structural_tag = struct_tag
                    except Exception as e:
                        logger.warning(f"[EDU-LM FALLBACK] Region #{reg.region_id}: {e}")
                        reg.structural_tag = "Text"

                    struct_counts[struct_tag] = struct_counts.get(struct_tag, 0) + 1

                    # ── Optional Enhancement 4: Handwriting Adaptation Boost ──
                    adapt_boost = 0.0
                    try:
                        adapt_boost = float(
                            self.handwriting_adaptation.calculate_candidate_adaptation_boost(
                                user_id=active_user_id,
                                candidate_text=reg.text
                            )
                        )
                        reg.adaptation_score_boost = adapt_boost
                        reg.confidence = float(
                            min(0.99, float(reg.confidence) + adapt_boost + (0.05 if lm_boost > 0 else 0.0))
                        )
                    except Exception as e:
                        logger.warning(f"[ADAPT FALLBACK] Region #{reg.region_id}: {e}")
                        reg.confidence = float(reg.confidence)

                    ensemble_telemetry.append({
                        "region_id": int(reg.region_id),
                        "selected_model": str(getattr(reg, "fallback_model", "standard") or "standard"),
                        "structural_tag": str(reg.structural_tag),
                        "candidates_aggregated": int(len(getattr(reg, "ensemble_candidates", []))),
                        "adaptation_boost": round(float(adapt_boost), 4),
                        "final_confidence": round(float(reg.confidence), 4)
                    })

                page.educational_structures = struct_counts
                enhancement_output = EnhancementOutput(
                    detected_subject=subject_info,
                    enhanced_regions=final_regions,
                    ensemble_telemetry=ensemble_telemetry,
                    vlm_verification_telemetry=vlm_verification_telemetry,
                    educational_structures=struct_counts,
                    duration_sec=time.time() - enhancement_start
                )
                _log_stage_telemetry(
                    stage_name=f"Phase 7 & 8: Optional Enhancements (Page {page.page_number})",
                    duration_sec=enhancement_output.duration_sec,
                    input_desc=f"regions={len(final_regions)}",
                    output_desc=f"subject='{subject_info.get('subject')}'"
                )

                # Re-merge text into page_plain & page_md if enhancements modified reg.text
                try:
                    enhanced_transcription = self.reconstructor.reconstruct(final_regions)
                    if enhanced_transcription.get("plain_text", "").strip():
                        page_plain = enhanced_transcription["plain_text"]
                    if enhanced_transcription.get("markdown", "").strip():
                        page_md = qwen_md if qwen_md.strip() else enhanced_transcription["markdown"]
                except Exception as e:
                    logger.warning(f"[PIPELINE ENHANCEMENT] Text re-merge notice: {e}")

                # Optional Contextual Proofreading
                if self.config.enable_contextual_proofreading:
                    try:
                        corr_res = self.text_corrector.analyze_text(page_plain)
                        if corr_res.corrected_text.strip():
                            page_plain = corr_res.corrected_text
                    except Exception as e:
                        logger.warning(f"[PIPELINE ENHANCEMENT] Contextual proofreading notice: {e}")

                all_plain_texts.append(page_plain)
                all_md_texts.append(
                    f"# Page {page.page_number} [{page.detected_subject}]\n\n" + page_md
                )

                page_elapsed = time.time() - page_start_time

                # ──────────────────────────────────────────────────────────────
                # Region Serialisation & Optimized Base64 Payload
                # ──────────────────────────────────────────────────────────────
                region_dicts: List[Dict[str, Any]] = []
                for r in final_regions:
                    region_dicts.append({
                        "region_id": int(r.region_id),
                        "paragraph_id": int(r.paragraph_id) if r.paragraph_id is not None else None,
                        "reading_order_idx": int(r.reading_order_idx),
                        "region_type": str(r.region_type),
                        "structural_tag": str(getattr(r, "structural_tag", "Text")),
                        "bbox": [int(v) for v in r.bbox],
                        "unpadded_bbox": (
                            [int(v) for v in r.unpadded_bbox]
                            if r.unpadded_bbox else [int(v) for v in r.bbox]
                        ),
                        "text": str(r.text),
                        "vlm_verified_text": str(getattr(r, "vlm_verified_text", "")),
                        "verification_changes": [
                            {"original": str(c.get("original", "")),
                             "verified": str(c.get("verified", ""))}
                            for c in getattr(r, "verification_changes", [])
                        ],
                        "confidence": round(float(r.confidence), 4),
                        "adaptation_boost": round(float(getattr(r, "adaptation_score_boost", 0.0)), 4),
                        "ensemble_candidates": [
                            {
                                "model": str(c.get("model", "")),
                                "text": str(c.get("text", "")),
                                "confidence": float(c.get("confidence", 0.0)),
                                "aggregated_score": float(c.get("aggregated_score", 0.0))
                            }
                            for c in getattr(r, "ensemble_candidates", [])
                        ],
                        "fallback_triggered": bool(r.fallback_triggered),
                        "fallback_model": str(r.fallback_model) if r.fallback_model else None
                    })

                # Compact JPEG Base64 encoding (downscaled to max 1280px dimension)
                original_b64 = _img_to_base64(page.image, max_dim=1280)
                preprocessed_b64 = _img_to_base64(preprocessed_img, max_dim=1280)
                annotated_b64 = _img_to_base64(_draw_bounding_boxes(preprocessed_img, region_dicts), max_dim=1280)

                safe_conf_stats: Dict[str, Any] = {}
                for k, v in conf_stats.items():
                    if isinstance(v, (np.integer,)):
                        safe_conf_stats[k] = int(v)
                    elif isinstance(v, (np.floating,)):
                        safe_conf_stats[k] = float(v)
                    elif isinstance(v, np.ndarray):
                        safe_conf_stats[k] = v.tolist()
                    else:
                        safe_conf_stats[k] = v

                pages_metadata.append({
                    "page_number": int(page.page_number),
                    "resolution": f"{page.width}x{page.height}",
                    "document_classification": str(getattr(page, "document_classification", "mixed_content")),
                    "detected_subject": subject_info,
                    "educational_structures": {str(k): int(v) for k, v in struct_counts.items()},
                    "document_analysis": doc_analysis_meta,
                    "orientation": orient_meta,
                    "preprocessing": prep_meta,
                    "layout_analysis": layout_meta,
                    "vlm_meta": vlm_meta,
                    "confidence_stats": safe_conf_stats,
                    "ensemble_telemetry": ensemble_telemetry,
                    "vlm_verification_telemetry": vlm_verification_telemetry,
                    "processing_duration_sec": round(float(page_elapsed), 3),
                    "debug_image": debug_img_path,
                    "regions": region_dicts,
                    "transcription": {
                        "plain_text": str(page_plain),
                        "markdown": str(page_md)
                    },
                    "original_image_base64": original_b64,
                    "preprocessed_image_base64": preprocessed_b64,
                    "annotated_image_base64": annotated_b64,
                })

                logger.info(
                    f"[PIPELINE CORE] Page {page.page_number} fully processed in {page_elapsed:.3f}s | "
                    f"RAM: {_get_memory_mb()} MB"
                )

            # ──────────────────────────────────────────────────────────────────
            # Combined Final Transcription Payload
            # ──────────────────────────────────────────────────────────────────
            final_plain = "\n\n=== PAGE BREAK ===\n\n".join(all_plain_texts)
            final_md = "\n\n---\n\n".join(all_md_texts)
            transcription_payload = {
                "plain_text": final_plain,
                "markdown": final_md
            }

            # ──────────────────────────────────────────────────────────────────
            # Phase 9: Export Results
            # ──────────────────────────────────────────────────────────────────
            phase_start = time.time()
            export_paths: Dict[str, str] = {}
            try:
                export_paths = self.exporter.export_all(
                    output_dir=out_dir,
                    base_name=base_name,
                    transcription=transcription_payload,
                    pages_metadata=pages_metadata
                )
            except Exception as e:
                logger.warning(f"[PIPELINE CORE] Phase 9 Export notice: {e}")

            total_elapsed = time.time() - start_pipeline_time

            logger.info(
                f"[PIPELINE CORE] ═══ Processing complete: '{base_name}' | "
                f"{len(pages)} page(s) | {total_elapsed:.3f}s total | RAM: {_get_memory_mb()} MB ═══"
            )

            return {
                "status": "success",
                "document_name": str(base_name),
                "user_id": str(active_user_id),
                "total_pages": int(len(pages)),
                "detected_subject": (
                    pages_metadata[0]["detected_subject"] if pages_metadata else "General"
                ),
                "handwriting_profile_version": str(user_profile.get("version", "1.0.0")),
                "total_processing_duration_sec": round(float(total_elapsed), 3),
                "export_paths": export_paths,
                "transcription": transcription_payload,
                "pages": pages_metadata
            }
