import cv2
import numpy as np
from src.ocr_pipeline.modules.orientation_corrector import OrientationCorrector
from src.ocr_pipeline.modules.image_preprocessor import ImagePreprocessor

def test_orientation_and_deskew():
    # Create test image with horizontal lines
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    cv2.putText(img, "TEST DOCUMENT TEXT", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    corrector = OrientationCorrector()
    corrected_img, meta = corrector.process(img)

    assert "rotation_angle" in meta
    assert "skew_angle" in meta
    assert isinstance(corrected_img, np.ndarray)

def test_image_preprocessor():
    img = np.full((300, 400, 3), 200, dtype=np.uint8)
    cv2.putText(img, "SAMPLE PREPROCESSING TEST", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (10, 10, 10), 2)

    preprocessor = ImagePreprocessor()
    processed_img, meta = preprocessor.process(img)

    assert isinstance(processed_img, np.ndarray)
    assert "quality_metrics" in meta
