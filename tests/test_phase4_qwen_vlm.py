import numpy as np
from src.ocr_pipeline.modules.qwen_vlm_ocr import QwenVLMOCR
from src.ocr_pipeline.models import TextRegion

def test_qwen_vlm_ocr():
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    layout_regions = [
        TextRegion(region_id=1, bbox=(50, 20, 350, 70), region_type="Title"),
        TextRegion(region_id=2, bbox=(50, 100, 350, 250), region_type="Text")
    ]

    qwen = QwenVLMOCR()
    full_md, regions, meta = qwen.transcribe_page(img, layout_regions)

    assert isinstance(full_md, str)
    assert isinstance(regions, list)
    assert len(regions) == 2
    assert "model" in meta
