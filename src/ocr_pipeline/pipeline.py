import os
import cv2
import time
import numpy as np
from typing import Dict, Any, List, Optional

from .config import PipelineConfig, default_config
from .models import DocumentPage, TextRegion
from .utils.logging_config import logger, Timer
from .utils.image_utils import save_image
from .modules.input_handler import InputHandler
from .modules.orientation_corrector import OrientationCorrector
from .modules.image_preprocessor import ImagePreprocessor
from .modules.surya_layout_analyzer import SuryaLayoutAnalyzer
from .modules.qwen_vlm_ocr import QwenVLMOCR
from .modules.confidence_evaluator import ConfidenceEvaluator
from .modules.layout_reconstructor import LayoutReconstructor
from .modules.exporter import Exporter

class OCRPipeline:
    """
    Production-ready VLM-First OCR pipeline using Qwen2.5-VL primary OCR engine,
    Surya OCR layout analysis, GOT-OCR 2.0 confidence fallback, and adaptive image preprocessing.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.config.validate()

        logger.info(f"Initializing VLM OCR Pipeline (Device: {self.config.device})...")

        # Initialize pipeline modules
        self.input_handler = InputHandler(self.config)
        self.orientation_corrector = OrientationCorrector(enable_perspective=self.config.enable_perspective_correction)
        self.preprocessor = ImagePreprocessor(self.config)
        self.layout_analyzer = SuryaLayoutAnalyzer(self.config)
        self.qwen_vlm = QwenVLMOCR(self.config)
        self.confidence_evaluator = ConfidenceEvaluator(self.config)
        self.reconstructor = LayoutReconstructor()
        self.exporter = Exporter()

    def process_document(self, input_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an image or multi-page PDF document end-to-end through the VLM pipeline.
        Returns a structured dictionary containing transcriptions, page metadata, confidence scores, and export paths.
        """
        out_dir = output_dir or self.config.output_dir
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        start_pipeline_time = time.time()

        with Timer(f"VLM Pipeline Processing ({base_name})", logger):
            # Phase 1: Ingestion & Rendering
            pages: List[DocumentPage] = self.input_handler.load_document(input_path)
            
            pages_metadata: List[Dict[str, Any]] = []
            all_plain_texts: List[str] = []
            all_md_texts: List[str] = []

            for page in pages:
                logger.info(f"--- Processing Page {page.page_number}/{page.total_pages} ---")
                page_start_time = time.time()

                # Phase 2: Orientation Correction & Preprocessing
                corrected_img, orient_meta = self.orientation_corrector.process(page.image)
                preprocessed_img, prep_meta = self.preprocessor.process(corrected_img)

                # Save debug images if configured
                debug_img_path = None
                if self.config.save_debug_images:
                    debug_img_path = os.path.join(out_dir, "debug", f"{base_name}_p{page.page_number}_preprocessed.png")
                    save_image(preprocessed_img, debug_img_path)

                # Phase 3: Layout Analysis (Surya OCR)
                layout_regions, layout_meta = self.layout_analyzer.analyze(preprocessed_img)

                # Phase 4: Primary VLM OCR (Qwen2.5-VL)
                qwen_md, vlm_regions, vlm_meta = self.qwen_vlm.transcribe_page(
                    image=preprocessed_img,
                    layout_regions=layout_regions
                )

                # Phase 5: Confidence Scoring & GOT-OCR 2.0 Fallback Recovery
                final_regions, conf_stats = self.confidence_evaluator.evaluate_and_recover(
                    image=preprocessed_img,
                    regions=vlm_regions
                )

                # Phase 6: Document Structure Reconstruction
                page_transcription = self.reconstructor.reconstruct(final_regions)
                
                # Use Qwen page level markdown if available, otherwise reconstruct
                page_md = qwen_md if qwen_md.strip() else page_transcription["markdown"]
                page_plain = page_transcription["plain_text"] or qwen_md

                all_plain_texts.append(page_plain)
                all_md_texts.append(f"# Page {page.page_number}\n\n" + page_md)

                page_elapsed = time.time() - page_start_time

                # Region dictionary serialization
                region_dicts = []
                for r in final_regions:
                    region_dicts.append({
                        "region_id": r.region_id,
                        "reading_order_idx": r.reading_order_idx,
                        "region_type": r.region_type,
                        "bbox": list(r.bbox),
                        "text": r.text,
                        "confidence": round(r.confidence, 4),
                        "fallback_triggered": r.fallback_triggered,
                        "fallback_model": r.fallback_model
                    })

                pages_metadata.append({
                    "page_number": page.page_number,
                    "resolution": f"{page.width}x{page.height}",
                    "orientation": orient_meta,
                    "preprocessing": prep_meta,
                    "layout_analysis": layout_meta,
                    "vlm_meta": vlm_meta,
                    "confidence_stats": conf_stats,
                    "processing_duration_sec": round(page_elapsed, 3),
                    "debug_image": debug_img_path,
                    "regions": region_dicts,
                    "transcription": {
                        "plain_text": page_plain,
                        "markdown": page_md
                    }
                })

            # Combined Multi-page Final Transcription
            final_plain = "\n\n=== PAGE BREAK ===\n\n".join(all_plain_texts)
            final_md = "\n\n---\n\n".join(all_md_texts)

            transcription_payload = {
                "plain_text": final_plain,
                "markdown": final_md
            }

            # Phase 7: Export Results
            export_paths = self.exporter.export_all(
                output_dir=out_dir,
                base_name=base_name,
                transcription=transcription_payload,
                pages_metadata=pages_metadata
            )

            total_elapsed = time.time() - start_pipeline_time

            return {
                "status": "success",
                "document_name": base_name,
                "total_pages": len(pages),
                "total_processing_duration_sec": round(total_elapsed, 3),
                "export_paths": export_paths,
                "transcription": transcription_payload,
                "pages": pages_metadata
            }
