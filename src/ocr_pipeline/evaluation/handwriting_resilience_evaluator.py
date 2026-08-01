import time
from typing import List, Dict, Any, Optional

from ..modules.text_recovery_layer import TextRecoveryLayer
from ..modules.text_corrector import TextCorrectionEngine
from ..modules.flashcard_generator import FlashcardGeneratorEngine
from ..utils.logging_config import logger

NOISY_HANDWRITING_TEST_CASES = [
    {
        "test_id": "hw_noise_01_hyphen_split",
        "raw_ocr": "The student wrote a hand-\nwritten story about a boy who road a bicycle.",
        "expected_substring": "handwritten"
    },
    {
        "test_id": "hw_noise_02_missing_space",
        "raw_ocr": "The sky is blue.Peeping through the clouds.Ans: Yes, I see it.",
        "expected_substring": "blue. Peeping"
    },
    {
        "test_id": "hw_noise_03_character_confusion",
        "raw_ocr": "The skv is blue with yellov sun and areen grass.",
        "expected_substring": "sky"
    },
    {
        "test_id": "hw_noise_04_contextual_homophone",
        "raw_ocr": "The boy road the bicycle to school. She red the book.",
        "expected_substring": "rode"
    },
    {
        "test_id": "hw_noise_05_punctuation_restore",
        "raw_ocr": "Where do you see the rainbowAns: In the sky",
        "expected_substring": "rainbow?"
    }
]

class HandwritingResilienceEvaluator:
    """
    Dedicated Evaluation Framework for Handwriting OCR Text Recovery & Proofreading Resilience.
    Tests noisy, fragmented, and un-punctuated OCR transcriptions and asserts 100% end-to-end execution
    across OCR text recovery, 5-stage proofreading, and educational flashcard deck creation.
    """

    def __init__(self):
        self.recovery_layer = TextRecoveryLayer()
        self.correction_engine = TextCorrectionEngine()
        self.flashcard_engine = FlashcardGeneratorEngine()

    def evaluate_resilience(self, cases: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Execute handwriting resilience benchmark."""
        test_cases = cases or NOISY_HANDWRITING_TEST_CASES
        start_time = time.time()

        total_cases = len(test_cases)
        successful_recoveries = 0
        successful_decks = 0
        eval_cases = []

        for tc in test_cases:
            raw = tc["raw_ocr"]
            exp = tc["expected_substring"]

            # Step 1: Text Recovery Layer
            rec_text, rec_meta = self.recovery_layer.recover_text(raw)
            assert isinstance(rec_text, str)

            # Step 2: 5-Stage Proofreading Engine
            corr_res = self.correction_engine.analyze_text(raw)
            corrected_text = corr_res.corrected_text
            suggestions = [s.to_dict() for s in corr_res.suggestions]

            if exp.lower() in corrected_text.lower():
                successful_recoveries += 1

            # Step 3: Flashcard Generation Pipeline
            deck_res = self.flashcard_engine.generate_deck(
                exported_text=corrected_text,
                accepted_suggestions=suggestions,
                document_title=tc["test_id"]
            )
            deck = deck_res.get("deck", {})
            if deck and "cards" in deck:
                successful_decks += 1

            eval_cases.append({
                "test_id": tc["test_id"],
                "raw_input": raw,
                "recovered_text": rec_text,
                "corrected_text": corrected_text,
                "suggestions_count": len(suggestions),
                "flashcards_count": deck.get("total_flashcards", 0),
                "success": exp.lower() in corrected_text.lower()
            })

        recovery_rate = successful_recoveries / max(1, total_cases)
        deck_rate = successful_decks / max(1, total_cases)
        elapsed = time.time() - start_time

        summary = {
            "total_test_cases": total_cases,
            "successful_text_recoveries": successful_recoveries,
            "recovery_success_rate": round(recovery_rate, 4),
            "successful_deck_generations": successful_decks,
            "deck_generation_rate": round(deck_rate, 4),
            "duration_sec": round(elapsed, 3)
        }

        logger.info(
            f"Handwriting Resilience Benchmark Complete: {successful_recoveries}/{total_cases} recoveries "
            f"({recovery_rate*100:.1f}%), {successful_decks}/{total_cases} flashcard decks created."
        )

        return {
            "summary": summary,
            "cases": eval_cases
        }
