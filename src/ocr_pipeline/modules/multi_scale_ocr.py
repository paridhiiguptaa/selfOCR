import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import math
import re

from ..config import PipelineConfig, default_config
from ..utils.logging_config import logger

class MultiScaleImageGenerator:
    """
    Generates multi-scale and multi-enhancement cropped image variations
    for handwritten text line regions.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config

    def generate_scales(
        self,
        crop: np.ndarray,
        full_image: Optional[np.ndarray] = None,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple preprocessed image variations for a given crop.
        Returns a list of dicts: [{"scale_name": str, "image": np.ndarray, "description": str}].
        """
        if crop is None or crop.size == 0:
            return []

        h, w = crop.shape[:2]
        if h < 5 or w < 5:
            return [{"scale_name": "original", "image": crop, "description": "Original crop"}]

        scales: List[Dict[str, Any]] = []

        # 1. Original crop
        scales.append({
            "scale_name": "original",
            "image": crop,
            "description": "Original raw crop"
        })

        # 2. CLAHE Contrast Boost
        try:
            lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB) if len(crop.shape) == 3 else cv2.cvtColor(cv2.cvtColor(crop, cv2.COLOR_GRAY2RGB), cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4))
            cl = clahe.apply(l)
            clahe_img = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2RGB)
            scales.append({
                "scale_name": "clahe_contrast",
                "image": clahe_img,
                "description": "CLAHE contrast enhanced crop"
            })
        except Exception as e:
            logger.debug(f"CLAHE scale generation notice: {e}")

        # 3. Unsharp Mask Sharpened
        try:
            blurred = cv2.GaussianBlur(crop, (0, 0), 1.0)
            sharpened = cv2.addWeighted(crop, 2.0, blurred, -1.0, 0)
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            scales.append({
                "scale_name": "unsharp_sharpened",
                "image": sharpened,
                "description": "Unsharp mask stroke sharpened crop"
            })
        except Exception as e:
            logger.debug(f"Unsharp scale notice: {e}")

        # 4. Lanczos Adaptive Super-Resolution / Upsampling
        try:
            target_h = max(64, h * 2)
            scale_factor = target_h / float(h)
            target_w = max(10, int(round(w * scale_factor)))
            resampled = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            scales.append({
                "scale_name": "lanczos_super_res",
                "image": resampled,
                "description": "Lanczos-4 upsampled crop"
            })
        except Exception as e:
            logger.debug(f"Lanczos scale notice: {e}")

        # 5. Grayscale Contrast Enhancement
        try:
            gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if len(crop.shape) == 3 else crop
            norm_gray = cv2.normalize(gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            norm_rgb = cv2.cvtColor(norm_gray, cv2.COLOR_GRAY2RGB)
            scales.append({
                "scale_name": "grayscale_enhanced",
                "image": norm_rgb,
                "description": "Normalized grayscale crop"
            })
        except Exception as e:
            logger.debug(f"Grayscale scale notice: {e}")

        # 6. Adaptive Threshold Binarization
        try:
            gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if len(crop.shape) == 3 else crop
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            thresh_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
            scales.append({
                "scale_name": "adaptive_threshold",
                "image": thresh_rgb,
                "description": "Adaptive Gaussian binarized crop"
            })
        except Exception as e:
            logger.debug(f"Adaptive threshold notice: {e}")

        # 7. Context Expanded Crop (from full image if available)
        if full_image is not None and bbox is not None:
            try:
                xmin, ymin, xmax, ymax = bbox
                img_h, img_w = full_image.shape[:2]
                pad_v = max(10, int((ymax - ymin) * 0.20))
                pad_h = max(15, int((xmax - xmin) * 0.12))
                ex_ymin = max(0, ymin - pad_v)
                ex_ymax = min(img_h, ymax + pad_v)
                ex_xmin = max(0, xmin - pad_h)
                ex_xmax = min(img_w, xmax + pad_h)
                ctx_crop = full_image[ex_ymin:ex_ymax, ex_xmin:ex_xmax]
                if ctx_crop.size > 0:
                    scales.append({
                        "scale_name": "context_expanded",
                        "image": ctx_crop,
                        "description": "Expanded context crop with ascender/descender margin"
                    })
            except Exception as e:
                logger.debug(f"Context expanded scale notice: {e}")

        # 8. Tighter Crop (Trim minimal padding)
        try:
            pad_v = max(1, int(h * 0.05))
            pad_h = max(1, int(w * 0.03))
            if h - 2 * pad_v > 10 and w - 2 * pad_h > 10:
                tighter = crop[pad_v:h-pad_v, pad_h:w-pad_h]
                scales.append({
                    "scale_name": "tighter_crop",
                    "image": tighter,
                    "description": "Tight margin crop"
                })
        except Exception as e:
            logger.debug(f"Tight crop scale notice: {e}")

        return scales


class CandidateFusionModule:
    """
    Evaluates multi-scale recognition candidates and fuses visual confidence,
    language statistics, subject priors, and user handwriting adaptation.
    """

    # Common English words and valid educational letter N-grams for candidate scoring
    COMMON_VOCAB = {
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
        "fraction", "number", "sum", "difference", "product", "part", "system", "body", "food",
        "air", "pressure", "acid", "base", "metal", "heat", "temperature", "color", "shape",
        "volume", "mass", "density", "line", "point", "angle", "triangle", "circle", "square"
    }

    def evaluate_and_fuse(
        self,
        candidates: List[Dict[str, Any]],
        subject_keywords: Optional[List[str]] = None,
        adaptation_boosts: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate transcriptions and choose the best candidate.
        Each item in `candidates`: {"text": str, "confidence": float, "scale": str}
        Returns:
        {
          "selected_text": str,
          "selected_scale": str,
          "fused_confidence": float,
          "ranked_candidates": List[Dict[str, Any]]
        }
        """
        if not candidates:
            return {
                "selected_text": "",
                "selected_scale": "original",
                "fused_confidence": 0.0,
                "ranked_candidates": []
            }

        subject_kw_set = set(k.lower() for k in (subject_keywords or []))
        adapt_dict = adaptation_boosts or {}

        scored_candidates = []

        for cand in candidates:
            raw_text = cand.get("text", "").strip()
            visual_conf = float(cand.get("confidence", 0.5))
            scale_name = cand.get("scale", "original")

            if not raw_text:
                continue

            # Factor 1: Visual Confidence
            score = visual_conf * 0.40

            # Factor 2: Language Validity (Dictionary & Word Structure)
            words = [w.lower().strip(".,!?;:\"'()") for w in raw_text.split() if w.strip()]
            if words:
                known_count = sum(1 for w in words if w in self.COMMON_VOCAB or w in subject_kw_set)
                validity_ratio = known_count / float(len(words))
                score += validity_ratio * 0.25

                # Penalize non-alphanumeric noise / single character gibberish
                noise_chars = sum(1 for c in raw_text if not c.isalnum() and c not in ' .,!?;:-\'\"')
                noise_penalty = min(0.20, noise_chars * 0.03)
                score -= noise_penalty
            else:
                score += 0.05

            # Factor 3: Subject Vocabulary Prior Boost
            if subject_kw_set:
                subject_match_count = sum(1 for w in words if w in subject_kw_set)
                if subject_match_count > 0:
                    score += min(0.20, subject_match_count * 0.10)

            # Factor 4: User Handwriting Adaptation Boost
            if raw_text.lower() in adapt_dict:
                score += adapt_dict[raw_text.lower()]
            else:
                # Partial word adaptation boost
                partial_boost = sum(adapt_dict.get(w, 0.0) for w in words)
                score += min(0.15, partial_boost)

            # Factor 5: Preferred baseline scale bias (light preference for original/clahe)
            if scale_name in ("original", "clahe_contrast", "unsharp_sharpened"):
                score += 0.05

            final_conf = max(0.05, min(0.99, score))

            scored_candidates.append({
                "text": raw_text,
                "scale": scale_name,
                "visual_confidence": round(visual_conf, 4),
                "fused_score": round(final_conf, 4)
            })

        if not scored_candidates:
            return {
                "selected_text": "",
                "selected_scale": "original",
                "fused_confidence": 0.0,
                "ranked_candidates": []
            }

        # Sort descending by fused score
        scored_candidates.sort(key=lambda c: c["fused_score"], reverse=True)
        best = scored_candidates[0]

        return {
            "selected_text": best["text"],
            "selected_scale": best["scale"],
            "fused_confidence": best["fused_score"],
            "ranked_candidates": scored_candidates
        }
