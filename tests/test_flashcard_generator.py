import pytest
import os
import shutil
import tempfile
from src.ocr_pipeline.modules.flashcard_generator import FlashcardGeneratorEngine

@pytest.fixture
def temp_generator():
    temp_dir = tempfile.mkdtemp()
    engine = FlashcardGeneratorEngine(storage_dir=temp_dir)
    yield engine
    shutil.rmtree(temp_dir)

def test_flashcard_deck_generation(temp_generator):
    exported_text = "The student receive their homework yesterday. It was a incredible success."
    accepted_suggestions = [
        {
            "suggestion_id": "sug_1",
            "original_text": "receive",
            "proposed_correction": "received",
            "category": "Grammar Correction",
            "confidence_score": 0.95,
            "explanation": "Verb tense mismatch. Use past tense 'received'.",
            "start_offset": 12,
            "end_offset": 19
        },
        {
            "suggestion_id": "sug_2",
            "original_text": "a incredible",
            "proposed_correction": "an incredible",
            "category": "Grammar Correction",
            "confidence_score": 0.92,
            "explanation": "Use article 'an' before vowel sound.",
            "start_offset": 52,
            "end_offset": 64
        }
    ]

    res = temp_generator.generate_deck(
        exported_text=exported_text,
        accepted_suggestions=accepted_suggestions,
        document_title="Sample English Essay.pdf"
    )

    assert "deck" in res
    assert "telemetry" in res
    deck = res["deck"]

    assert deck["source_document_title"] == "Sample English Essay.pdf"
    assert deck["total_flashcards"] == 2
    assert len(deck["cards"]) == 2

    # Check card styles & metadata
    card1 = deck["cards"][0]
    assert card1["card_style"] in ["grammar_explanation", "spelling", "fill_in_blank"]
    assert "child_friendly_definition" in card1["back"]
    assert "example_sentence" in card1["back"]
    assert "part_of_speech" in card1["back"]
    assert len(card1["back"]["child_friendly_definition"]) > 0
    assert len(card1["back"]["example_sentence"]) > 0

    # Ensure NO legacy placeholder text exists anywhere in the card
    card_str = str(card1)
    assert "Refers to the concept" not in card_str
    assert "Her writing demonstrated" not in card_str

    # Ensure example sentence is between 8 and 20 words
    ex_words = card1["back"]["example_sentence"].split()
    assert 8 <= len(ex_words) <= 20

    assert "original_sentence" in card1
    assert "corrected_sentence" in card1
    assert "learning_objective" in card1
    assert "rule" in card1
    assert card1["accepted_correction"]["original"] == "receive"
    assert card1["accepted_correction"]["proposed"] == "received"

    # Verify persistence
    decks = temp_generator.list_decks()
    assert len(decks) == 1
    assert decks[0]["deck_id"] == deck["deck_id"]

def test_deduplication_and_concept_merging(temp_generator):
    exported_text = "He write everyday. She write everyday."
    accepted_suggestions = [
        {
            "suggestion_id": "sug_1",
            "original_text": "write",
            "proposed_correction": "writes",
            "category": "Grammar Correction",
            "confidence_score": 0.90,
            "explanation": "Subject-verb agreement.",
            "start_offset": 3,
            "end_offset": 8
        },
        {
            "suggestion_id": "sug_2",
            "original_text": "write",
            "proposed_correction": "writes",
            "category": "Grammar Correction",
            "confidence_score": 0.90,
            "explanation": "Subject-verb agreement.",
            "start_offset": 23,
            "end_offset": 28
        }
    ]

    res = temp_generator.generate_deck(
        exported_text=exported_text,
        accepted_suggestions=accepted_suggestions,
        document_title="Deduplication Test"
    )

    deck = res["deck"]
    telemetry = res["telemetry"]

    # Duplicates should be merged into 1 single flashcard with extra examples!
    assert deck["total_flashcards"] == 1
    assert telemetry["duplicate_cards_removed"] == 1

def test_deck_progress_and_deletion(temp_generator):
    exported_text = "I have a apple."
    accepted_suggestions = [
        {
            "suggestion_id": "sug_1",
            "original_text": "a apple",
            "proposed_correction": "an apple",
            "category": "Grammar Correction",
            "confidence_score": 0.91,
            "explanation": "Article usage.",
            "start_offset": 7,
            "end_offset": 14
        }
    ]

    res = temp_generator.generate_deck(
        exported_text=exported_text,
        accepted_suggestions=accepted_suggestions,
        document_title="Progress Test"
    )
    deck_id = res["deck"]["deck_id"]
    card_id = res["deck"]["cards"][0]["id"]

    # Update card progress as mastered & bookmarked
    updated_deck = temp_generator.update_deck_progress(
        deck_id=deck_id,
        card_updates=[{"id": card_id, "is_mastered": True, "is_bookmarked": True}]
    )

    assert updated_deck is not None
    assert updated_deck["mastery_percentage"] == 100.0
    assert updated_deck["study_progress"]["cards_mastered"] == 1

    # Delete deck
    deleted = temp_generator.delete_deck(deck_id)
    assert deleted is True
    assert temp_generator.get_deck(deck_id) is None

def test_child_friendly_definitions_and_classification(temp_generator):
    """Test child-friendly definitions and proper noun / functional grammar classification."""
    exported_text = "The adventure was incredible. He live in Paris."
    accepted_suggestions = [
        {
            "suggestion_id": "sug_vocab",
            "original_text": "advnture",
            "proposed_correction": "adventure",
            "category": "Spelling Correction",
            "confidence_score": 0.95,
            "explanation": "Correct spelling of 'adventure'.",
            "start_offset": 4,
            "end_offset": 13
        },
        {
            "suggestion_id": "sug_grammar",
            "original_text": "is",
            "proposed_correction": "are",
            "category": "Grammar Correction",
            "confidence_score": 0.90,
            "explanation": "Subject-verb agreement.",
            "start_offset": 35,
            "end_offset": 37
        }
    ]

    res = temp_generator.generate_deck(
        exported_text=exported_text,
        accepted_suggestions=accepted_suggestions,
        document_title="Child Friendly Test"
    )

    deck = res["deck"]
    cards = deck["cards"]
    assert len(cards) == 2

    vocab_card = next(c for c in cards if c["accepted_correction"]["proposed"] == "adventure")
    grammar_card = next(c for c in cards if c["accepted_correction"]["proposed"] == "are")

    # Vocabulary card assertions
    assert len(vocab_card["child_friendly_definition"]) > 0
    assert len(vocab_card["official_dictionary_definition"]) > 0
    ex_words = vocab_card["example_sentence"].split()
    assert 8 <= len(ex_words) <= 20

    # Functional grammar edit assertions (dictionary definition skipped cleanly)
    assert grammar_card["child_friendly_definition"] == ""
    assert grammar_card["example_sentence"] == ""
    assert grammar_card["part_of_speech"] in ["verb", "grammar", "noun"]


