import pytest
import numpy as np
from src.ocr_pipeline.modules.surya_layout_analyzer import SuryaLayoutAnalyzer
from src.ocr_pipeline.models import TextRegion
from src.ocr_pipeline.config import PipelineConfig

def test_paragraph_grouping():
    cfg = PipelineConfig(enable_paragraph_grouping=True)
    analyzer = SuryaLayoutAnalyzer(cfg)

    regions = [
        TextRegion(region_id=1, bbox=(20, 20, 300, 45), region_type="Text"),
        TextRegion(region_id=2, bbox=(20, 52, 320, 77), region_type="Text"),
        TextRegion(region_id=3, bbox=(20, 150, 280, 175), region_type="Text")
    ]

    grouped = analyzer.group_lines_into_paragraphs(regions)
    assert len(grouped) == 3
    # Region 1 and 2 should be in paragraph 1, region 3 in paragraph 2
    assert grouped[0].paragraph_id == 1
    assert grouped[1].paragraph_id == 1
    assert grouped[2].paragraph_id == 2
