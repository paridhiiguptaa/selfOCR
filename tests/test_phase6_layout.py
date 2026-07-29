from src.ocr_pipeline.modules.layout_reconstructor import LayoutReconstructor
from src.ocr_pipeline.models import TextRegion

def test_layout_reconstruction():
    regions = [
        TextRegion(region_id=1, bbox=(0, 0, 100, 20), region_type="Title", text="Document Title", reading_order_idx=1),
        TextRegion(region_id=2, bbox=(0, 30, 100, 50), region_type="Section-header", text="Section Heading", reading_order_idx=2),
        TextRegion(region_id=3, bbox=(0, 60, 100, 80), region_type="Text", text="Paragraph 1 text content.", reading_order_idx=3)
    ]

    reconstructor = LayoutReconstructor()
    res = reconstructor.reconstruct(regions)

    assert "plain_text" in res
    assert "markdown" in res
    assert "# Document Title" in res["markdown"]
    assert "## Section Heading" in res["markdown"]
    assert "Paragraph 1 text content." in res["plain_text"]
