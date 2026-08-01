import pytest
from src.ocr_pipeline.evaluation.flashcard_evaluator import FlashcardEvaluator
from src.ocr_pipeline.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES
from src.ocr_pipeline.modules.learning_opportunity_detector import LearningOpportunityDetector

def test_learning_opportunity_detector():
    detector = LearningOpportunityDetector()
    sample_suggestions = [
        {
            "suggestion_id": "sug_1",
            "original_text": "road",
            "proposed_correction": "rode",
            "category": "Contextual Substitution",
            "explanation": "Use 'rode' for bicycle context"
        },
        {
            "suggestion_id": "sug_2",
            "original_text": "skv",
            "proposed_correction": "sky",
            "category": "Character Confusion",
            "explanation": "Correct 'skv' to 'sky'"
        },
        {
            "suggestion_id": "sug_3",
            "original_text": "dont",
            "proposed_correction": "don't",
            "category": "Punctuation Correction",
            "explanation": "Add apostrophe"
        }
    ]

    opps = detector.align_and_detect(
        exported_text="The boy rode the bicycle. The sky is blue. Don't worry.",
        accepted_suggestions=sample_suggestions
    )

    assert len(opps) == 3
    styles = {o["card_style"] for o in opps}
    assert "vocabulary" in styles
    assert "spelling" in styles
    assert "punctuation_practice" in styles

def test_flashcard_evaluation_benchmark():
    evaluator = FlashcardEvaluator()
    report = evaluator.evaluate_flashcard_generation(BENCHMARK_TEST_CASES)

    summary = report["summary"]
    assert summary["total_test_cases"] == len(BENCHMARK_TEST_CASES)
    assert summary["total_accepted_corrections"] > 0
    assert summary["total_flashcards_created"] > 0
    assert summary["conversion_rate"] >= 0.70

    for case in report["cases"]:
        assert "test_id" in case
        assert "cards_created" in case
        assert case["cards_created"] >= 0
