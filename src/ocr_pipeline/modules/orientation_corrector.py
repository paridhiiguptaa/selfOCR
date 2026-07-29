import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
from ..utils.logging_config import logger, Timer

class OrientationCorrector:
    """
    Handles automatic orientation detection (0, 90, 180, 270 degrees),
    fine-angle deskewing, and 4-corner perspective distortion correction.
    """

    def __init__(self, enable_perspective: bool = True):
        self.enable_perspective = enable_perspective

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Detect and correct orientation, deskew, and optionally fix perspective distortion.
        Returns corrected RGB image and a dictionary of applied transformations.
        """
        metadata = {
            "rotation_angle": 0,
            "skew_angle": 0.0,
            "perspective_corrected": False
        }

        with Timer("Orientation & Geometry Correction", logger):
            # Step 1: Detect and correct coarse orientation (0, 90, 180, 270)
            oriented_img, rotation_angle = self.correct_coarse_orientation(image)
            metadata["rotation_angle"] = rotation_angle

            # Step 2: Detect and correct fine skew angle
            deskewed_img, skew_angle = self.correct_fine_skew(oriented_img)
            metadata["skew_angle"] = skew_angle

            # Step 3: Perspective correction (if quadrilateral document boundary found)
            final_img = deskewed_img
            if self.enable_perspective:
                rectified_img, applied_perspective = self.correct_perspective(deskewed_img)
                metadata["perspective_corrected"] = applied_perspective
                final_img = rectified_img

        return final_img, metadata

    def detect_coarse_orientation(self, image: np.ndarray) -> int:
        """
        Detect image orientation (0, 90, 180, or 270 degrees) using normalized projection profile analysis.
        Aspect-ratio invariant to prevent false positive 90° rotations on tall/wide images.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image.copy()
        
        scores = {}
        for angle in [0, 90, 180, 270]:
            if angle == 0:
                rotated = gray
            elif angle == 90:
                rotated = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                rotated = cv2.rotate(gray, cv2.ROTATE_180)
            elif angle == 270:
                rotated = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Apply Otsu binarization
            _, thresh = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Normalize projection profile by width to be aspect-ratio invariant
            rot_h, rot_w = thresh.shape
            h_proj = np.sum(thresh, axis=1) / float(rot_w)
            
            # Calculate variance of difference between adjacent rows (text line periodicity)
            h_diff_var = np.var(np.diff(h_proj))
            scores[angle] = float(h_diff_var)

        score_0 = scores[0]
        best_angle = 0
        max_score = score_0

        for angle in [90, 180, 270]:
            # Require candidate angle score to be at least 35% higher than 0° score to rotate
            if scores[angle] > 1.35 * score_0 and scores[angle] > max_score:
                max_score = scores[angle]
                best_angle = angle

        logger.info(f"Coarse orientation detected: {best_angle}° (Scores: 0°={scores[0]:.4f}, 90°={scores[90]:.4f}, 180°={scores[180]:.4f}, 270°={scores[270]:.4f})")
        return best_angle

    def correct_coarse_orientation(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """Rotate image by detected orientation angle (0, 90, 180, or 270 degrees)."""
        angle = self.detect_coarse_orientation(image)
        if angle == 0:
            return image.copy(), 0
        elif angle == 90:
            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated = image.copy()
            
        logger.info(f"Applied coarse rotation: {angle}°")
        return rotated, angle

    def detect_skew_angle(self, image: np.ndarray) -> float:
        """
        Detect fine skew angle in degrees (-45° to +45°) using Hough line angles
        and minimum area bounding boxes of text contours.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image.copy()
        
        # Binarize and invert
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Find Hough lines
        edges = cv2.Canny(dilated, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
        
        angles = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 == 0:
                    continue
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                # Only consider near-horizontal text line angles (-30 to +30 degrees)
                if -30.0 <= angle <= 30.0:
                    angles.append(angle)

        if len(angles) >= 5:
            skew_angle = float(np.median(angles))
        else:
            # Fallback to MinAreaRect on large contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            rect_angles = []
            for cnt in contours:
                if cv2.contourArea(cnt) > 100:
                    rect = cv2.minAreaRect(cnt)
                    angle = rect[-1]
                    if angle < -45:
                        angle = 90 + angle
                    elif angle > 45:
                        angle = angle - 90
                    if -30.0 <= angle <= 30.0 and abs(angle) > 0.1:
                        rect_angles.append(angle)
            skew_angle = float(np.median(rect_angles)) if rect_angles else 0.0

        return skew_angle

    def correct_fine_skew(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Deskew image by fine angle."""
        angle = self.detect_skew_angle(image)
        # Skip if skew is negligible (< 0.35 degrees)
        if abs(angle) < 0.35:
            logger.info(f"Deskew skipped (skew angle {angle:.2f}° is negligible)")
            return image.copy(), 0.0

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Determine canvas size to avoid clipping during rotation
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        deskewed = cv2.warpAffine(
            image, M, (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )
        logger.info(f"Applied deskew correction: {angle:.2f}°")
        return deskewed, angle

    def correct_perspective(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Detect quadrilateral document boundaries and rectify perspective.
        Returns transformed image and boolean indicating if perspective transformation was applied.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image.copy()
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)
        
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image.copy(), False

        # Sort contours by area descending
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        doc_cnt = None

        for cnt in contours[:5]:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # If quadrilateral contour found with significant area relative to image
            if len(approx) == 4 and cv2.contourArea(cnt) > 0.20 * (w * h):
                doc_cnt = approx
                break

        if doc_cnt is None:
            return image.copy(), False

        # Order 4 corners: top-left, top-right, bottom-right, bottom-left
        pts = doc_cnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)] # top-left
        rect[2] = pts[np.argmax(s)] # bottom-right
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)] # top-right
        rect[3] = pts[np.argmax(diff)] # bottom-left

        (tl, tr, br, bl) = rect
        # Compute maximum width and height
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight), flags=cv2.INTER_CUBIC)
        logger.info(f"Applied perspective rectification (Output Size: {maxWidth}x{maxHeight})")
        return warped, True
