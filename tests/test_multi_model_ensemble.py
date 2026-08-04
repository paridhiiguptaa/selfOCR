import pytest
import numpy as np
from src.ocr_pipeline.modules.multi_model_ocr_ensemble import CandidateAggregationLayer, MultiModelOCREnsemble

def test_candidate_aggregation_layer():
    aggregator = CandidateAggregationLayer()
    candidates = [
        {"model": "easyocr", "text": "Propeties of Matier", "confidence": 0.70},
        {"model": "trocr_handwritten", "text": "Properties of Matter", "confidence": 0.88},
        {"model": "crop_ocr_standard", "text": "Prop er ties of Mat ter", "confidence": 0.60}
    ]

    res = aggregator.aggregate_candidates(candidates, subject_keywords=["matter", "properties"])
    assert res["selected_text"] == "Properties of Matter"
    assert res["selected_model"] == "trocr_handwritten"
    assert res["aggregated_confidence"] > 0.75
    assert len(res["ranked_candidates"]) == 3

def test_multi_model_ocr_ensemble():
    ensemble = MultiModelOCREnsemble()
    crop = np.zeros((40, 200, 3), dtype=np.uint8) + 220
    res = ensemble.recognize_region_ensemble(crop)

    assert "selected_text" in res
    assert "confidence" in res
    assert "candidates" in res
