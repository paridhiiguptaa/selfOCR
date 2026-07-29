from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

@dataclass
class TextRegion:
    """Structure representing a bounding box text region in a document."""
    region_id: int
    bbox: Tuple[int, int, int, int]  # [xmin, ymin, xmax, ymax]
    region_type: str = "Text"        # "Title", "Section-header", "Text", "List-item", "Table", "Caption"
    text: str = ""
    confidence: float = 1.0
    text_type: str = "mixed"         # "printed", "handwritten", "mixed"
    reading_order_idx: int = 0
    line_number: int = 1
    column_number: int = 1
    fallback_triggered: bool = False
    fallback_model: Optional[str] = None

    @property
    def center(self) -> Tuple[float, float]:
        """Center coordinates of bounding box (x_center, y_center)."""
        xmin, ymin, xmax, ymax = self.bbox
        return (xmin + xmax) / 2.0, (ymin + ymax) / 2.0

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

@dataclass
class DocumentPage:
    """Structure representing a single processed document page."""
    page_number: int
    total_pages: int
    image: np.ndarray          # RGB numpy array (H, W, 3)
    source_path: str
    width: int
    height: int
    is_pdf: bool = False

@dataclass
class PageTelemetry:
    """Detailed timing telemetry for pipeline stages per page."""
    stage_durations: Dict[str, float] = field(default_factory=dict)
    preprocessing_meta: Dict[str, Any] = field(default_factory=dict)
    orientation_meta: Dict[str, Any] = field(default_factory=dict)
    layout_stats: Dict[str, Any] = field(default_factory=dict)
    fallback_count: int = 0
    mean_confidence: float = 0.0

@dataclass
class OCRResult:
    """Complete document OCR result."""
    document_name: str
    total_pages: int
    transcription_plain: str
    transcription_markdown: str
    pages: List[Dict[str, Any]]
    telemetry: Dict[str, Any]
    export_paths: Dict[str, str] = field(default_factory=dict)
