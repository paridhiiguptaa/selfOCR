import pytest
from src.ocr_pipeline.modules.educational_language_model import EducationalLanguageModel

def test_structural_classification():
    lm = EducationalLanguageModel()
    assert lm.classify_structure("Chapter 4: Properties of Matter") == "Heading"
    assert lm.classify_structure("Definition: Opaque materials do not let light pass.") == "Definition"
    assert lm.classify_structure("Activity 1: Testing solubility") == "Activity"
    assert lm.classify_structure("Experiment: Measure water boiling point") == "Experiment"
    assert lm.classify_structure("Fill a bucket with water.") == "Procedure"

def test_structural_heading_reconstruction():
    lm = EducationalLanguageModel()
    recon_text, tag, boost = lm.reconstruct_structural_text("Propeties of Matier")
    assert recon_text == "Properties of Matter"
    assert tag == "Heading"
    assert boost > 0.0

def test_candidate_selection_by_structure():
    lm = EducationalLanguageModel()
    candidates = [
        {"text": "propeties of matier", "visual_confidence": 0.75},
        {"text": "Properties of Matter", "visual_confidence": 0.85}
    ]
    recon_text, tag, boost = lm.reconstruct_structural_text("propeties of matier", candidates=candidates)
    assert recon_text == "Properties of Matter"
