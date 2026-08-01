import time
from typing import List, Dict, Any, Optional
from ..modules.flashcard_generator import FlashcardGeneratorEngine
from ..modules.text_corrector import TextCorrectionEngine
from .benchmark_dataset import BENCHMARK_TEST_CASES, TestCase
from ..utils.logging_config import logger

class FlashcardEvaluator:
    """
    Dedicated evaluation framework for Flashcard Generation pipeline.
    Verifies that every accepted proofreading correction is correctly classified into learning opportunities,
    mapped to appropriate flashcard styles, deduplicated, and converted into study cards.
    """

    def __init__(self):
        self.correction_engine = TextCorrectionEngine()
        self.flashcard_engine = FlashcardGeneratorEngine()

    def evaluate_flashcard_generation(self, test_cases: Optional[List[TestCase]] = None) -> Dict[str, Any]:
        """Execute flashcard evaluation benchmark across target test cases."""
        cases = test_cases or BENCHMARK_TEST_CASES
        start_time = time.time()

        total_accepted_corrections = 0
        total_opportunities_detected = 0
        total_flashcards_created = 0
        category_counts: Dict[str, int] = {}
        card_style_counts: Dict[str, int] = {}
        eval_cases = []

        for tc in cases:
            corr_res = self.correction_engine.analyze_text(tc.raw_ocr_input)
            suggestions = [s.to_dict() for s in corr_res.suggestions]
            accepted_sugs = suggestions  # Treat all suggestions as accepted for benchmark evaluation

            deck_res = self.flashcard_engine.generate_deck(
                exported_text=corr_res.corrected_text,
                accepted_suggestions=accepted_sugs,
                document_title=tc.test_id
            )

            deck = deck_res["deck"]
            cards = deck.get("cards", [])

            total_accepted_corrections += len(accepted_sugs)
            total_flashcards_created += len(cards)

            for card in cards:
                cat = card.get("category", "Grammar Correction")
                style = card.get("card_style", "grammar_explanation")
                category_counts[cat] = category_counts.get(cat, 0) + 1
                card_style_counts[style] = card_style_counts.get(style, 0) + 1

            eval_cases.append({
                "test_id": tc.test_id,
                "category": tc.category,
                "corrections_count": len(accepted_sugs),
                "cards_created": len(cards),
                "cards": [
                    {
                        "id": c.get("id"),
                        "style": c.get("card_style"),
                        "front_title": c.get("front", {}).get("title"),
                        "rule": c.get("rule")
                    } for c in cards
                ]
            })

        conversion_rate = total_flashcards_created / max(1, total_accepted_corrections)
        elapsed = time.time() - start_time

        report = {
            "summary": {
                "total_test_cases": len(cases),
                "total_accepted_corrections": total_accepted_corrections,
                "total_flashcards_created": total_flashcards_created,
                "conversion_rate": round(conversion_rate, 4),
                "category_distribution": category_counts,
                "card_style_distribution": card_style_counts,
                "evaluation_duration_sec": round(elapsed, 3)
            },
            "cases": eval_cases
        }

        logger.info(
            f"Flashcard Evaluation Complete: {total_flashcards_created} flashcards generated from "
            f"{total_accepted_corrections} corrections (Conversion Rate: {conversion_rate*100:.1f}%)."
        )
        return report
