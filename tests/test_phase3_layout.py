import cv2
import numpy as np
from src.ocr_pipeline.modules.surya_layout_analyzer import SuryaLayoutAnalyzer
from src.ocr_pipeline.models import TextRegion

def test_surya_layout_analyzer():
    img = np.full((500, 600, 3), 255, dtype=np.uint8)
    cv2.putText(img, "DOCUMENT TITLE", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
    cv2.putText(img, "Section Header 1", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    cv2.putText(img, "This is paragraph text in the body of the document.", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    analyzer = SuryaLayoutAnalyzer()
    regions, meta = analyzer.analyze(img)

    assert isinstance(regions, list)
    assert len(regions) > 0
    assert "engine" in meta
    assert isinstance(regions[0], TextRegion)
