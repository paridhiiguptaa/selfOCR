import time
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from ..config import PipelineConfig, default_config
from ..models import TextRegion
from .got_fallback_ocr import GOTFallbackOCR
from ..utils.logging_config import logger, Timer
from ..utils.image_utils import crop_box

from .image_preprocessor import ImagePreprocessor
from .crop_ocr_engine import CropOCREngine
from .quality_estimator import QualityEstimator
from .handwriting_ocr_engine import HandwritingOCREngine

class ConfidenceEvaluator:
    """
    Evaluates VLM & layout quality metrics using Multi-Factor QualityEstimator,
    detects low-quality or uncalibrated gibberish regions, and triggers multi-tier fallback re-processing.
    Merges results non-destructively, retaining highest-quality transcriptions.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.got_fallback = GOTFallbackOCR(self.config)
        self.preprocessor = ImagePreprocessor(self.config)
        self.crop_ocr = CropOCREngine()
        self.handwriting_ocr = HandwritingOCREngine(self.config)
        self.quality_estimator = QualityEstimator(self.config)

    def is_confident(self, confidence: float) -> bool:
        """Check if confidence score meets minimum quality threshold."""
        return confidence >= self.config.min_confidence_threshold

    def compute_word_confidences(self, region: TextRegion) -> List[Dict[str, Any]]:
        """
        Derive word-level confidence scores from region-level confidence and character statistics.
        Identifies specific low-confidence words requiring downstream proofreading validation.
        """
        words = region.text.split()
        if not words:
            return []

        word_list = []
        base_conf = region.confidence

        for w in words:
            # Assign penalty for suspicious noise characters or digits inside words
            has_noise = bool(any(c in r"@~{}[\]|_" for c in w))
            w_conf = max(0.40, base_conf - (0.20 if has_noise else 0.0))
            word_list.append({
                "word": w,
                "confidence": round(w_conf, 4),
                "is_low_confidence": w_conf < self.config.word_confidence_threshold
            })

        return word_list

    def evaluate_and_recover(
        self,
        image: np.ndarray,
        regions: List[TextRegion]
    ) -> Tuple[List[TextRegion], Dict[str, Any]]:
        """
        Evaluate confidence & quality of all regions using QualityEstimator.
        Low quality or uncalibrated regions are automatically reprocessed using a multi-tier recovery pipeline:
          Tier 1: Dedicated Handwriting TrOCR Engine
          Tier 2: Enhanced preprocessing (unsharp mask + contrast boost) + Crop OCR
          Tier 3: GOT-OCR 2.0 Fallback
        Returns (merged_regions, statistics).
        """
        stats = {
            "total_regions": len(regions),
            "high_confidence_count": 0,
            "fallback_invocations": 0,
            "improvements_count": 0,
            "mean_confidence": 0.0,
            "mean_quality_score": 0.0
        }

        if not regions:
            return [], stats

        with Timer("Confidence & Multi-Factor Quality Calibration", logger):
            recovered_regions: List[TextRegion] = []
            conf_sum = 0.0
            quality_sum = 0.0
            recovery_start_time = time.time()
            max_recovery_budget_sec = 5.0
            max_fallback_invocations = 3

            for region in regions:
                crop = crop_box(image, region.bbox)
                q_score, q_indicators = self.quality_estimator.evaluate_region_quality(region, crop=crop)
                region.quality_score = q_score
                region.quality_indicators = q_indicators
                region.word_confidences = self.compute_word_confidences(region)

                is_low_conf = region.confidence < self.config.min_confidence_threshold
                is_low_quality = q_score < self.config.min_quality_score_threshold
                is_gibberish = bool(q_indicators.get("is_uncalibrated_gibberish", 0.0))

                if not is_low_conf and not is_low_quality and not is_gibberish:
                    stats["high_confidence_count"] += 1
                    conf_sum += region.confidence
                    quality_sum += q_score
                    recovered_regions.append(region)
                    continue

                # Check budget / max retry limit
                time_elapsed = time.time() - recovery_start_time
                if stats["fallback_invocations"] >= max_fallback_invocations or time_elapsed > max_recovery_budget_sec:
                    if stats["fallback_invocations"] == max_fallback_invocations:
                        logger.info("[CONFIDENCE RECOVERY] Max fallback retry limit reached. Retaining primary OCR text.")
                    conf_sum += region.confidence
                    quality_sum += q_score
                    recovered_regions.append(region)
                    continue

                # Low quality or empty text detected -> Trigger Recovery
                logger.info(
                    f"[CONFIDENCE RECOVERY] Low quality/uncalibrated region detected (Quality {q_score:.2f}, Gibberish={is_gibberish}) "
                    f"in Region #{region.region_id} ('{region.text}'). Triggering recovery pass."
                )
                stats["fallback_invocations"] += 1

                best_text = region.text
                best_conf = region.confidence
                best_quality = q_score
                best_model = region.fallback_model

                # Tier 1: Fast Crop OCR Engine
                try:
                    t1_text, t1_conf = self.crop_ocr.recognize_crop(crop)
                    if t1_text.strip():
                        dummy_reg = TextRegion(region_id=region.region_id, bbox=region.bbox, text=t1_text, confidence=t1_conf, ink_density=region.ink_density)
                        t1_q, _ = self.quality_estimator.evaluate_region_quality(dummy_reg, crop=crop)
                        if t1_q > best_quality:
                            best_text = t1_text
                            best_conf = t1_conf
                            best_quality = t1_q
                            best_model = "CropOCR_Tier1"
                except Exception as e:
                    logger.warning(f"Tier 1 recovery failed for Region #{region.region_id}: {e}")

                # Tier 2: Enhanced Preprocessing Crop Re-run
                if best_quality < self.config.min_quality_score_threshold:
                    try:
                        enhanced_crop = self.preprocessor.sharpen_unsharp_mask(crop, amount=2.0)
                        t2_text, t2_conf = self.crop_ocr.recognize_crop(enhanced_crop)
                        if t2_text.strip():
                            dummy_reg = TextRegion(region_id=region.region_id, bbox=region.bbox, text=t2_text, confidence=t2_conf, ink_density=region.ink_density)
                            t2_q, _ = self.quality_estimator.evaluate_region_quality(dummy_reg, crop=enhanced_crop)
                            if t2_q > best_quality:
                                best_text = t2_text
                                best_conf = t2_conf
                                best_quality = t2_q
                                best_model = "CropOCR_EnhancedTier2"
                    except Exception as e:
                        logger.warning(f"Tier 2 recovery failed for Region #{region.region_id}: {e}")

                # Tier 3: GOT-OCR 2.0 Fallback (Only if enabled and GPU is active)
                if self.config.enable_got_fallback and self.got_fallback.device == "cuda":
                    try:
                        fallback_text, fallback_conf = self.got_fallback.reprocess_region(crop)
                        if fallback_text.strip():
                            dummy_reg = TextRegion(region_id=region.region_id, bbox=region.bbox, text=fallback_text, confidence=fallback_conf, ink_density=region.ink_density)
                            fb_q, _ = self.quality_estimator.evaluate_region_quality(dummy_reg, crop=crop)
                            if fb_q > best_quality:
                                best_text = fallback_text
                                best_conf = fallback_conf
                                best_quality = fb_q
                                best_model = self.got_fallback.model_name
                    except Exception as e:
                        logger.warning(f"Tier 3 GOT-OCR recovery failed for Region #{region.region_id}: {e}")

                # Non-destructive merge: update region if quality improved
                if best_quality > q_score and len(best_text.strip()) > 0:
                    logger.info(
                        f"Multi-tier recovery improved Region #{region.region_id} quality: "
                        f"{q_score:.2f} -> {best_quality:.2f} [{best_model}] | Text: '{best_text}'"
                    )
                    region.text = best_text
                    region.confidence = best_conf
                    region.quality_score = best_quality
                    region.fallback_triggered = True
                    region.fallback_model = best_model
                    region.word_confidences = self.compute_word_confidences(region)
                    stats["improvements_count"] += 1
                else:
                    logger.info(f"Multi-tier recovery did not improve quality. Retaining primary result for Region #{region.region_id}.")

                conf_sum += region.confidence
                quality_sum += region.quality_score
                recovered_regions.append(region)

            stats["mean_confidence"] = round(conf_sum / max(1, len(regions)), 4)
            stats["mean_quality_score"] = round(quality_sum / max(1, len(regions)), 4)
            logger.info(
                f"Confidence & Quality evaluation complete: {stats['high_confidence_count']}/{stats['total_regions']} high quality, "
                f"{stats['fallback_invocations']} fallback retries, {stats['improvements_count']} improved."
            )
            return recovered_regions, stats
