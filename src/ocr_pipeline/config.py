import os
import torch
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class PipelineConfig:
    """Central configuration for VLM-first OCR pipeline stages."""
    
    # Input & Rendering
    pdf_render_dpi: int = 300
    supported_extensions: Tuple[str, ...] = (
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".pdf"
    )
    
    # Preprocessing
    enable_orientation_correction: bool = True
    enable_deskew: bool = True
    enable_perspective_correction: bool = True
    enable_quality_enhancement: bool = True
    smart_skip_clean_images: bool = True
    contrast_clahe_clip_limit: float = 2.0
    contrast_clahe_tile_grid: Tuple[int, int] = (8, 8)
    
    # Layout Analysis (Surya OCR)
    enable_surya_layout: bool = True
    surya_batch_size: int = 4
    
    # Primary VLM OCR Engine (Qwen2.5-VL)
    qwen_model_name: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    qwen_max_new_tokens: int = 1024
    
    # Fallback OCR Engine (GOT-OCR 2.0)
    got_fallback_model_name: str = "stepfun-ai/GOT-OCR2_0"
    enable_got_fallback: bool = True
    
    # Confidence & Fallback Thresholds
    min_confidence_threshold: float = 0.75
    max_fallback_retries: int = 2
    
    # Execution Device & Precision
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype: str = "float16" if torch.cuda.is_available() else "float32"
    
    # Output & Debug
    output_dir: str = "output"
    save_debug_images: bool = True
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.pdf_render_dpi < 72:
            raise ValueError("pdf_render_dpi must be at least 72")
        if not (0.0 <= self.min_confidence_threshold <= 1.0):
            raise ValueError("min_confidence_threshold must be between 0.0 and 1.0")

default_config = PipelineConfig()

