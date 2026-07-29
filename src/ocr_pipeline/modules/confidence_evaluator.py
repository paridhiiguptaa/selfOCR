import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from ..config import PipelineConfig, default_config
from ..models import TextRegion
from .got_fallback_ocr import GOTFallbackOCR
from ..utils.logging_config import logger, Timer
from ..utils.image_utils import crop_box

class ConfidenceEvaluator:
    """
    Evaluates VLM & layout confidence scores, detects low-confidence regions,
    and automatically triggers GOT-OCR 2.0 fallback re-processing.
    Merges results non-destructively, retaining highest-confidence transcriptions.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.got_fallback = GOTFallbackOCR(self.config)

    def is_confident(self, confidence: float) -> bool:
        """Check if confidence score meets minimum quality threshold."""
        return confidence >= self.config.min_confidence_threshold

    def evaluate_and_recover(
        self,
        image: np.ndarray,
        regions: List[TextRegion]
    ) -> Tuple[List[TextRegion], Dict[str, Any]]:
        """
        Evaluate confidence of all regions. Low confidence regions (< min_confidence_threshold)
        are automatically reprocessed using GOT-OCR 2.0.
        Returns (merged_regions, statistics).
        """
        stats = {
            "total_regions": len(regions),
            "high_confidence_count": 0,
            "fallback_invocations": 0,
            "improvements_count": 0,
            "mean_confidence": 0.0
        }

        if not regions:
            return [], stats

        with Timer("Confidence Evaluation & GOT-OCR 2.0 Fallback Recovery", logger):
            recovered_regions: List[TextRegion] = []
            conf_sum = 0.0

            for region in regions:
                current_conf = region.confidence
                conf_sum += current_conf

                if self.is_confident(current_conf) or not self.config.enable_got_fallback:
                    stats["high_confidence_count"] += 1
                    recovered_regions.append(region)
                    continue

                # Low confidence detected -> Trigger GOT-OCR 2.0 fallback
                logger.info(
                    f"Low confidence ({current_conf:.2f} < {self.config.min_confidence_threshold:.2f}) "
                    f"detected in Region #{region.region_id} ('{region.text}'). Triggering GOT-OCR 2.0 fallback."
                )
                stats["fallback_invocations"] += 1

                crop = crop_box(image, region.bbox)
                fallback_text, fallback_conf = self.got_fallback.reprocess_region(crop)

                # Non-destructive merge: keep prediction with HIGHEST confidence
                if fallback_conf > region.confidence and len(fallback_text.strip()) > 0:
                    logger.info(
                        f"Fallback improved Region #{region.region_id} confidence: "
                        f"{region.confidence:.2f} -> {fallback_conf:.2f} | Text: '{fallback_text}'"
                    )
                    region.text = fallback_text
                    region.confidence = fallback_conf
                    region.fallback_triggered = True
                    region.fallback_model = self.got_fallback.model_name
                    stats["improvements_count"] += 1
                else:
                    logger.info(f"Fallback did not improve confidence. Retaining primary VLM result for Region #{region.region_id}.")

                recovered_regions.append(region)

            stats["mean_confidence"] = round(conf_sum / max(1, len(regions)), 4)
            logger.info(
                f"Confidence evaluation complete: {stats['high_confidence_count']}/{stats['total_regions']} high confidence, "
                f"{stats['fallback_invocations']} fallback retries, {stats['improvements_count']} improved."
            )
            return recovered_regions, stats
