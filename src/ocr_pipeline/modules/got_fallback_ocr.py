import torch
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional

from ..config import PipelineConfig, default_config
from .crop_ocr_engine import CropOCREngine
from ..utils.logging_config import logger, Timer

class GOTFallbackOCR:
    """
    Automatic fallback OCR engine using GOT-OCR 2.0 (stepfun-ai/GOT-OCR2_0).
    Reprocesses low-confidence or difficult handwritten regions identified by primary VLM.
    Includes real crop-level OCR fallback for low-memory CPU environments.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.model_name = self.config.got_fallback_model_name
        self.device = self.config.device
        self._model = None
        self._tokenizer = None
        self._initialized = False
        self._crop_engine = CropOCREngine()

    def _init_model(self) -> bool:
        """Lazily initialize GOT-OCR 2.0 model on CUDA GPU."""
        if self._initialized:
            return self._model is not None

        self._initialized = True
        if self.device != "cuda" or not torch.cuda.is_available():
            logger.info("Execution device is CPU. Utilizing fast Crop OCR engine for fallback.")
            self._model = None
            self._tokenizer = None
            return False

        try:
            from transformers import AutoModel, AutoTokenizer

            logger.info(f"Loading GOT-OCR 2.0 model '{self.model_name}' on CUDA...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self._model = AutoModel.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            self._model.eval()

            logger.info("GOT-OCR 2.0 loaded successfully on CUDA.")
            return True
        except Exception as e:
            logger.warning(f"Failed to load GOT-OCR 2.0 model '{self.model_name}': {e}. Utilizing Crop OCR fallback.")
            self._model = None
            self._tokenizer = None
            return False

    def reprocess_region(self, crop: np.ndarray) -> Tuple[str, float]:
        """
        Reprocess isolated low-confidence region crop using GOT-OCR 2.0 or Crop OCR Engine.
        Returns (text, confidence score).
        """
        if crop is None or crop.size == 0:
            return "", 0.0

        with Timer("GOT-OCR 2.0 Fallback Region Reprocessing", logger):
            if self._init_model() and self._model is not None:
                try:
                    pil_crop = Image.fromarray(crop)
                    res = self._model.chat(self._tokenizer, pil_crop, ocr_type='ocr')
                    res_text = res.strip() if isinstance(res, str) else str(res)
                    confidence = 0.94 if len(res_text) > 0 else 0.50
                    logger.info(f"GOT-OCR 2.0 reprocessed region result: '{res_text}' (Conf: {confidence:.2f})")
                    return res_text, confidence
                except Exception as e:
                    logger.warning(f"GOT-OCR 2.0 inference exception: {e}")

            # Real OCR crop engine fallback
            return self._crop_engine.recognize_crop(crop)
