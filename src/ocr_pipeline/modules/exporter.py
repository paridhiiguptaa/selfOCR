import os
import json
from typing import Dict, Any, List, Optional
from ..utils.logging_config import logger, Timer

class Exporter:
    """
    Handles structured exporting of document transcriptions into Plain Text (.txt),
    Markdown (.md), and JSON (.json) formats.
    """

    def export_all(
        self,
        output_dir: str,
        base_name: str,
        transcription: Dict[str, str],
        pages_metadata: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Export plain text, markdown, and structured JSON results to output_dir.
        Returns a dictionary of output file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        export_paths = {}

        with Timer(f"Export Results ({base_name})", logger):
            # 1. Plain Text Export (.txt)
            txt_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcription.get("plain_text", ""))
            export_paths["txt"] = txt_path

            # 2. Markdown Export (.md)
            md_path = os.path.join(output_dir, f"{base_name}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(transcription.get("markdown", ""))
            export_paths["markdown"] = md_path

            # 3. JSON Export (.json)
            json_payload = {
                "document_name": base_name,
                "total_pages": len(pages_metadata),
                "transcription": transcription,
                "pages": pages_metadata
            }
            json_path = os.path.join(output_dir, f"{base_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_payload, f, indent=2, ensure_ascii=False)
            export_paths["json"] = json_path

            logger.info(f"Successfully exported results for '{base_name}' to {output_dir}")
            return export_paths
