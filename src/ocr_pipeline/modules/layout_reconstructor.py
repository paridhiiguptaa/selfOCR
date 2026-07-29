from typing import List, Dict, Any, Optional
from ..models import TextRegion
from ..utils.logging_config import logger, Timer

class LayoutReconstructor:
    """
    Reconstructs natural human reading order, paragraphs, headings, lists,
    tables, and page structure into clean Plain Text and Markdown.
    """

    def reconstruct(self, regions: List[TextRegion]) -> Dict[str, str]:
        """
        Convert ordered list of TextRegion items into structured Plain Text and Markdown.
        Returns dict containing 'plain_text' and 'markdown'.
        """
        if not regions:
            return {"plain_text": "", "markdown": ""}

        with Timer("Layout Reconstruction", logger):
            # Sort by reading_order_idx
            ordered = sorted(regions, key=lambda r: r.reading_order_idx)

            plain_lines: List[str] = []
            md_lines: List[str] = []

            for reg in ordered:
                text = reg.text.strip()
                if not text:
                    continue

                # Plain text line
                plain_lines.append(text)

                # Format Markdown based on layout region type
                if reg.region_type == "Title":
                    md_lines.append(f"# {text}")
                elif reg.region_type == "Section-header":
                    md_lines.append(f"## {text}")
                elif reg.region_type == "Caption":
                    md_lines.append(f"*{text}*")
                elif reg.region_type == "List-item":
                    if not (text.startswith("- ") or text.startswith("* ") or text[0].isdigit()):
                        md_lines.append(f"- {text}")
                    else:
                        md_lines.append(text)
                elif reg.region_type == "Table":
                    # If table text isn't already formatted as markdown table, wrap in code block or paragraph
                    if "|" in text:
                        md_lines.append(text)
                    else:
                        md_lines.append(f"```table\n{text}\n```")
                else:
                    md_lines.append(text)

            plain_output = "\n\n".join(plain_lines)
            markdown_output = "\n\n".join(md_lines)

            return {
                "plain_text": plain_output,
                "markdown": markdown_output
            }
