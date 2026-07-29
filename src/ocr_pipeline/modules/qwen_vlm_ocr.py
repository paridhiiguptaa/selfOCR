import torch
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional

from ..config import PipelineConfig, default_config
from ..models import TextRegion
from .crop_ocr_engine import CropOCREngine
from ..utils.logging_config import logger, Timer

class QwenVLMOCR:
    """
    Primary Vision Language Model (VLM) OCR engine based on Qwen2.5-VL.
    Understands entire document pages, reading order, printed text, handwriting, lists, and tables.
    Includes real crop-level OCR fallback for high accuracy on low-memory/CPU systems.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.model_name = self.config.qwen_model_name
        self.device = self.config.device
        self._model = None
        self._processor = None
        self._initialized = False
        self._crop_engine = CropOCREngine()

    def _init_model(self) -> bool:
        """Lazily initialize Qwen2.5-VL model on CUDA GPU."""
        if self._initialized:
            return self._model is not None

        self._initialized = True

        # Heavy 3B+ VLM weights require CUDA GPU.
        # On CPU-only Windows, use Crop OCR engine to prevent PyTorch C++ safetensors access violations.
        if self.device != "cuda" or not torch.cuda.is_available():
            logger.info("Execution device is CPU. Utilizing fast Crop OCR engine for text extraction.")
            self._model = None
            self._processor = None
            return False

        try:
            from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

            logger.info(f"Loading Qwen2.5-VL model '{self.model_name}' on CUDA...")
            self._processor = AutoProcessor.from_pretrained(self.model_name)
            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            self._model.eval()

            logger.info("Qwen2.5-VL loaded successfully on CUDA.")
            return True
        except Exception as e:
            logger.warning(f"Failed to load Qwen2.5-VL model '{self.model_name}': {e}. Utilizing Crop OCR fallback engine.")
            self._model = None
            self._processor = None
            return False

    def transcribe_page(
        self,
        image: np.ndarray,
        layout_regions: Optional[List[TextRegion]] = None
    ) -> Tuple[str, List[TextRegion], Dict[str, Any]]:
        """
        Transcribe complete document page image using Qwen2.5-VL.
        Integrates layout information from Surya to guide document structure.
        Returns (full_page_markdown, updated_regions, metadata).
        """
        h, w = image.shape[:2]
        metadata = {
            "model": self.model_name if self._model else "crop_ocr_fallback_engine",
            "device": self.device,
            "tokens_generated": 0
        }

        with Timer("Qwen2.5-VL Full Page Transcription", logger):
            pil_img = Image.fromarray(image)

            if self._init_model() and self._model is not None:
                try:
                    from qwen_vl_utils import process_vision_info

                    prompt_text = (
                        "Transcribe all printed and handwritten text in this educational document image into clean Markdown. "
                        "Preserve exact reading order, headings, paragraphs, lists, and tables."
                    )
                    if layout_regions:
                        layout_summary = ", ".join([f"{r.region_type} at box {r.bbox}" for r in layout_regions[:8]])
                        prompt_text += f"\nDocument Layout Regions: {layout_summary}."

                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image", "image": pil_img},
                                {"type": "text", "text": prompt_text}
                            ]
                        }
                    ]

                    text_prompt = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    image_inputs, video_inputs = process_vision_info(messages)

                    inputs = self._processor(
                        text=[text_prompt],
                        images=image_inputs,
                        videos=video_inputs,
                        padding=True,
                        return_tensors="pt"
                    ).to(self.device)

                    with torch.no_grad():
                        generated_ids = self._model.generate(**inputs, max_new_tokens=self.config.qwen_max_new_tokens)
                        generated_ids_trimmed = [
                            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                        ]
                        output_text = self._processor.batch_decode(
                            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                        )[0]

                    metadata["tokens_generated"] = len(generated_ids[0])
                    updated_regions = self._assign_transcription_to_regions(output_text, layout_regions)
                    return output_text, updated_regions, metadata

                except Exception as e:
                    logger.warning(f"Qwen2.5-VL inference error: {e}. Falling back to region-based crop extraction.")

            # Perform REAL text recognition on every image crop
            fallback_text, updated_regions = self._real_crop_transcribe(image, layout_regions)
            return fallback_text, updated_regions, metadata

    def transcribe_crop(self, crop: np.ndarray) -> Tuple[str, float]:
        """Transcribe an isolated image crop. Returns (text, confidence)."""
        if crop is None or crop.size == 0:
            return "", 0.0

        if self._init_model() and self._model is not None:
            try:
                pil_crop = Image.fromarray(crop)
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": pil_crop},
                            {"type": "text", "text": "Transcribe the text in this image crop accurately."}
                        ]
                    }
                ]
                text_prompt = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self._processor(text=[text_prompt], images=[pil_crop], return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    ids = self._model.generate(**inputs, max_new_tokens=128)
                    res = self._processor.batch_decode(ids, skip_special_tokens=True)[0]
                return res.strip(), 0.92
            except Exception as e:
                logger.warning(f"Qwen crop transcription error: {e}")

        # Real OCR crop fallback
        return self._crop_engine.recognize_crop(crop)

    def _assign_transcription_to_regions(
        self,
        full_text: str,
        layout_regions: Optional[List[TextRegion]]
    ) -> List[TextRegion]:
        """Map page transcription lines back to detected layout regions."""
        if not layout_regions:
            return []

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        for idx, region in enumerate(layout_regions):
            if idx < len(lines):
                region.text = lines[idx]
                region.confidence = 0.92
            else:
                region.confidence = 0.80

        return layout_regions

    def _real_crop_transcribe(
        self,
        image: np.ndarray,
        layout_regions: Optional[List[TextRegion]]
    ) -> Tuple[str, List[TextRegion]]:
        """Perform real OCR extraction across all image regions."""
        if not layout_regions:
            h, w = image.shape[:2]
            layout_regions = [TextRegion(region_id=1, bbox=(0, 0, w, h), region_type="Text", confidence=0.88)]

        md_lines = []
        for reg in layout_regions:
            xmin, ymin, xmax, ymax = reg.bbox
            crop = image[ymin:ymax, xmin:xmax]
            text, conf = self._crop_engine.recognize_crop(crop)
            
            if text.strip():
                reg.text = text.strip()
                reg.confidence = conf
            elif not reg.text:
                reg.text = ""
                reg.confidence = 0.50

            if reg.text.strip():
                if reg.region_type == "Title":
                    md_lines.append(f"# {reg.text}")
                elif reg.region_type == "Section-header":
                    md_lines.append(f"## {reg.text}")
                else:
                    md_lines.append(reg.text)

        full_md = "\n\n".join(md_lines)
        return full_md, layout_regions
