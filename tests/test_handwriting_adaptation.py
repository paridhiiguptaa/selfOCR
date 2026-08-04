import pytest
import os
import shutil
from src.ocr_pipeline.modules.handwriting_adaptation import HandwritingAdaptationModule
from src.ocr_pipeline.config import PipelineConfig

def test_handwriting_adaptation_learning(tmp_path):
    cfg = PipelineConfig(user_profile_dir=str(tmp_path))
    adapter = HandwritingAdaptationModule(cfg)
    uid = "test_student_1"

    # Initial profile
    prof = adapter.get_profile(uid)
    assert prof["user_id"] == uid
    assert prof["documents_processed"] == 0

    # Record corrections
    adapter.record_feedback(uid, original_ocr="road a bike", accepted_correction="rode a bike")
    adapter.record_feedback(uid, original_ocr="matier", accepted_correction="matter")

    prof_updated = adapter.get_profile(uid)
    assert prof_updated["documents_processed"] == 2
    assert prof_updated["corrections_accepted"] == 2
    assert "matter" in prof_updated["custom_vocabulary"]

    # Test adaptation boost calculation
    boost = adapter.calculate_candidate_adaptation_boost(uid, "matter")
    assert boost > 0.0

    # Reset profile
    assert adapter.reset_profile(uid) is True
    prof_reset = adapter.get_profile(uid)
    assert prof_reset["documents_processed"] == 0
