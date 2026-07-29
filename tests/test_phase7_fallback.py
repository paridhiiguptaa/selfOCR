import os
from src.ocr_pipeline.modules.exporter import Exporter

def test_exporter(tmp_path):
    exporter = Exporter()
    transcription = {
        "plain_text": "Sample Plain Text",
        "markdown": "# Sample Markdown"
    }
    pages_meta = [{"page_number": 1}]

    export_paths = exporter.export_all(
        output_dir=str(tmp_path),
        base_name="doc1",
        transcription=transcription,
        pages_metadata=pages_meta
    )

    assert os.path.exists(export_paths["txt"])
    assert os.path.exists(export_paths["markdown"])
    assert os.path.exists(export_paths["json"])
