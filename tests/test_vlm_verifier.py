import pytest
import numpy as np
from src.ocr_pipeline.modules.vlm_verifier import VisionLanguageVerifier

def test_vlm_verifier_lightweight_verification():
    verifier = VisionLanguageVerifier()
    crop = np.zeros((40, 200, 3), dtype=np.uint8) + 210

    candidate_text = "Us is made of matier and opaqe substances"
    res = verifier.verify_transcription(crop, candidate_text, subject="Science")

    assert "matter" in res["verified_text"]
    assert "opaque" in res["verified_text"]
    assert len(res["changes_made"]) >= 1
    assert "confidence" in res
