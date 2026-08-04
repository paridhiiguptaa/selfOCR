import pytest
import numpy as np
from src.ocr_pipeline.modules.multi_scale_ocr import MultiScaleImageGenerator, CandidateFusionModule

def test_multi_scale_image_generator():
    generator = MultiScaleImageGenerator()
    dummy_crop = np.zeros((40, 200, 3), dtype=np.uint8) + 200

    scales = generator.generate_scales(dummy_crop)
    assert len(scales) >= 5
    scale_names = [s["scale_name"] for s in scales]
    assert "original" in scale_names
    assert "clahe_contrast" in scale_names
    assert "unsharp_sharpened" in scale_names
    assert "lanczos_super_res" in scale_names
    assert "adaptive_threshold" in scale_names

def test_candidate_fusion_module():
    fusion = CandidateFusionModule()
    candidates = [
        {"scale": "original", "text": "Propeties of Matier", "confidence": 0.70},
        {"scale": "clahe_contrast", "text": "Properties of Matter", "confidence": 0.88},
        {"scale": "adaptive_threshold", "text": "Prop er ties of Mat ter", "confidence": 0.60}
    ]

    subject_kws = ["matter", "properties", "states", "solid", "liquid"]
    res = fusion.evaluate_and_fuse(candidates, subject_keywords=subject_kws)

    assert res["selected_text"] == "Properties of Matter"
    assert res["selected_scale"] == "clahe_contrast"
    assert res["fused_confidence"] > 0.70
    assert len(res["ranked_candidates"]) == 3
