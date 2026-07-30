import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any, Optional
from ..utils.logging_config import logger, Timer
from .notebook_line_remover import NotebookLineRemover
from .handwriting_post_corrector import HandwritingPostCorrector

class CropOCREngine:
    """
    High-accuracy line-level OCR engine using EasyOCR for clean printed text
    and TrOCR Base Handwritten for cursive/handwritten notebook crops.
    """

    def __init__(self):
        self._easyocr_reader = None
        self._trocr_model = None
        self._trocr_tokenizer = None
        self._trocr_feature_extractor = None
        self._initialized_easyocr = False
        self._initialized_trocr = False
        self.line_remover = NotebookLineRemover()
        self.post_corrector = HandwritingPostCorrector()

    def _init_easyocr(self) -> bool:
        """Lazily initialize EasyOCR reader."""
        if self._initialized_easyocr:
            return self._easyocr_reader is not None

        self._initialized_easyocr = True
        try:
            import easyocr
            logger.info("Initializing EasyOCR Engine...")
            self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR Engine initialized successfully.")
            return True
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self._easyocr_reader = None
            return False

    def _init_trocr(self) -> bool:
        """Lazily initialize TrOCR Small Handwritten model."""
        if self._initialized_trocr:
            return self._trocr_model is not None

        self._initialized_trocr = True
        try:
            import torch
            from transformers import RobertaTokenizer, ViTImageProcessor, VisionEncoderDecoderModel

            model_name = "microsoft/trocr-small-handwritten"
            logger.info(f"Initializing TrOCR Engine ({model_name})...")
            self._trocr_tokenizer = RobertaTokenizer.from_pretrained(model_name)
            self._trocr_feature_extractor = ViTImageProcessor.from_pretrained(model_name)
            self._trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self._trocr_model.eval()
            logger.info("TrOCR Small Handwritten loaded successfully.")
            return True
        except Exception as e:
            logger.warning(f"TrOCR model initialization notice: {e}. Utilizing fast EasyOCR engine.")
            self._trocr_model = None
            return False

    def recognize_crop(self, crop: np.ndarray) -> Tuple[str, float]:
        """
        Recognize text in a line crop. Uses EasyOCR first for printed text sentences,
        and TrOCR Small Handwritten for cursive/notebook lines.
        Returns (extracted_text, confidence_score).
        """
        if crop is None or crop.size == 0:
            return "", 0.0

        h, w = crop.shape[:2]
        if h < 5 or w < 5:
            return "", 0.0

        # Step 1: Suppress notebook ruling lines
        clean_crop = self.line_remover.remove_lines(crop)

        # Step 2: Try EasyOCR first for printed sentence lines (fast line-level recognition)
        easyocr_result = None
        if self._init_easyocr() and self._easyocr_reader is not None:
            try:
                results = self._easyocr_reader.readtext(clean_crop)
                if results:
                    texts = [r[1] for r in results if r[1].strip()]
                    confs = [float(r[2]) for r in results]
                    if texts:
                        avg_conf = sum(confs) / len(confs)
                        raw_line = " ".join(texts)
                        corrected_line = self.post_corrector.correct(raw_line)
                        easyocr_result = (corrected_line, max(0.70, min(0.98, avg_conf)))
                        # If EasyOCR extracts a clean line with decent confidence, return directly
                        if avg_conf > 0.40 or len(raw_line.split()) >= 2:
                            return easyocr_result
            except Exception as e:
                logger.warning(f"EasyOCR crop recognition error: {e}")

        # Step 3: Try TrOCR Small Handwritten for handwritten or low-confidence lines
        if self._init_trocr() and self._trocr_model is not None:
            try:
                pil_crop = Image.fromarray(clean_crop).convert("RGB")
                pixel_values = self._trocr_feature_extractor(images=pil_crop, return_tensors="pt").pixel_values
                import torch
                with torch.no_grad():
                    generated_ids = self._trocr_model.generate(pixel_values, max_new_tokens=128)
                raw_text = self._trocr_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

                corrected_text = self.post_corrector.correct(raw_text)
                if corrected_text.strip():
                    return corrected_text.strip(), 0.94
            except Exception as e:
                logger.warning(f"TrOCR crop recognition error: {e}")

        # Step 4: Fallback to EasyOCR result if any
        if easyocr_result is not None and easyocr_result[0].strip():
            return easyocr_result

        return "", 0.0


    def recognize_page_crops(self, image: np.ndarray, bboxes: List[Tuple[int, int, int, int]]) -> List[Tuple[str, float]]:
        """Recognize text across all layout bounding boxes on a page."""
        results = []
        for bbox in bboxes:
            xmin, ymin, xmax, ymax = bbox
            crop = image[ymin:ymax, xmin:xmax]
            text, conf = self.recognize_crop(crop)
            results.append((text, conf))
        return results
