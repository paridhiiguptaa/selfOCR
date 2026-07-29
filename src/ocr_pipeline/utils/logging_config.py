import logging
import sys
import time
from typing import Optional

def setup_logger(name: str = "OCR_Pipeline", level: int = logging.INFO) -> logging.Logger:
    """Setup and configure a structured logger for the OCR pipeline."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

class Timer:
    """Utility class for timing pipeline execution steps."""
    def __init__(self, step_name: str, logger_instance: Optional[logging.Logger] = None):
        self.step_name = step_name
        self.logger = logger_instance or logger
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Started step: {self.step_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed step: {self.step_name} in {elapsed:.3f}s")
        else:
            self.logger.error(f"Failed step: {self.step_name} after {elapsed:.3f}s with error: {exc_val}")
