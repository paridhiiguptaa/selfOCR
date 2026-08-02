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
            kernel_len = max(20, w // 12)
            horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))

            # Otsu binarization for dark ink / pencil strokes on light background
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Isolate horizontal lines
            detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel, iterations=1)

            # 2. Isolate vertical/diagonal text strokes to prevent line removal from eroding letters
            vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            vert_strokes = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vert_kernel, iterations=1)

            # Line mask removing points that are part of strong vertical strokes
            line_mask = cv2.subtract(detected_lines, vert_strokes)

            if np.count_nonzero(line_mask) == 0:
                return crop.copy()

            # 3. Use inpainting to restore line intersections smoothly without leaving white holes in letters
            dilated_mask = cv2.dilate(line_mask, np.ones((2, 1), np.uint8), iterations=1)
            
            if len(crop.shape) == 3:
                cleaned = cv2.inpaint(crop, dilated_mask, 2, cv2.INPAINT_TELEA)
            else:
                cleaned = cv2.inpaint(crop, dilated_mask, 2, cv2.INPAINT_TELEA)

            return cleaned
        except Exception as e:
            logger.warning(f"Notebook line removal warning: {e}")
            return crop.copy()
