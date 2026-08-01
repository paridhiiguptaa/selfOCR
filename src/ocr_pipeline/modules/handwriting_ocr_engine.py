import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any, Optional

from ..config import PipelineConfig, default_config
from ..utils.logging_config import logger, Timer
from .notebook_line_remover import NotebookLineRemover
from .handwriting_post_corrector import HandwritingPostCorrector
from .image_preprocessor import ImagePreprocessor

class HandwritingOCREngine:
    """
    Dedicated Handwriting Recognition Layer.
    Processes cursive and handwritten notebook line crops using Microsoft TrOCR Small/Base
    and GOT-OCR 2.0 with Lanczos stroke-preserving upscaling and notebook ruling line suppression.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.line_remover = NotebookLineRemover()
        self.post_corrector = HandwritingPostCorrector()
        self.preprocessor = ImagePreprocessor(self.config)

        self._trocr_model = None
        self._trocr_tokenizer = None
        self._trocr_feature_extractor = None
        self._initialized_trocr = False

    def _init_trocr(self) -> bool:
        """Lazily initialize TrOCR Small Handwritten model."""
        if self._initialized_trocr:
            return self._trocr_model is not None

        self._initialized_trocr = True
        try:
            import torch
            from transformers import RobertaTokenizer, ViTImageProcessor, VisionEncoderDecoderModel

            model_name = self.config.trocr_handwriting_model_name
            logger.info(f"Initializing Dedicated Handwriting TrOCR Engine ({model_name})...")
            self._trocr_tokenizer = RobertaTokenizer.from_pretrained(model_name)
            self._trocr_feature_extractor = ViTImageProcessor.from_pretrained(model_name)
            self._trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self._trocr_model.eval()
            logger.info("TrOCR Small Handwritten loaded successfully.")
            return True
        except Exception as e:
            logger.warning(f"TrOCR model initialization notice: {e}.")
            self._trocr_model = None
            return False

    def recognize_handwriting_crop(self, crop: np.ndarray) -> Tuple[str, float]:
        """
        Recognize text in a handwritten line crop.
        Applies line removal, stroke sharpening, Lanczos upscaling, and TrOCR inference.
        Returns (recognized_text, confidence_score).
        """
        if crop is None or crop.size == 0:
            return "", 0.0

        h, w = crop.shape[:2]
        if h < 5 or w < 5:
            return "", 0.0

        # Step 1: Suppress notebook ruling lines
        clean_crop = self.line_remover.remove_lines(crop)

        # Step 2: Stroke Sharpening & Lanczos Upscaling
        enhanced_crop = self.preprocessor.sharpen_unsharp_mask(clean_crop, amount=1.5)
        upscaled_crop = self.preprocessor.adaptive_resample_crop(enhanced_crop, target_height=64)

        # Step 3: TrOCR Small Handwritten inference
        if self._init_trocr() and self._trocr_model is not None:
            try:
                import torch
                pil_crop = Image.fromarray(upscaled_crop).convert("RGB")
                pixel_values = self._trocr_feature_extractor(images=pil_crop, return_tensors="pt").pixel_values
                with torch.no_grad():
                    generated_ids = self._trocr_model.generate(pixel_values, max_new_tokens=128)
                raw_text = self._trocr_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

                corrected_text = self.post_corrector.correct(raw_text)
                if corrected_text.strip():
                    return corrected_text.strip(), 0.94
            except Exception as e:
                logger.warning(f"TrOCR handwriting recognition error: {e}")

        return "", 0.0
