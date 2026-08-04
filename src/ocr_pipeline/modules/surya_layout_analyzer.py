import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional

from ..config import PipelineConfig, default_config
from ..models import TextRegion
from ..utils.logging_config import logger, Timer
from ..utils.image_utils import expand_bounding_box_intelligently

class SuryaLayoutAnalyzer:
    """
    Layout analysis using Surya OCR and line-level geometric segmentation.
    Groups word-level bounding boxes on the same horizontal line into line-level sentence regions,
    preventing 1-word-per-line fragmentation and dramatically reducing OCR latency.
    Includes intelligent non-overlapping margin padding to preserve ascenders and descenders.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or default_config
        self._surya_predictor = None
        self._initialized = False

    def _init_surya(self) -> bool:
        """Lazily initialize Surya layout predictor."""
        if self._initialized:
            return self._surya_predictor is not None

        self._initialized = True
        try:
            from surya.layout import LayoutPredictor

            logger.info("Initializing Surya LayoutPredictor...")
            self._surya_predictor = LayoutPredictor()
            logger.info("Surya LayoutPredictor initialized successfully.")
            return True
        except Exception as e:
            logger.warning(f"Surya LayoutPredictor failed to initialize ({e}). Falling back to geometric line segmentation.")
            self._surya_predictor = None
            return False

    def analyze(self, image: np.ndarray) -> Tuple[List[TextRegion], Dict[str, Any]]:
        """
        Analyze page layout, identify document regions, bounding boxes, labels, and human reading order.
        Applies non-overlapping padding to preserve complete ascenders and descenders.
        Returns (ordered_regions, layout_metadata).
        """
        h, w = image.shape[:2]
        metadata: Dict[str, Any] = {
            "engine": "geometric_line_segmenter",
            "region_count": 0,
            "detected_types": {}
        }

        with Timer("Line-Level Layout Analysis", logger):
            if self.config.enable_surya_layout and self._init_surya():
                try:
                    pil_img = Image.fromarray(image)
                    layout_results = self._surya_predictor(images=[pil_img])
                    if layout_results and len(layout_results) > 0:
                        res = layout_results[0]
                        bboxes = getattr(res, 'bboxes', getattr(res, 'layout_boxes', []))
                        raw_regions = []
                        reg_id = 1
                        type_counts: Dict[str, int] = {}

                        for box in bboxes:
                            raw_bbox = getattr(box, 'bbox', getattr(box, 'polygon', [0, 0, w, h]))
                            if hasattr(box, 'polygon') and isinstance(box.polygon, (list, tuple)) and len(box.polygon) == 4:
                                xmin, ymin, xmax, ymax = [int(v) for v in box.polygon]
                            else:
                                xmin, ymin, xmax, ymax = [int(v) for v in raw_bbox]

                            # Clamp bounding box
                            xmin = max(0, min(w - 1, xmin))
                            ymin = max(0, min(h - 1, ymin))
                            xmax = max(xmin + 1, min(w, xmax))
                            ymax = max(ymin + 1, min(h, ymax))

                            label = getattr(box, 'label', 'Text')
                            conf = float(getattr(box, 'confidence', 0.90))

                            raw_regions.append(TextRegion(
                                region_id=reg_id,
                                bbox=(xmin, ymin, xmax, ymax),
                                region_type=label,
                                confidence=conf
                            ))
                            reg_id += 1

                        # Group word boxes into line sentence regions
                        line_regions = self._merge_word_boxes_into_lines(raw_regions)
                        ordered_regions = self.reconstruct_reading_order(line_regions, image_width=w)
                        filtered_regions = self.filter_empty_regions(ordered_regions, image=image)
                        padded_regions = self.apply_intelligent_padding(filtered_regions, image_size=(w, h))

                        metadata["engine"] = "surya_ocr"
                        metadata["region_count"] = len(padded_regions)
                        metadata["detected_types"] = type_counts
                        return padded_regions, metadata
                except Exception as e:
                    logger.warning(f"Surya layout prediction failed: {e}. Utilizing geometric line segmenter.")

            # Geometric line segmentation
            line_regions = self._geometric_line_segmentation(image)
            ordered_regions = self.reconstruct_reading_order(line_regions, image_width=w)
            filtered_regions = self.filter_empty_regions(ordered_regions, image=image)
            padded_regions = self.apply_intelligent_padding(filtered_regions, image_size=(w, h))

            metadata["engine"] = "geometric_line_segmenter"
            metadata["region_count"] = len(padded_regions)
            metadata["detected_types"] = {"Text": len(padded_regions)}
            return padded_regions, metadata

    def compute_ink_density(self, crop: np.ndarray) -> float:
        """Calculate foreground ink pixel ratio inside bounding box crop."""
        if crop is None or crop.size == 0:
            return 0.0
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if len(crop.shape) == 3 else crop
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        ink_pixels = np.count_nonzero(thresh)
        return float(ink_pixels) / float(gray.size)

    def filter_empty_regions(self, regions: List[TextRegion], image: np.ndarray) -> List[TextRegion]:
        """Filter out empty background bounding boxes with insufficient ink density."""
        valid_regions = []
        for reg in regions:
            xmin, ymin, xmax, ymax = reg.bbox
            crop = image[ymin:ymax, xmin:xmax]
            density = self.compute_ink_density(crop)
            reg.ink_density = density
            if density >= self.config.min_ink_density:
                valid_regions.append(reg)
            else:
                logger.info(f"Filtered out empty background Region #{reg.region_id} (Ink density {density:.4f} < {self.config.min_ink_density:.4f}).")
        return valid_regions

    def apply_intelligent_padding(self, regions: List[TextRegion], image_size: Tuple[int, int]) -> List[TextRegion]:
        """Apply adaptive margin padding around all detected text regions to preserve ascenders & descenders."""
        if not regions:
            return []

        all_bboxes = [r.bbox for r in regions]
        padded_regions = []

        for reg in regions:
            reg.unpadded_bbox = reg.bbox
            padded_box = expand_bounding_box_intelligently(
                bbox=reg.bbox,
                image_size=image_size,
                v_pad_ratio=self.config.bbox_padding_vertical_ratio,
                h_pad_ratio=self.config.bbox_padding_horizontal_ratio,
                min_pad_px=self.config.bbox_min_padding_px,
                other_bboxes=all_bboxes
            )
            reg.bbox = padded_box
            padded_regions.append(reg)

        return padded_regions

    def reconstruct_reading_order(self, regions: List[TextRegion], image_width: int) -> List[TextRegion]:
        """
        Sort detected line regions into natural human reading order (top-to-bottom, left-to-right).
        """
        if not regions:
            return []

        sorted_regions = sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))
        order_idx = 1
        for reg in sorted_regions:
            reg.reading_order_idx = order_idx
            order_idx += 1

        return sorted_regions

    def _geometric_line_segmentation(self, image: np.ndarray) -> List[TextRegion]:
        """
        High-precision line-level geometric detector. Uses adaptive horizontal dilation
        and merges adjacent word contours on the same line into full sentence bounding boxes.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        h, w = gray.shape

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Horizontal structuring element to connect words into full lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw_regions = []
        reg_id = 1

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 60:
                continue
            x, y, bw, bh = cv2.boundingRect(cnt)
            if bw < 12 or bh < 6:
                continue

            label = "Text"
            if bh > 40 and bw > 0.6 * w:
                label = "Title"
            elif bh > 22 and bw < 0.4 * w and y < 0.2 * h:
                label = "Section-header"

            raw_regions.append(TextRegion(
                region_id=reg_id,
                bbox=(x, y, x + bw, y + bh),
                region_type=label,
                confidence=0.90
            ))
            reg_id += 1

        # Split multi-line blocks then merge horizontally into line regions
        split_regions = self._split_tall_regions(image, raw_regions)
        return self._merge_word_boxes_into_lines(split_regions)

    def _split_tall_regions(self, image: np.ndarray, regions: List[TextRegion]) -> List[TextRegion]:
        """
        Detect multi-line bounding boxes (height > 38px) and split them into line bands
        using horizontal projection gaps.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        img_h, img_w = gray.shape
        fine_regions = []
        reg_id = 1

        for reg in regions:
            xmin, ymin, xmax, ymax = reg.bbox
            bh = ymax - ymin
            bw = xmax - xmin

            if bh < 38:
                reg.region_id = reg_id
                fine_regions.append(reg)
                reg_id += 1
                continue

            crop_gray = gray[ymin:ymax, xmin:xmax]
            _, crop_thresh = cv2.threshold(crop_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            h_proj = np.sum(crop_thresh, axis=1)
            is_text = h_proj > 0.05 * np.max(h_proj) if np.max(h_proj) > 0 else np.zeros_like(h_proj, dtype=bool)
            
            line_starts = []
            line_ends = []
            in_line = False

            for row_idx, val in enumerate(is_text):
                if val and not in_line:
                    line_starts.append(row_idx)
                    in_line = True
                elif not val and in_line:
                    line_ends.append(row_idx)
                    in_line = False

            if in_line:
                line_ends.append(len(is_text))

            if len(line_starts) > 1:
                for l_start, l_end in zip(line_starts, line_ends):
                    line_h = l_end - l_start
                    if line_h >= 6:
                        sub_ymin = max(0, ymin + l_start - 2)
                        sub_ymax = min(img_h, ymin + l_end + 2)
                        fine_regions.append(TextRegion(
                            region_id=reg_id,
                            bbox=(xmin, sub_ymin, xmax, sub_ymax),
                            region_type=reg.region_type,
                            confidence=reg.confidence
                        ))
                        reg_id += 1
            else:
                reg.region_id = reg_id
                fine_regions.append(reg)
                reg_id += 1

        return fine_regions

    def _merge_word_boxes_into_lines(self, regions: List[TextRegion]) -> List[TextRegion]:
        """
        Group word boxes that lie on the same horizontal line into full sentence line regions.
        Eliminates 1-word-per-line output fragmentation.
        """
        if not regions:
            return []

        sorted_regs = sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))
        lines: List[List[TextRegion]] = []

        for reg in sorted_regs:
            xmin, ymin, xmax, ymax = reg.bbox
            placed = False

            for line in lines:
                l_ymin = min(r.bbox[1] for r in line)
                l_ymax = max(r.bbox[3] for r in line)
                l_h = max(1, l_ymax - l_ymin)
                r_h = max(1, ymax - ymin)

                overlap = max(0, min(ymax, l_ymax) - max(ymin, l_ymin))
                # Check vertical overlap on same horizontal line
                if overlap >= 0.4 * min(r_h, l_h):
                    line.append(reg)
                    placed = True
                    break

            if not placed:
                lines.append([reg])

        merged_regions: List[TextRegion] = []
        reg_id = 1

        for line in lines:
            # Sort left-to-right within the line
            line.sort(key=lambda r: r.bbox[0])

            line_xmin = min(r.bbox[0] for r in line)
            line_ymin = min(r.bbox[1] for r in line)
            line_xmax = max(r.bbox[2] for r in line)
            line_ymax = max(r.bbox[3] for r in line)

            merged_regions.append(TextRegion(
                region_id=reg_id,
                bbox=(line_xmin, line_ymin, line_xmax, line_ymax),
                region_type=line[0].region_type,
                confidence=max(r.confidence for r in line)
            ))
            reg_id += 1

        ordered = sorted(merged_regions, key=lambda r: r.bbox[1])
        if self.config.enable_paragraph_grouping:
            return self.group_lines_into_paragraphs(ordered)
        return ordered

    def group_lines_into_paragraphs(self, regions: List[TextRegion]) -> List[TextRegion]:
        """
        Group adjacent horizontal line regions into paragraph blocks.
        Assigns paragraph_id to each TextRegion.
        """
        if not regions:
            return []

        para_id = 1
        current_para: List[TextRegion] = []
        result: List[TextRegion] = []

        for reg in regions:
            if not current_para:
                reg.paragraph_id = para_id
                current_para.append(reg)
                continue

            last_reg = current_para[-1]
            gap_v = reg.bbox[1] - last_reg.bbox[3]
            avg_h = max(1, last_reg.height)

            # Check if region is part of the same paragraph (vertical gap < 1.6 * line_height)
            if gap_v <= 1.6 * avg_h and reg.region_type == last_reg.region_type and reg.region_type not in ("Title", "Section-header"):
                reg.paragraph_id = para_id
                current_para.append(reg)
            else:
                para_id += 1
                reg.paragraph_id = para_id
                current_para = [reg]

            result.append(reg)

        if current_para and current_para[0] not in result:
            result.insert(0, current_para[0])

        return sorted(regions, key=lambda r: r.bbox[1])

