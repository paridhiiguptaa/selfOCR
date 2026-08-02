import pytest
from src.ocr_pipeline.modules.text_corrector import TextCorrectionEngine

def test_contextual_homophone_corrections():
    engine = TextCorrectionEngine()

    test_cases = [
        ("The boy road his bicycle to school.", "The boy rode his bicycle to school."),
        ("She red the book yesterday afternoon.", "She read the book yesterday afternoon."),
        ("I sea the blue sky and rainbow.", "I see the blue sky and rainbow."),
        ("Their are seven colors in the rainbow.", "There are seven colors in the rainbow."),
        ("The son is shining brightly.", "The sun is shining brightly."),
        ("I cat the paper with scissors.", "I cut the paper with scissors."),
    ]

    for raw, expected in test_cases:
        result = engine.analyze_text(raw)
        assert result.corrected_text == expected, f"Failed on '{raw}': got '{result.corrected_text}', expected '{expected}'"
        assert len(result.suggestions) > 0
        assert any(s.category in ("Contextual Substitution", "Grammar Correction") for s in result.suggestions)

def test_multi_word_handwriting_reconstruction():
    engine = TextCorrectionEngine()
    sample = "The yellov sun is peepina through clouds."
    result = engine.analyze_text(sample)

    assert result.corrected_text == "The yellow sun is peeping through clouds."
    categories = [s.category for s in result.suggestions]
    assert "Character Confusion" in categories or "Contextual Substitution" in categories

def test_ocr_candidate_evaluation():
    engine = TextCorrectionEngine()
    sample = "The cat sat on the mat."
    candidates = [
        {
            "original": "cat",
            "start_offset": 4,
            "end_offset": 7,
            "candidates": [
                {"text": "car", "confidence": 0.92},
                {"text": "cat", "confidence": 0.70}
            ]
        }
    ]

    result = engine.analyze_text(sample, ocr_candidates=candidates)
    assert len(result.suggestions) > 0
    assert any(s.proposed_correction == "car" for s in result.suggestions)
