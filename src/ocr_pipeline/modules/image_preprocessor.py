import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional

from ..config import PipelineConfig, default_config
from ..utils.logging_config import logger, Timer

class ImagePreprocessor:
    """
    Quality evaluation, shadow removal, noise reduction, CLAHE contrast enhancement,
    border removal, and intelligent clean skip mechanism.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Preprocess image to maximize OCR text readability while preserving natural contrast.
        Returns preprocessed RGB image and metadata dictionary.
        """
        metadata = {
            "skipped": False,
            "denoised": False,
            "clahe_applied": False,
            "shadow_removed": False,
            "border_removed": False,
            "quality_metrics": {}
        }

        with Timer("Image Quality Preprocessing", logger):
            metrics = self.evaluate_quality(image)
            metadata["quality_metrics"] = metrics
            logger.info(f"Quality Metrics: Contrast={metrics['contrast']:.2f}, Noise={metrics['noise_std']:.2f}, Mean Brightness={metrics['brightness_mean']:.2f}")

            # Intelligent Skip: If image is already crisp, low noise, and good contrast
            if self.config.smart_skip_clean_images and self.should_skip(metrics):
                logger.info("Image identified as high quality. Skipping aggressive preprocessing.")
                metadata["skipped"] = True
                return image.copy(), metadata

            output_img = image.copy()

            # Step 1: Border / Margin Removal
            output_img, border_applied = self.remove_black_borders(output_img)
            metadata["border_removed"] = border_applied

            # Step 2: Shadow removal if illumination variance is high
            if metrics["brightness_std"] > 45.0:
                output_img = self.remove_shadows(output_img)
                metadata["shadow_removed"] = True

            # Step 3: Edge-preserving Denoising if noise is detected
            if metrics["noise_std"] > 10.0:
                output_img = self.denoise(output_img)
                metadata["denoised"] = True

            # Step 4: Contrast Enhancement using CLAHE on L-channel of LAB
            if metrics["contrast"] < 65.0:
                output_img = self.enhance_contrast_clahe(output_img)
                metadata["clahe_applied"] = True

            # Step 5: Stroke Sharpening via Unsharp Masking
            if self.config.enable_unsharp_mask:
                output_img = self.sharpen_unsharp_mask(output_img, amount=self.config.unsharp_amount)
                metadata["unsharp_mask_applied"] = True

        return output_img, metadata

    def sharpen_unsharp_mask(self, image: np.ndarray, amount: float = 1.5, sigma: float = 1.0) -> np.ndarray:
        """Sharpen fine strokes using unsharp masking while preserving grayscale detail."""
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def adaptive_resample_crop(self, crop: np.ndarray, target_height: Optional[int] = None, add_margin: bool = True) -> np.ndarray:
        """Lanczos adaptive upscaling for low-height line crops to improve character recognizer legibility, with border padding."""
        if crop is None or crop.size == 0:
            return crop

        th = target_height or self.config.target_crop_height_px
        h, w = crop.shape[:2]
        if h < 5 or w < 5:
            return crop

        # Add light margin padding around handwritten crops so descenders/ascenders/edge characters are preserved
        if add_margin:
            pad_v = max(4, int(h * 0.12))
            pad_h = max(6, int(w * 0.05))
            if len(crop.shape) == 3:
                crop = cv2.copyMakeBorder(crop, pad_v, pad_v, pad_h, pad_h, cv2.BORDER_CONSTANT, value=[255, 255, 255])
            else:
                crop = cv2.copyMakeBorder(crop, pad_v, pad_v, pad_h, pad_h, cv2.BORDER_CONSTANT, value=255)
            h, w = crop.shape[:2]

        if h >= th:
            return crop

        scale = th / float(h)
        new_w = max(1, int(round(w * scale)))
        new_h = th

        return cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    def evaluate_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Calculate image quality metrics: contrast, noise level, and brightness statistics."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        
        contrast = float(np.std(gray))
        brightness_mean = float(np.mean(gray))
        brightness_std = float(np.std(gray))

        # Robust high-frequency noise estimate (residual between image and median blur)
        blurred = cv2.medianBlur(gray, 3)
        diff = cv2.absdiff(gray, blurred)
        # Median absolute deviation of noise residual
        noise_std = float(np.median(diff))

        return {
            "contrast": contrast,
            "brightness_mean": brightness_mean,
            "brightness_std": brightness_std,
            "noise_std": noise_std
        }

    def should_skip(self, metrics: Dict[str, float]) -> bool:
        """Determine if preprocessing should be skipped for clean documents."""
        is_good_contrast = metrics["contrast"] >= 50.0
        is_low_noise = metrics["noise_std"] <= 25.0
        is_good_brightness = 40.0 <= metrics["brightness_mean"] <= 235.0
        return is_good_contrast and is_low_noise and is_good_brightness

    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """Correct non-uniform illumination and shadows using morphological background estimation."""
        rgb_planes = cv2.split(image)
        result_planes = []

        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(norm_img)

        logger.info("Applied illumination & shadow normalization.")
        return cv2.merge(result_planes)

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Apply edge-preserving bilateral filter to eliminate high-frequency noise."""
        denoised = cv2.bilateralFilter(image, d=5, sigmaColor=50, sigmaSpace=50)
        logger.info("Applied edge-preserving bilateral noise filter.")
        return denoised

    def enhance_contrast_clahe(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE on Lightness channel in LAB color space."""
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(
            clipLimit=self.config.contrast_clahe_clip_limit,
            tileGridSize=self.config.contrast_clahe_tile_grid
        )
        cl = clahe.apply(l)

        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        logger.info("Applied CLAHE contrast enhancement.")
        return enhanced

    def remove_black_borders(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Detect and crop artificial black margins from scanned documents."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        h, w = gray.shape

        # Threshold black margins (pixels < 25)
        _, black_mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return image, False

        # Find maximum bounding box containing document content
        largest_cnt = max(contours, key=cv2.contourArea)
        x, y, bw, bh = cv2.boundingRect(largest_cnt)

        # Apply crop if border removal trims at least 2% of black margin
        if bw * bh > 0.85 * (w * h) and (x > 0 or y > 0 or bw < w or bh < h):
            cropped = image[y:y+bh, x:x+bw]
            logger.info(f"Cropped document scan margins: ({x}, {y}, {bw}, {bh})")
            return cropped, True

        return image, False
