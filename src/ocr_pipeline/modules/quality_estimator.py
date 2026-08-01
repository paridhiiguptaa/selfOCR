import re
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from ..config import PipelineConfig, default_config
from ..models import TextRegion
from ..utils.logging_config import logger

class QualityEstimator:
    """
    Intelligent Multi-Factor Quality Estimator & Confidence Calibration System.
    Evaluates OCR regions using multiple quality indicators:
      1. OCR Model Raw Confidence / Log-Probs
      2. Ink Density & Crop Pixel Quality
      3. Language Consistency & English Dictionary Ratio
      4. Bounding Box Completeness & Aspect Ratio
    Replaces naive binary confidence thresholds with a calibrated quality score Q in [0.0, 1.0].
    """

    ENGLISH_WHITELIST = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not",
        "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from",
        "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would",
        "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which",
        "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know",
        "take", "people", "into", "year", "your", "good", "some", "could", "them", "see",
        "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
        "also", "back", "after", "use", "two", "how", "our", "work", "first", "well",
        "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
        "rainbow", "sky", "green", "blue", "yellow", "orange", "violet", "indigo", "red",
        "clouds", "peeping", "sun", "bicycle", "rode", "road", "book", "read", "school",
        "answer", "question", "questions", "yes", "no", "ans", "implementation", "usability"
    }

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config

    def evaluate_region_quality(self, region: TextRegion, crop: Optional[np.ndarray] = None) -> Tuple[float, Dict[str, float]]:
        """
        Evaluate region using multiple quality indicators and return (calibrated_quality_score, indicators).
        """
        text = region.text.strip()
        conf = region.confidence

        # Indicator 1: Raw OCR Model Confidence
        s_conf = max(0.0, min(1.0, conf))

        # Indicator 2: Ink Density
        ink_density = region.ink_density if region.ink_density > 0 else 0.05
        s_ink = max(0.20, min(1.0, ink_density / 0.15))

        # Indicator 3: Language Consistency & Dictionary Ratio
        s_lang = self.compute_language_consistency(text)

        # Indicator 4: Bounding Box Aspect Ratio
        w, h = region.width, region.height
        s_box = 0.90 if (w >= 10 and h >= 8) else 0.40

        # Calibrated Quality Score Weighted Combination
        # Q = 0.40*S_conf + 0.35*S_lang + 0.15*S_ink + 0.10*S_box
        calibrated_q = (0.40 * s_conf) + (0.35 * s_lang) + (0.15 * s_ink) + (0.10 * s_box)
        calibrated_q = max(0.0, min(1.0, calibrated_q))

        indicators = {
            "raw_confidence": round(s_conf, 4),
            "language_consistency": round(s_lang, 4),
            "ink_density": round(ink_density, 4),
            "box_quality": round(s_box, 4),
            "calibrated_quality": round(calibrated_q, 4)
        }

        # Calibration flags
        is_gibberish = (s_conf >= 0.70 and s_lang <= 0.20 and len(text.split()) > 0)
        indicators["is_uncalibrated_gibberish"] = 1.0 if is_gibberish else 0.0

        if is_gibberish:
            logger.warning(f"Uncalibrated high confidence ({s_conf:.2f}) gibberish detected in Region #{region.region_id}: '{text}'")

        return calibrated_q, indicators

    def compute_language_consistency(self, text: str) -> float:
        """Evaluate dictionary ratio, vowel presence, and gibberish metrics."""
        if not text:
            return 0.0

        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        if not words:
            # Punctuation or digits
            return 0.70 if len(text) <= 5 else 0.30

        valid_count = sum(1 for w in words if w in self.ENGLISH_WHITELIST or bool(re.search(r'[aeiouy]', w)))
        dictionary_ratio = float(valid_count) / float(len(words))

        # Check for repetitive noise (e.g., "|||||", "aaaaa")
        has_vowels = any(re.search(r'[aeiouy]', w) for w in words)
        if not has_vowels:
            dictionary_ratio *= 0.3

        return max(0.10, min(1.0, dictionary_ratio))
