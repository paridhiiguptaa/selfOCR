import pytest
import numpy as np
from src.ocr_pipeline.modules.document_analyzer import DocumentAnalyzer
from src.ocr_pipeline.modules.quality_estimator import QualityEstimator
from src.ocr_pipeline.modules.handwriting_ocr_engine import HandwritingOCREngine
from src.ocr_pipeline.evaluation.full_pipeline_evaluator import FullPipelineEvaluator
from src.ocr_pipeline.models import TextRegion

def test_document_analyzer_classification():
    analyzer = DocumentAnalyzer()
    dummy_printed = np.ones((200, 400, 3), dtype=np.uint8) * 255
    classification, meta = analyzer.analyze_page(dummy_printed)
    assert classification in ("predominantly_printed", "predominantly_handwritten", "mixed_content")
    assert "handwritten_ink_ratio" in meta

def test_quality_estimator_calibration():
    estimator = QualityEstimator()
    region = TextRegion(region_id=1, bbox=(0, 0, 100, 20), text="The sky is blue.", confidence=0.85, ink_density=0.10)
    q_score, indicators = estimator.evaluate_region_quality(region)
    assert 0.0 <= q_score <= 1.0
    assert indicators["raw_confidence"] == 0.85
    assert indicators["is_uncalibrated_gibberish"] == 0.0

def test_quality_estimator_gibberish_flagging():
    estimator = QualityEstimator()
    gibberish_region = TextRegion(region_id=2, bbox=(0, 0, 100, 20), text="||||||| zzzzz", confidence=0.90, ink_density=0.08)
    q_score, indicators = estimator.evaluate_region_quality(gibberish_region)
    assert indicators["is_uncalibrated_gibberish"] == 1.0

def test_handwriting_ocr_engine_creation():
    hw_engine = HandwritingOCREngine()
    dummy_crop = np.ones((40, 200, 3), dtype=np.uint8) * 255
    text, conf = hw_engine.recognize_handwriting_crop(dummy_crop)
    assert isinstance(text, str)
    assert isinstance(conf, float)

def test_full_pipeline_evaluator_benchmark():
    evaluator = FullPipelineEvaluator()
    res = evaluator.evaluate_test_cases()
    summary = res["summary"]
    assert summary["total_test_cases"] > 0
    assert summary["mean_cer"] >= 0.0
    assert summary["mean_wer"] >= 0.0
    assert summary["sentence_accuracy"] >= 0.0
