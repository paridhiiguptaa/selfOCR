import os
from typing import Union, Tuple, List, Optional
import cv2
import numpy as np
from PIL import Image, ImageOps

def load_image_as_numpy(input_path: str) -> np.ndarray:
    """
    Load an image from disk and return an RGB NumPy array (H, W, 3).
    Handles EXIF orientation tags automatically.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    try:
        pil_img = Image.open(input_path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        return np.array(pil_img)
    except Exception as e:
        # Fallback to OpenCV
        img_bgr = cv2.imread(input_path)
        if img_bgr is None:
            raise ValueError(f"Failed to decode image at {input_path}: {e}")
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def pil_to_numpy(pil_img: Image.Image) -> np.ndarray:
    """Convert a PIL Image to RGB NumPy array."""
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    return np.array(pil_img)

def numpy_to_pil(np_img: np.ndarray) -> Image.Image:
    """Convert an RGB NumPy array to a PIL Image."""
    return Image.fromarray(np_img)

def save_image(img: Union[np.ndarray, Image.Image], output_path: str) -> None:
    """Save an RGB NumPy array or PIL Image to disk."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    if isinstance(img, np.ndarray):
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, bgr)
    elif isinstance(img, Image.Image):
        img.save(output_path)
    else:
        raise TypeError("img must be a numpy.ndarray or PIL.Image.Image")

def crop_box(img: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop region from RGB image given bounding box (ymin, xmin, ymax, xmax) or (xmin, ymin, xmax, ymax).
    Expects (xmin, ymin, xmax, ymax).
    """
    h, w = img.shape[:2]
    xmin, ymin, xmax, ymax = bbox
    xmin = max(0, min(w - 1, int(xmin)))
    xmax = max(xmin + 1, min(w, int(xmax)))
    ymin = max(0, min(h - 1, int(ymin)))
    ymax = max(ymin + 1, min(h, int(ymax)))
    return img[ymin:ymax, xmin:xmax]
