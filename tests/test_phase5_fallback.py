import numpy as np
from src.ocr_pipeline.config import PipelineConfig
from src.ocr_pipeline.modules.confidence_evaluator import ConfidenceEvaluator
from src.ocr_pipeline.models import TextRegion

def test_confidence_evaluator_and_fallback():
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    regions = [
        TextRegion(region_id=1, bbox=(10, 10, 100, 50), text="High Conf Text", confidence=0.95),
        TextRegion(region_id=2, bbox=(10, 60, 100, 100), text="Low Conf", confidence=0.40)
    ]

    config = PipelineConfig(min_confidence_threshold=0.75)
    evaluator = ConfidenceEvaluator(config)

    recovered_regions, stats = evaluator.evaluate_and_recover(img, regions)

    assert stats["total_regions"] == 2
    assert stats["high_confidence_count"] == 1
    assert stats["fallback_invocations"] == 1
    assert len(recovered_regions) == 2
