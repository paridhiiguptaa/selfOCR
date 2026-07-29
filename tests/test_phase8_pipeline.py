import os
import cv2
import numpy as np
from PIL import Image
from src.ocr_pipeline.config import PipelineConfig
from src.ocr_pipeline.pipeline import OCRPipeline

def test_full_vlm_ocr_pipeline(tmp_path):
    # Create synthetic test image
    img_path = os.path.join(str(tmp_path), "test_doc.png")
    img = np.full((400, 500, 3), 255, dtype=np.uint8)
    cv2.putText(img, "TEST OCR DOCUMENT", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    cv2.putText(img, "Handwritten Note: Math solution = 42", (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.imwrite(img_path, img)

    out_dir = os.path.join(str(tmp_path), "output")
    config = PipelineConfig(output_dir=out_dir, save_debug_images=True)
    pipeline = OCRPipeline(config)

    res = pipeline.process_document(img_path, output_dir=out_dir)

    assert res["status"] == "success"
    assert res["total_pages"] == 1
    assert "transcription" in res
    assert "plain_text" in res["transcription"]
    assert "markdown" in res["transcription"]
    assert os.path.exists(res["export_paths"]["txt"])
    assert os.path.exists(res["export_paths"]["markdown"])
    assert os.path.exists(res["export_paths"]["json"])
