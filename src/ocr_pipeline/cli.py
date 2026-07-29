import os
import sys
import argparse
from typing import Optional

from .config import PipelineConfig
from .pipeline import OCRPipeline
from .utils.logging_config import logger

def main():
    parser = argparse.ArgumentParser(
        description="Run VLM-First OCR Pipeline (Qwen2.5-VL + Surya OCR + GOT-OCR 2.0 Fallback) on images or PDFs."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input image file or PDF document.")
    parser.add_argument("--output", "-o", default="output", help="Directory where results will be saved.")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for rendering PDF pages.")
    parser.add_argument("--min-confidence", type=float, default=0.75, help="Confidence threshold to trigger GOT-OCR 2.0 fallback.")
    parser.add_argument("--no-orientation", action="store_true", help="Disable orientation detection and rotation.")
    parser.add_argument("--no-deskew", action="store_true", help="Disable fine deskewing.")
    parser.add_argument("--no-perspective", action="store_true", help="Disable perspective correction.")
    parser.add_argument("--no-fallback", action="store_true", help="Disable GOT-OCR 2.0 fallback.")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    config = PipelineConfig(
        pdf_render_dpi=args.dpi,
        min_confidence_threshold=args.min_confidence,
        enable_orientation_correction=not args.no_orientation,
        enable_deskew=not args.no_deskew,
        enable_perspective_correction=not args.no_perspective,
        enable_got_fallback=not args.no_fallback,
        output_dir=args.output,
        save_debug_images=True
    )

    logger.info(f"Starting VLM OCR Pipeline execution for: {args.input}")
    ocr_pipeline = OCRPipeline(config)
    
    try:
        results = ocr_pipeline.process_document(args.input, output_dir=args.output)
        print("\n" + "="*60)
        print(f"OCR Pipeline Processing Complete: {results['document_name']}")
        print(f"Total Pages: {results['total_pages']}")
        print(f"Processing Time: {results['total_processing_duration_sec']} seconds")
        print("="*60)
        print("\n--- TRANSCRIPTION MARKDOWN PREVIEW ---\n")
        print(results["transcription"]["markdown"][:1000])
        print("\n" + "="*60)
        print("Exported Files:")
        for fmt, path in results["export_paths"].items():
            print(f"  - {fmt.upper()}: {path}")
        print("="*60 + "\n")
    except Exception as e:
        logger.error(f"OCR processing failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
