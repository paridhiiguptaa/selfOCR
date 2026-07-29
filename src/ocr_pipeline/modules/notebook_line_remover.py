import cv2
import numpy as np
from typing import Tuple
from ..utils.logging_config import logger

class NotebookLineRemover:
    """
    Suppresses horizontal notebook ruling lines (blue/red lines) from handwritten document crops,
    preventing line intersections from corrupting handwritten character recognition.
    """

    def remove_lines(self, crop: np.ndarray) -> np.ndarray:
        """
        Detect and suppress thin horizontal ruled lines in notebook crops.
        Returns line-suppressed RGB image.
        """
        if crop is None or crop.size == 0:
            return crop

        h, w = crop.shape[:2]
        if h < 10 or w < 10:
            return crop.copy()

        try:
            gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if len(crop.shape) == 3 else crop.copy()

            # 1. Detect thin horizontal lines using long horizontal morphological kernel
            kernel_len = max(15, w // 15)
            horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))

            # Otsu binarization
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Isolate horizontal lines
            detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel, iterations=1)

            # 2. Subtract detected lines slightly diluted to leave text strokes intact
            dilated_lines = cv2.dilate(detected_lines, np.ones((2, 2), np.uint8), iterations=1)

            # Inpaint or replace line pixels with background lightness
            cleaned = crop.copy()
            cleaned[dilated_lines > 0] = [255, 255, 255] if len(crop.shape) == 3 else 255

            return cleaned
        except Exception as e:
            logger.warning(f"Notebook line removal warning: {e}")
            return crop.copy()
