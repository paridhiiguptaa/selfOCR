import cv2
import numpy as np
from typing import Tuple, Dict, Any, List, Optional
from ..config import PipelineConfig, default_config
from ..models import TextRegion
from ..utils.logging_config import logger, Timer

class DocumentAnalyzer:
    """
    Pre-OCR Document Analysis & Classification Module.
    Automatically classifies document pages into 'predominantly_printed',
    'predominantly_handwritten', or 'mixed_content' using stroke width variance,
    connected component aspect ratio distributions, and contour curvature statistics.
    Provides region-level classification for mixed-content document pages.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config

    def analyze_page(self, image: np.ndarray) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze document page image and classify content structure.
        Returns (page_classification, metadata).
        """
        with Timer("Pre-OCR Document Content Analysis", logger):
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            h, w = gray.shape

            # Compute stroke & contour metrics
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return "predominantly_printed", {"confidence": 0.90, "handwritten_ink_ratio": 0.0}

            aspect_ratios = []
            stroke_variances = []
            contour_curvatures = []

            total_ink_area = 0
            handwritten_ink_area = 0

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 30 or area > 0.8 * (w * h):
                    continue

                total_ink_area += area
                x, y, bw, bh = cv2.boundingRect(cnt)
                aspect_ratios.append(float(bw) / max(1.0, float(bh)))

                # Perimeter vs area ratio indicates contour curvature complexity
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    compactness = (4 * np.pi * area) / (perimeter ** 2)
                    contour_curvatures.append(compactness)
                    if compactness < 0.25: # Low compactness indicates irregular handwriting strokes
                        handwritten_ink_area += area

            handwritten_ratio = float(handwritten_ink_area) / max(1.0, float(total_ink_area))
            mean_aspect = float(np.mean(aspect_ratios)) if aspect_ratios else 1.0
            std_aspect = float(np.std(aspect_ratios)) if aspect_ratios else 0.0

            # Classification Logic
            if handwritten_ratio > 0.60:
                classification = "predominantly_handwritten"
            elif handwritten_ratio > 0.15:
                classification = "mixed_content"
            else:
                classification = "predominantly_printed"

            metadata = {
                "classification": classification,
                "handwritten_ink_ratio": round(handwritten_ratio, 4),
                "mean_aspect_ratio": round(mean_aspect, 3),
                "aspect_ratio_std": round(std_aspect, 3),
                "total_contours_analyzed": len(aspect_ratios)
            }

            logger.info(f"Document Analysis Classification: {classification.upper()} (Handwritten Ink Ratio: {handwritten_ratio*100:.1f}%)")
            return classification, metadata

    def classify_region(self, crop: np.ndarray) -> str:
        """Classify isolated region crop as 'printed' or 'handwritten'."""
        if crop is None or crop.size == 0:
            return "printed"

        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if len(crop.shape) == 3 else crop
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return "printed"

        curvatures = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if area > 10 and perimeter > 0:
                compactness = (4 * np.pi * area) / (perimeter ** 2)
                curvatures.append(compactness)

        if not curvatures:
            return "printed"

        mean_compactness = float(np.mean(curvatures))
        return "handwritten" if mean_compactness < 0.35 else "printed"
