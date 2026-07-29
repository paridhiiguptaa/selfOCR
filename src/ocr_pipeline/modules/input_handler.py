import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import pypdfium2 as pdfium
from PIL import Image

from ..config import PipelineConfig, default_config
from ..utils.image_utils import load_image_as_numpy, pil_to_numpy
from ..utils.logging_config import logger, Timer

@dataclass
class DocumentPage:
    """Structure representing a single processed document page."""
    page_number: int          # 1-indexed page number
    total_pages: int          # Total number of pages in document
    image: np.ndarray         # RGB numpy array (H, W, 3)
    source_path: str          # Original file path
    width: int
    height: int
    is_pdf: bool

class InputHandler:
    """Handles loading images and multi-page PDFs into unified DocumentPage structures."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self.config.validate()

    def is_supported(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.config.supported_extensions

    def load_document(self, file_path: str) -> List[DocumentPage]:
        """
        Load an image or PDF file and return a list of DocumentPage objects.
        For PDFs, converts each page to a high-resolution RGB image.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not self.is_supported(file_path):
            raise ValueError(
                f"Unsupported file format '{os.path.splitext(file_path)[1]}'. "
                f"Supported: {self.config.supported_extensions}"
            )
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._load_pdf(file_path)
        else:
            return self._load_image(file_path)

    def _load_image(self, file_path: str) -> List[DocumentPage]:
        """Load a single static image file."""
        with Timer(f"Load Image ({os.path.basename(file_path)})", logger):
            img_arr = load_image_as_numpy(file_path)
            h, w = img_arr.shape[:2]
            page = DocumentPage(
                page_number=1,
                total_pages=1,
                image=img_arr,
                source_path=file_path,
                width=w,
                height=h,
                is_pdf=False
            )
            logger.info(f"Loaded image {file_path} (Resolution: {w}x{h})")
            return [page]

    def _load_pdf(self, file_path: str) -> List[DocumentPage]:
        """Convert multi-page PDF into DocumentPage instances at target DPI using pypdfium2."""
        with Timer(f"Render PDF ({os.path.basename(file_path)})", logger):
            pdf = pdfium.PdfDocument(file_path)
            total_pages = len(pdf)
            logger.info(f"Rendering PDF {file_path} with {total_pages} page(s) at {self.config.pdf_render_dpi} DPI")
            
            pages: List[DocumentPage] = []
            # Calculate scale factor: 72 DPI is base PDF 1.0 scale
            scale = self.config.pdf_render_dpi / 72.0
            
            for idx in range(total_pages):
                pdf_page = pdf[idx]
                pil_image = pdf_page.render(scale=scale).to_pil()
                img_arr = pil_to_numpy(pil_image)
                h, w = img_arr.shape[:2]
                
                doc_page = DocumentPage(
                    page_number=idx + 1,
                    total_pages=total_pages,
                    image=img_arr,
                    source_path=file_path,
                    width=w,
                    height=h,
                    is_pdf=True
                )
                pages.append(doc_page)
                logger.info(f"Rendered page {idx+1}/{total_pages} (Resolution: {w}x{h})")
                
            pdf.close()
            return pages
