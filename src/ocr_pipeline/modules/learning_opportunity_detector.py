import re
import difflib
from typing import List, Dict, Any, Tuple, Optional
from ..utils.logging_config import logger

class LearningOpportunityDetector:
    """
    Dedicated Learning Opportunity Detection Engine.
    Uses token sequence alignment between original OCR transcriptions and accepted proofreading history
    to identify every educational learning opportunity and map it to an appropriate flashcard activity style.
    """

    CATEGORY_TO_CARD_STYLE = {
        "Spelling Mistake": "spelling",
        "Spelling Correction": "spelling",
        "Vocabulary Improvement": "vocabulary",
        "Contextual Word Correction": "vocabulary",
        "Contextual Substitution": "vocabulary",
        "Grammar Correction": "grammar_explanation",
        "Subject-Verb Agreement": "grammar_explanation",
        "Verb Tense": "grammar_explanation",
        "Article Usage": "grammar_explanation",
        "Preposition Usage": "grammar_explanation",
        "Punctuation Correction": "punctuation_practice",
        "Punctuation Improvement": "punctuation_practice",
        "Missing Word": "fill_in_blank",
        "Capitalization": "capitalization_rule",
        "Capitalization Correction": "capitalization_rule",
        "Sentence Restructuring": "sentence_reconstruction",
        "Style Suggestion": "sentence_reconstruction",
        "Stylistic Improvement": "sentence_reconstruction",
        "OCR Confidence Recovery": "spelling",
        "Character Confusion": "spelling",
    }

    def align_and_detect(
        self,
        exported_text: str,
        accepted_suggestions: List[Dict[str, Any]],
        raw_ocr_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze accepted proofreading history and perform token sequence alignment
        to generate a complete list of structured learning opportunities with educational category mappings.
        """
        opportunities = []
        if not accepted_suggestions:
            return opportunities

        for idx, sug in enumerate(accepted_suggestions, 1):
            orig_text = sug.get("original_text", "").strip()
            prop_text = sug.get("proposed_correction", "").strip()
            raw_cat = sug.get("category", "Grammar Correction")
            explanation = sug.get("explanation", "")
            conf = sug.get("confidence_score", 0.90)

            if not orig_text and not prop_text:
                continue

            # Classify into granular educational category
            refined_cat = self.classify_category(orig_text, prop_text, raw_cat, explanation)
            card_style = self.CATEGORY_TO_CARD_STYLE.get(refined_cat, "grammar_explanation")

            decision_log = {
                "suggestion_id": sug.get("suggestion_id", f"sug_{idx}"),
                "original_text": orig_text,
                "proposed_correction": prop_text,
                "raw_category": raw_cat,
                "classified_category": refined_cat,
                "selected_card_style": card_style,
                "confidence_score": conf,
                "generated": True,
                "reason": f"Captured meaningful learning opportunity classified as '{refined_cat}' mapped to card style '{card_style}'."
            }

            opp = {
                "opportunity_id": f"opp_{idx}",
                "original_text": orig_text,
                "proposed_correction": prop_text,
                "category": refined_cat,
                "card_style": card_style,
                "explanation": explanation or f"Learn the correct form: '{prop_text}' instead of '{orig_text}'.",
                "confidence_score": conf,
                "start_offset": sug.get("start_offset", -1),
                "end_offset": sug.get("end_offset", -1),
                "line_number": sug.get("line_number", 1),
                "decision_log": decision_log
            }

            opportunities.append(opp)

        logger.info(f"Learning Opportunity Detector identified {len(opportunities)} structured learning opportunities from {len(accepted_suggestions)} accepted corrections.")
        return opportunities

    def classify_category(self, orig: str, prop: str, raw_cat: str, explanation: str) -> str:
        """Categorize correction into specific educational learning domain."""
        expl_lower = explanation.lower()
        orig_lower = orig.lower()
        prop_lower = prop.lower()

        if "article" in expl_lower or orig_lower in ("a", "an", "the") or prop_lower in ("a", "an", "the"):
            return "Article Usage"

        if "subject-verb" in expl_lower or "agreement" in expl_lower:
            return "Subject-Verb Agreement"

        if "verb tense" in expl_lower or "past participle" in expl_lower or "tense" in expl_lower:
            return "Verb Tense"

        if "preposition" in expl_lower or orig_lower in ("on", "in", "at", "to", "for", "with", "by", "from", "of"):
            return "Preposition Usage"

        if "apostrophe" in expl_lower or "comma" in expl_lower or "period" in expl_lower or "question mark" in expl_lower or raw_cat in ("Punctuation Correction", "Punctuation Improvement"):
            return "Punctuation Correction"

        if raw_cat in ("Capitalization", "Capitalization Correction") or "capitalize" in expl_lower:
            return "Capitalization Correction"

        if raw_cat in ("Contextual Substitution", "Contextual Word Correction") or "homophone" in expl_lower or "contextual" in expl_lower:
            return "Contextual Word Correction"

        if raw_cat in ("Spelling Correction", "Spelling Mistake", "Character Confusion", "OCR Confidence Recovery") or "spelling" in expl_lower or "typo" in expl_lower:
            return "Spelling Mistake"

        if raw_cat == "Missing Word" or not orig:
            return "Missing Word"

        if len(orig.split()) > 2 or len(prop.split()) > 2:
            return "Sentence Restructuring"

        return raw_cat or "Grammar Correction"
