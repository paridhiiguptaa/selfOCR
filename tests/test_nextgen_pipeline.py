import pytest
import os
import cv2
import numpy as np
from src.ocr_pipeline.pipeline import OCRPipeline
from src.ocr_pipeline.config import PipelineConfig

def test_nextgen_pipeline_end_to_end(tmp_path):
    out_dir = os.path.join(tmp_path, "output")
    cfg = PipelineConfig(
        output_dir=out_dir,
        user_profile_dir=os.path.join(tmp_path, "profiles"),
        save_debug_images=False
    )
    pipeline = OCRPipeline(cfg)

    # Create dummy synthetic document image with text header
    img = np.zeros((300, 600, 3), dtype=np.uint8) + 245
    cv2.putText(img, "Properties of Matter", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (10, 10, 10), 2)
    cv2.putText(img, "Everything around us is made of matter.", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10, 10, 10), 2)

    img_path = os.path.join(tmp_path, "test_doc.png")
    cv2.imwrite(img_path, img)

    res = pipeline.process_document(
        input_path=img_path,
        user_id="student_benchmark_1",
        subject_override="Science"
    )

    assert res["status"] == "success"
    assert res["user_id"] == "student_benchmark_1"
    assert res["detected_subject"]["subject"] == "Science"
    assert len(res["pages"]) == 1

    page_meta = res["pages"][0]
    assert "detected_subject" in page_meta
    assert "educational_structures" in page_meta
    assert "ensemble_telemetry" in page_meta

