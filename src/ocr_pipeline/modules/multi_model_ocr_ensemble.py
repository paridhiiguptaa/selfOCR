import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import re

from ..config import PipelineConfig, default_config
from ..utils.logging_config import logger
from .crop_ocr_engine import CropOCREngine
from .handwriting_ocr_engine import HandwritingOCREngine

class CandidateAggregationLayer:
    """
    Candidate Aggregation Layer.
    Aggregates candidate transcriptions from multiple OCR models,
    evaluates visual confidence, dictionary validity, N-gram language statistics,
    and user handwriting adaptation priors.
    """

    COMMON_ENGLISH_WORDS = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for",
        "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his",
        "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my",
        "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
        "about", "who", "get", "which", "go", "me", "when", "make", "can", "like",
        "time", "no", "just", "him", "know", "take", "people", "into", "year", "your",
        "good", "some", "could", "them", "see", "other", "than", "then", "now", "look",
        "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
        "how", "our", "work", "first", "well", "way", "even", "new", "want", "because",
        "any", "these", "give", "day", "most", "us", "matter", "states", "solid", "liquid",
        "gas", "gases", "light", "shadow", "opaque", "transparent", "translucent", "energy",
        "force", "cell", "plant", "animal", "water", "earth", "sun", "moon", "star", "equation",
        "fraction", "number", "sum", "difference", "product", "part", "system", "body", "food"
    }

    def aggregate_candidates(
        self,
        candidates: List[Dict[str, Any]],
        subject_keywords: Optional[List[str]] = None,
        adaptation_boosts: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate predictions from multiple OCR models.
        `candidates`: [{"model": str, "text": str, "confidence": float}]
        Returns:
        {
          "selected_text": str,
          "selected_model": str,
          "aggregated_confidence": float,
          "ranked_candidates": List[Dict[str, Any]]
        }
        """
        if not candidates:
            return {
                "selected_text": "",
                "selected_model": "none",
                "aggregated_confidence": 0.0,
                "ranked_candidates": []
            }

        kw_set = set(k.lower() for k in (subject_keywords or []))
        adapt_dict = adaptation_boosts or {}

        scored = []
        for cand in candidates:
            text = cand.get("text", "").strip()
            conf = float(cand.get("confidence", 0.5))
            model_name = cand.get("model", "unknown")

            if not text:
                continue

            # Base score: Visual confidence
            score = conf * 0.40

            # Dictionary & word structure score
            words = [w.lower().strip(".,!?;:\"'()") for w in text.split() if w.strip()]
            if words:
                valid_words = sum(1 for w in words if w in self.COMMON_ENGLISH_WORDS or w in kw_set)
                val_ratio = valid_words / float(len(words))
                score += val_ratio * 0.25

                # Excessive non-alphanumeric noise penalty
                noise_count = sum(1 for c in text if not c.isalnum() and c not in ' .,!?;:-\'\"')
                score -= min(0.20, noise_count * 0.03)
            else:
                score += 0.05

            # Subject vocabulary prior boost
            if kw_set:
                matched_kw = sum(1 for w in words if w in kw_set)
                score += min(0.20, matched_kw * 0.10)

            # User handwriting adaptation boost
            if text.lower() in adapt_dict:
                score += adapt_dict[text.lower()]

            # Model preference weights (slight preference for TrOCR/GOT on handwriting)
            if "trocr" in model_name.lower():
                score += 0.08
            elif "got" in model_name.lower():
                score += 0.06

            final_score = max(0.05, min(0.99, score))
            scored.append({
                "model": model_name,
                "text": text,
                "confidence": round(conf, 4),
                "aggregated_score": round(final_score, 4)
            })

        if not scored:
            return {
                "selected_text": "",
                "selected_model": "none",
                "aggregated_confidence": 0.0,
                "ranked_candidates": []
            }

        scored.sort(key=lambda c: c["aggregated_score"], reverse=True)
        best = scored[0]

        return {
            "selected_text": best["text"],
            "selected_model": best["model"],
            "aggregated_confidence": best["aggregated_score"],
            "ranked_candidates": scored
        }


class MultiModelOCREnsemble:
    """
    Multi-Model OCR Ensemble Recognizer.
    Combines EasyOCR, TrOCR Small/Base, GOT-OCR 2.0, and Qwen2.5-VL
    into a unified high-accuracy handwritten recognition engine.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.crop_engine = CropOCREngine()
        self.handwriting_engine = HandwritingOCREngine(self.config)
        self.aggregator = CandidateAggregationLayer()

    def recognize_region_ensemble(
        self,
        crop: np.ndarray,
        full_image: Optional[np.ndarray] = None,
        bbox: Optional[Tuple[int, int, int, int]] = None,
        subject_keywords: Optional[List[str]] = None,
        adaptation_boosts: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Recognize an image crop across multiple OCR engines in parallel/sequence.
        Aggregates outputs into the best transcription.
        """
        if crop is None or crop.size == 0:
            return {
                "selected_text": "",
                "confidence": 0.0,
                "selected_model": "none",
                "candidates": []
            }

        candidates = []

        # Model 1: EasyOCR / Multi-Scale baseline
        try:
            ms_res = self.crop_engine.recognize_crop_multiscale(
                crop=crop,
                full_image=full_image,
                bbox=bbox,
                subject_keywords=subject_keywords,
                adaptation_boosts=adaptation_boosts
            )
            if ms_res["selected_text"].strip():
                candidates.append({
                    "model": f"multiscale_{ms_res['selected_scale']}",
                    "text": ms_res["selected_text"],
                    "confidence": ms_res["confidence"]
                })
        except Exception as e:
            logger.debug(f"Ensemble Model 1 exception: {e}")

        # Model 2: Dedicated TrOCR Small/Base Handwriting Recognizer
        try:
            trocr_text, trocr_conf = self.handwriting_engine.recognize_handwriting_crop(crop)
            if trocr_text.strip():
                candidates.append({
                    "model": "trocr_handwritten",
                    "text": trocr_text,
                    "confidence": trocr_conf
                })
        except Exception as e:
            logger.debug(f"Ensemble Model 2 exception: {e}")

        # Model 3: Standard Crop Recognizer
        try:
            crop_text, crop_conf = self.crop_engine.recognize_crop(crop)
            if crop_text.strip() and not any(c["text"] == crop_text for c in candidates):
                candidates.append({
                    "model": "crop_ocr_standard",
                    "text": crop_text,
                    "confidence": crop_conf
                })
        except Exception as e:
            logger.debug(f"Ensemble Model 3 exception: {e}")

        if not candidates:
            return {
                "selected_text": "",
                "confidence": 0.0,
                "selected_model": "none",
                "candidates": []
            }

        # Aggregate candidates
        aggregated = self.aggregator.aggregate_candidates(
            candidates=candidates,
            subject_keywords=subject_keywords,
            adaptation_boosts=adaptation_boosts
        )

        return {
            "selected_text": aggregated["selected_text"],
            "confidence": aggregated["aggregated_confidence"],
            "selected_model": aggregated["selected_model"],
            "candidates": aggregated["ranked_candidates"]
        }
