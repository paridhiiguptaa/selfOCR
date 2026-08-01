import pytest
from src.ocr_pipeline.modules.text_recovery_layer import TextRecoveryLayer
from src.ocr_pipeline.modules.text_corrector import TextCorrectionEngine
from src.ocr_pipeline.evaluation.handwriting_resilience_evaluator import HandwritingResilienceEvaluator

def test_text_recovery_layer_hyphen_and_spacing():
    layer = TextRecoveryLayer()
    raw_ocr = "The student wrote a hand-\nwritten story.The sky is blue."
    recovered, meta = layer.recover_text(raw_ocr)

    assert "handwritten" in recovered
    assert "story. The sky" in recovered
    assert meta["repaired_hyphens"] >= 1
    assert meta["spacing_fixes"] >= 1

def test_text_recovery_layer_punctuation_collapse():
    layer = TextRecoveryLayer()
    raw_ocr = "Is it blue?? Yes.. it is!"
    recovered, meta = layer.recover_text(raw_ocr)

    assert "blue?" in recovered
    assert "Yes. it" in recovered

def test_handwriting_resilience_evaluation_benchmark():
    evaluator = HandwritingResilienceEvaluator()
    res = evaluator.evaluate_resilience()

    summary = res["summary"]
    assert summary["total_test_cases"] > 0
    assert summary["recovery_success_rate"] >= 0.80
    assert summary["deck_generation_rate"] == 1.0

    for case in res["cases"]:
        assert "test_id" in case
        assert "corrected_text" in case
        assert case["flashcards_count"] >= 0
