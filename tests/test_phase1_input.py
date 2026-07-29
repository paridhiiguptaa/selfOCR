import os
import pytest
import numpy as np
from PIL import Image
from src.ocr_pipeline.config import PipelineConfig
from src.ocr_pipeline.modules.input_handler import InputHandler

def test_input_handler_image_loading(tmp_path):
    # Create test image
    img_path = os.path.join(str(tmp_path), "test.png")
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    img.save(img_path)

    handler = InputHandler()
    assert handler.is_supported(img_path) is True

    pages = handler.load_document(img_path)
    assert len(pages) == 1
    assert pages[0].width == 200
    assert pages[0].height == 100
    assert pages[0].is_pdf is False
    assert isinstance(pages[0].image, np.ndarray)

def test_unsupported_file_raises_error(tmp_path):
    invalid_file = os.path.join(str(tmp_path), "invalid_file.xyz")
    with open(invalid_file, "w") as f:
        f.write("test")
    handler = InputHandler()
    assert handler.is_supported(invalid_file) is False
    with pytest.raises(ValueError):
        handler.load_document(invalid_file)

