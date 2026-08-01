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
    Crop region from RGB image given bounding box (xmin, ymin, xmax, ymax).
    """
    h, w = img.shape[:2]
    xmin, ymin, xmax, ymax = bbox
    xmin = max(0, min(w - 1, int(xmin)))
    xmax = max(xmin + 1, min(w, int(xmax)))
    ymin = max(0, min(h - 1, int(ymin)))
    ymax = max(ymin + 1, min(h, int(ymax)))
    return img[ymin:ymax, xmin:xmax]

def expand_bounding_box_intelligently(
    bbox: Tuple[int, int, int, int],
    image_size: Tuple[int, int],  # (width, height)
    v_pad_ratio: float = 0.18,
    h_pad_ratio: float = 0.08,
    min_pad_px: int = 6,
    other_bboxes: Optional[List[Tuple[int, int, int, int]]] = None
) -> Tuple[int, int, int, int]:
    """
    Intelligently expand bounding box to include ascenders (f, h, k, l, b, d) and descenders (g, y, p, q, j).
    Clamps expansion to prevent overlapping neighboring text regions or exceeding image boundaries.
    """
    img_w, img_h = image_size
    xmin, ymin, xmax, ymax = bbox

    box_h = max(1, ymax - ymin)
    box_w = max(1, xmax - xmin)

    desired_v_pad = max(min_pad_px, int(box_h * v_pad_ratio))
    desired_h_pad = max(min_pad_px, int(box_w * h_pad_ratio))

    new_xmin = max(0, xmin - desired_h_pad)
    new_ymin = max(0, ymin - desired_v_pad)
    new_xmax = min(img_w, xmax + desired_h_pad)
    new_ymax = min(img_h, ymax + desired_v_pad)

    if other_bboxes:
        for other in other_bboxes:
            oxmin, oymin, oxmax, oymax = other
            if (oxmin, oymin, oxmax, oymax) == (xmin, ymin, xmax, ymax):
                continue

            # Check horizontal overlap with neighboring box to constrain vertical expansion
            h_overlap = max(0, min(xmax, oxmax) - max(xmin, oxmin))
            if h_overlap > 0:
                # Other box is directly above
                if oymax <= ymin:
                    new_ymin = max(new_ymin, oymax)
                # Other box is directly below
                elif oymin >= ymax:
                    new_ymax = min(new_ymax, oymin)

            # Check vertical overlap with neighboring box to constrain horizontal expansion
            v_overlap = max(0, min(ymax, oymax) - max(ymin, oymin))
            if v_overlap > 0:
                # Other box is directly left
                if oxmax <= xmin:
                    new_xmin = max(new_xmin, oxmax)
                # Other box is directly right
                elif oxmin >= xmax:
                    new_xmax = min(new_xmax, oxmin)

    # Sanity checks
    new_xmin = max(0, min(img_w - 1, new_xmin))
    new_xmax = max(new_xmin + 1, min(img_w, new_xmax))
    new_ymin = max(0, min(img_h - 1, new_ymin))
    new_ymax = max(new_ymin + 1, min(img_h, new_ymax))

    return (new_xmin, new_ymin, new_xmax, new_ymax)

