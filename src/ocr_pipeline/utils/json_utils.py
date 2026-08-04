"""
json_utils.py

Standalone JSON sanitisation utility.
Kept in a separate module to avoid importing api.py (and its module-level
OCRPipeline singleton) just to run unit tests.
"""
import json
import numpy as np
from typing import Any
from .logging_config import logger


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert all NumPy scalars, arrays, and non-serialisable types
    into native Python equivalents so that FastAPI's JSONResponse never raises
    a TypeError during serialisation.

    This is the primary guard against the post-VLM JSON crash:
      TypeError: Object of type float32 is not JSON serializable
    """
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    # Pass through all native Python-serialisable types unchanged
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    # Last resort: convert unknown types to string to avoid crash
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        logger.warning(f"[SANITIZE] Non-serialisable type {type(obj).__name__} coerced to str.")
        return str(obj)
