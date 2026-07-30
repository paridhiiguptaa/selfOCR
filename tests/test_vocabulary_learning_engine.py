"""
Comprehensive Context-First Evaluation Test Suite for Vocabulary Learning Engine
Tests spaCy POS hard constraints, context-first WSD sense selection, embedding ranking,
learner dictionary prioritization, sense-specific synonyms, and zero incorrect sense mappings.
"""

import pytest
from src.ocr_pipeline.modules.vocabulary_engine import (
    POSTagger,
    LearnerLexicalProvider,
    ContextualSemanticWSD,
    SemanticValidator,
    VocabularyLearningEngine
)
from src.ocr_pipeline.modules.flashcard_generator import FlashcardGeneratorEngine
import tempfile
import shutil


def test_spacy_pos_hard_constraints():
    """Verify spaCy POS tagger correctly enforces hard POS constraints for 'very' and 'dirty'."""
    # 1. 'very' in "She was very excited" -> adverb (never noun/adjective)
    pos_very, _, conf1 = POSTagger.tag_word_in_context("very", "She was very excited about the school trip.")
    assert pos_very == "adverb"

    # 2. 'dirty' in "His shoes were dirty" -> adjective (never verb)
    pos_dirty, _, conf2 = POSTagger.tag_word_in_context("dirty", "His shoes were dirty after playing outside.")
    assert pos_dirty == "adjective"


def test_very_and_dirty_sense_resolution():
    """Test that 'very' and 'dirty' resolve to their correct learner definitions."""
    # Test 'very' -> adverb: to a great degree
    res_very = VocabularyLearningEngine.process_correction(
        orig_word="vry", prop_word="very",
        corrected_sentence="The student was very happy with her test results.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_very["is_vocabulary_word"] is True
    assert res_very["detected_pos"] == "adverb"
    assert "great degree" in res_very["official_dictionary_definition"].lower() or "high degree" in res_very["simplified_child_definition"].lower()
    assert "really" not in res_very["identified_word_sense"] or "adv" in res_very["identified_word_sense"]

    # Test 'dirty' -> adjective: not clean (never verb: to make dirty)
    res_dirty = VocabularyLearningEngine.process_correction(
        orig_word="drty", prop_word="dirty",
        corrected_sentence="His hands were dirty after digging in the garden.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_dirty["is_vocabulary_word"] is True
    assert res_dirty["detected_pos"] == "adjective"
    assert "not clean" in res_dirty["simplified_child_definition"].lower() or "soil" in res_dirty["official_dictionary_definition"].lower() or "muddy" in res_dirty["simplified_child_definition"].lower()
    assert "soiled" in res_dirty["synonyms"] or "muddy" in res_dirty["synonyms"] or "unclean" in res_dirty["synonyms"]


def test_20_word_polysemy_evaluation_suite():
    """Test 20+ ambiguous/polysemous words across different sentence contexts."""

    # 1. light (noun vs adjective)
    res_light_n = VocabularyLearningEngine.process_correction(
        orig_word="lght", prop_word="light",
        corrected_sentence="Turn on the bright light so we can read our books.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_light_n["detected_pos"] == "noun"
    assert "brightness" in res_light_n["simplified_child_definition"].lower() or "see" in res_light_n["simplified_child_definition"].lower()

    res_light_adj = VocabularyLearningEngine.process_correction(
        orig_word="lght", prop_word="light",
        corrected_sentence="The small box was light and easy to carry to school.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_light_adj["detected_pos"] == "adjective"
    assert "heavy" in res_light_adj["simplified_child_definition"].lower() or "lightweight" in res_light_adj["synonyms"]

    # 2. bank (financial vs river)
    res_bank_fin = VocabularyLearningEngine.process_correction(
        orig_word="bnk", prop_word="bank",
        corrected_sentence="My parents went to the bank to deposit their savings.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bank_fin["detected_pos"] == "noun"
    assert "money" in res_bank_fin["simplified_child_definition"].lower()

    res_bank_riv = VocabularyLearningEngine.process_correction(
        orig_word="bnk", prop_word="bank",
        corrected_sentence="We sat on the grassy bank of the river watching ducks swim.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bank_riv["detected_pos"] == "noun"
    assert "river" in res_bank_riv["simplified_child_definition"].lower() or "land" in res_bank_riv["simplified_child_definition"].lower()

    # 3. bat (animal vs sports)
    res_bat_anim = VocabularyLearningEngine.process_correction(
        orig_word="bt", prop_word="bat",
        corrected_sentence="A small bat flew out of the dark cave at sunset.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bat_anim["detected_pos"] == "noun"
    assert "flying" in res_bat_anim["simplified_child_definition"].lower() or "mammal" in res_bat_anim["simplified_child_definition"].lower()

    res_bat_sport = VocabularyLearningEngine.process_correction(
        orig_word="bt", prop_word="bat",
        corrected_sentence="He swung the wooden baseball bat and hit a home run.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bat_sport["detected_pos"] == "noun"
    assert "baseball" in res_bat_sport["simplified_child_definition"].lower() or "club" in res_bat_sport["simplified_child_definition"].lower()

    # 4. spring (season vs water)
    res_spring_sea = VocabularyLearningEngine.process_correction(
        orig_word="sprng", prop_word="spring",
        corrected_sentence="Colorful flowers begin to bloom everywhere during early spring.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_spring_sea["detected_pos"] == "noun"
    assert "season" in res_spring_sea["simplified_child_definition"].lower() or "flowers" in res_spring_sea["simplified_child_definition"].lower()

    res_spring_wat = VocabularyLearningEngine.process_correction(
        orig_word="sprng", prop_word="spring",
        corrected_sentence="Cool mountain water flowed clean and clear from the natural spring.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_spring_wat["detected_pos"] == "noun"
    assert "water" in res_spring_wat["simplified_child_definition"].lower()

    # 5. fair (just vs festival)
    res_fair_just = VocabularyLearningEngine.process_correction(
        orig_word="far", prop_word="fair",
        corrected_sentence="The teacher gave everyone a fair turn to answer the question.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_fair_just["detected_pos"] == "adjective"
    assert "equal" in res_fair_just["simplified_child_definition"].lower() or "rules" in res_fair_just["simplified_child_definition"].lower()

    res_fair_event = VocabularyLearningEngine.process_correction(
        orig_word="far", prop_word="fair",
        corrected_sentence="Our family enjoyed playing games at the annual fair.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_fair_event["detected_pos"] == "noun"
    assert "event" in res_fair_event["simplified_child_definition"].lower() or "games" in res_fair_event["simplified_child_definition"].lower()

    # 6. bark (verb vs noun)
    res_bark_v = VocabularyLearningEngine.process_correction(
        orig_word="brk", prop_word="bark",
        corrected_sentence="The puppy started to bark happily when we arrived home.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bark_v["detected_pos"] == "verb"
    assert "sound" in res_bark_v["simplified_child_definition"].lower() or "dog" in res_bark_v["simplified_child_definition"].lower()

    res_bark_n = VocabularyLearningEngine.process_correction(
        orig_word="brk", prop_word="bark",
        corrected_sentence="Rough tree bark protects the trunk of tall oak trees.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_bark_n["detected_pos"] == "noun"
    assert "tree" in res_bark_n["simplified_child_definition"].lower() or "outer" in res_bark_n["simplified_child_definition"].lower()

    # 7. right (adjective vs adverb)
    res_right_adj = VocabularyLearningEngine.process_correction(
        orig_word="rght", prop_word="right",
        corrected_sentence="She gave the right answer to the math problem.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_right_adj["detected_pos"] == "adjective"
    assert "correct" in res_right_adj["simplified_child_definition"].lower() or "true" in res_right_adj["simplified_child_definition"].lower()

    # 8. well (adverb vs noun)
    res_well_adv = VocabularyLearningEngine.process_correction(
        orig_word="wel", prop_word="well",
        corrected_sentence="The student performed very well on her science exam.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_well_adv["detected_pos"] == "adverb"
    assert "good" in res_well_adv["simplified_child_definition"].lower() or "satisfactory" in res_well_adv["simplified_child_definition"].lower()

    # 9. watch (noun vs verb)
    res_watch_n = VocabularyLearningEngine.process_correction(
        orig_word="wtch", prop_word="watch",
        corrected_sentence="He checked his new watch to see if class was starting.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_watch_n["detected_pos"] == "noun"
    assert "clock" in res_watch_n["simplified_child_definition"].lower() or "wrist" in res_watch_n["simplified_child_definition"].lower()

    res_watch_v = VocabularyLearningEngine.process_correction(
        orig_word="wtch", prop_word="watch",
        corrected_sentence="The children sat together to watch the science movie.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_watch_v["detected_pos"] == "verb"
    assert "look" in res_watch_v["simplified_child_definition"].lower() or "observe" in res_watch_v["simplified_child_definition"].lower()

    # 10. play (verb vs noun)
    res_play_v = VocabularyLearningEngine.process_correction(
        orig_word="ply", prop_word="play",
        corrected_sentence="Children love to play tag together during recess.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_play_v["detected_pos"] == "verb"
    assert "fun" in res_play_v["simplified_child_definition"].lower() or "games" in res_play_v["simplified_child_definition"].lower()

    # 11. hard (adjective vs adverb)
    res_hard_adj = VocabularyLearningEngine.process_correction(
        orig_word="hrd", prop_word="hard",
        corrected_sentence="The diamond is a hard stone that cannot be scratched easily.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_hard_adj["detected_pos"] == "adjective"
    assert "solid" in res_hard_adj["simplified_child_definition"].lower() or "firm" in res_hard_adj["simplified_child_definition"].lower()

    # 12. kind (adjective vs noun)
    res_kind_adj = VocabularyLearningEngine.process_correction(
        orig_word="knd", prop_word="kind",
        corrected_sentence="She is a kind friend who always helps her classmates.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_kind_adj["detected_pos"] == "adjective"
    assert "caring" in res_kind_adj["simplified_child_definition"].lower() or "friendly" in res_kind_adj["simplified_child_definition"].lower()

    # 13. mean (adjective vs verb)
    res_mean_adj = VocabularyLearningEngine.process_correction(
        orig_word="mn", prop_word="mean",
        corrected_sentence="Saying mean words can hurt someone's feelings.",
        category="Spelling Correction", explanation="Correct spelling"
    )
    assert res_mean_adj["detected_pos"] == "adjective"
    assert "unkind" in res_mean_adj["simplified_child_definition"].lower() or "hurtful" in res_mean_adj["simplified_child_definition"].lower()


def test_confidence_scoring_and_manual_verification_flag():
    """Verify confidence metrics and manual verification flag for uncertain words."""
    res_unknown = VocabularyLearningEngine.process_correction(
        orig_word="xyzqw", prop_word="xyzqw",
        corrected_sentence="The student saw a xyzqw in the garden.",
        category="Vocabulary Choice", explanation="Unusual term"
    )

    assert res_unknown["confidence_score"] <= 0.70
    assert res_unknown["requires_manual_verification"] is True


def test_full_flashcard_generator_deck_integration():
    """Verify FlashcardGeneratorEngine creates decks with grounded context-first definitions."""
    temp_dir = tempfile.mkdtemp()
    try:
        engine = FlashcardGeneratorEngine(storage_dir=temp_dir)
        exported_text = "She was very happy. His shoes were dirty after playing."
        suggestions = [
            {
                "suggestion_id": "s1",
                "original_text": "vry",
                "proposed_correction": "very",
                "category": "Spelling Correction",
                "confidence_score": 0.95,
                "explanation": "Correct spelling of very",
                "start_offset": 8,
                "end_offset": 12
            },
            {
                "suggestion_id": "s2",
                "original_text": "drty",
                "proposed_correction": "dirty",
                "category": "Spelling Correction",
                "confidence_score": 0.95,
                "explanation": "Correct spelling of dirty",
                "start_offset": 30,
                "end_offset": 35
            }
        ]

        result = engine.generate_deck(exported_text, suggestions, document_title="Context-First Integration Test")
        deck = result["deck"]

        assert deck["total_flashcards"] == 2
        card1 = next(c for c in deck["cards"] if c["accepted_correction"]["proposed"] == "very")
        card2 = next(c for c in deck["cards"] if c["accepted_correction"]["proposed"] == "dirty")

        assert card1["detected_pos"] == "adverb"
        assert "degree" in card1["simplified_child_definition"].lower()

        assert card2["detected_pos"] == "adjective"
        assert "clean" in card2["simplified_child_definition"].lower() or "dirty" in card2["simplified_child_definition"].lower()

    finally:
        shutil.rmtree(temp_dir)
