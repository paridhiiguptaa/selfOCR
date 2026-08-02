import pytest
from src.ocr_pipeline.modules.text_corrector import TextCorrectionEngine
from src.ocr_pipeline.models import CorrectionSuggestion

def test_text_correction_engine():
    engine = TextCorrectionEngine()
    sample_text = (
        "# Document Review\n\n"
        "This is a review of platform from student perspective.\n"
        "The implomentation and usebility of froin this document is good.\n\n"
        "=== PAGE BREAK ===\n\n"
        "1. Fix Kowid metrix calculations.\n"
    )

    result = engine.analyze_text(sample_text)

    assert result.original_text == sample_text
    assert isinstance(result.suggestions, list)
    assert len(result.suggestions) > 0

    # Verify quality metrics
    metrics = result.quality_metrics
    assert "spelling_errors" in metrics
    assert "missing_words" in metrics
    assert "total_suggestions" in metrics
    assert metrics["total_suggestions"] == len(result.suggestions)

    # Verify offset accuracy for suggestions
    for sug in result.suggestions:
        assert 0 <= sug.start_offset < sug.end_offset <= len(sample_text)
        assert sample_text[sug.start_offset : sug.end_offset] == sug.original_text
        assert sug.category in [
            'Spelling Correction', 'Grammar Correction', 'Missing Word',
            'Punctuation Improvement', 'Capitalization', 'OCR Confidence Recovery',
            'Sentence Structure', 'Style Suggestion', 'Character Confusion', 'Contextual Substitution'
        ]
        assert 0.0 <= sug.confidence_score <= 1.0
        assert len(sug.explanation) > 0

def test_apply_suggestions_selective():
    engine = TextCorrectionEngine()
    original_text = "The implomentation of froin document is ready."
    
    suggestions = [
        CorrectionSuggestion(
            suggestion_id="sug_1",
            original_text="implomentation",
            proposed_correction="implementation",
            category="Spelling Correction",
            confidence_score=0.90,
            explanation="Fix spelling",
            start_offset=4,
            end_offset=18
        ),
        CorrectionSuggestion(
            suggestion_id="sug_2",
            original_text="froin",
            proposed_correction="from",
            category="Spelling Correction",
            confidence_score=0.88,
            explanation="Fix OCR error",
            start_offset=22,
            end_offset=27
        )
    ]

    # Accept only sug_1
    corrected_1 = engine.apply_suggestions(original_text, ["sug_1"], suggestions)
    assert "implementation" in corrected_1
    assert "froin" in corrected_1  # sug_2 rejected

    # Accept both sug_1 and sug_2
    corrected_all = engine.apply_suggestions(original_text, ["sug_1", "sug_2"], suggestions)
    assert corrected_all == "The implementation of from document is ready."
