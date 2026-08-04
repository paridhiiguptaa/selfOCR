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
    
    # Preprocessing & Stroke Preservation
    enable_orientation_correction: bool = True
    enable_deskew: bool = True
    enable_perspective_correction: bool = True
    enable_quality_enhancement: bool = True
    smart_skip_clean_images: bool = True
    contrast_clahe_clip_limit: float = 2.0
    contrast_clahe_tile_grid: Tuple[int, int] = (8, 8)
    enable_unsharp_mask: bool = True
    unsharp_amount: float = 1.5
    enable_adaptive_crop_upscaling: bool = True
    target_crop_height_px: int = 64
    
    # Document Analysis & Content Classification
    enable_document_analysis: bool = True
    min_ink_density: float = 0.015            # Filter out empty background bounding boxes (< 1.5% ink)
    
    # Layout Analysis & Bounding Box Padding (Surya / Geometric)
    enable_surya_layout: bool = True
    surya_batch_size: int = 4
    bbox_padding_vertical_ratio: float = 0.18  # 18% vertical padding to preserve ascenders/descenders
    bbox_padding_horizontal_ratio: float = 0.08 # 8% horizontal padding
    bbox_min_padding_px: int = 6               # Minimum 6px padding around all crops
    
    # Primary VLM OCR Engine (Qwen2.5-VL)
    qwen_model_name: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    qwen_max_new_tokens: int = 1024
    
    # Dedicated Handwriting & Fallback OCR Engines (TrOCR & GOT-OCR 2.0)
    trocr_handwriting_model_name: str = "microsoft/trocr-small-handwritten"
    got_fallback_model_name: str = "stepfun-ai/GOT-OCR2_0"
    enable_got_fallback: bool = False
    
    # Quality Estimator & Calibration Thresholds
    min_quality_score_threshold: float = 0.50 # Multi-factor quality threshold
    min_confidence_threshold: float = 0.60
    word_confidence_threshold: float = 0.70
    max_fallback_retries: int = 2
    
    # Context-Aware Proofreading (Decoupled - user triggered via 'Show Corrections')
    enable_contextual_proofreading: bool = False
    proofreading_transformer_model: str = "distilroberta-base"
    proofreading_regex_timeout_sec: float = 2.0
    
    # Next-Generation Intelligent OCR Architecture Settings
    enable_multiscale_ocr: bool = True
    multiscale_high_confidence_bypass: float = 0.90
    multiscale_max_candidates: int = 8
    
    enable_multi_model_ensemble: bool = True
    enable_vlm_verification: bool = True
    enable_paragraph_grouping: bool = True
    vlm_verification_strictness: float = 0.85

    enable_subject_detection: bool = True
    subject_override: Optional[str] = None
    
    enable_educational_lm: bool = True
    
    enable_handwriting_adaptation: bool = True
    user_profile_dir: str = "src/data/user_profiles"
    default_user_id: str = "default_student"


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


