import pytest
from src.ocr_pipeline.modules.text_corrector import TextCorrectionEngine
from src.ocr_pipeline.modules.document_reconstruction_engine import DocumentReconstructionEngine

def test_properties_of_matter_reconstruction():
    engine = TextCorrectionEngine()
    
    corrupted_input = "Us is made of matte EartethaGaAEeu exists in 3 states"
    expected_reconstructed = "Everything around us is made of matter. Matter exists in three states: solid, liquid and gases."
    
    result = engine.analyze_text(corrupted_input)
    assert result.corrected_text == expected_reconstructed
    assert result.topic_prior.get("topic_key") == "matter"
    assert len(result.suggestions) > 0

def test_classroom_activity_reconstruction():
    engine = TextCorrectionEngine()
    
    corrupted_input = "Eil Jueket with water Take ang tempt braille"
    expected_reconstructed = "Fill a bucket with water. Take an empty bottle with its mouth facing downwards."
    
    result = engine.analyze_text(corrupted_input)
    assert result.corrected_text == expected_reconstructed
    assert result.topic_prior.get("topic_key") == "matter"

def test_optics_note_reconstruction():
    engine = TextCorrectionEngine()
    
    corrupted_input = "Matrials which light does pass atall thccaldbd is Opaque"
    expected_reconstructed = "Materials through which light does not pass at all are called Opaque."
    
    result = engine.analyze_text(corrupted_input)
    assert result.corrected_text == expected_reconstructed
    assert result.topic_prior.get("topic_key") == "optics"

def test_multi_factor_confidence_calibration():
    engine = DocumentReconstructionEngine()
    
    raw_text = "Us is made of matte EartethaGaAEeu exists in 3 states"
    recon_text, suggs, stats = engine.reconstruct_document(raw_text)
    
    assert "ocr_confidence" in stats
    assert "reconstruction_confidence" in stats
    assert "final_confidence" in stats
    assert stats["reconstruction_confidence"] >= stats["ocr_confidence"]
    assert stats["final_confidence"] > 0.85

def test_document_topic_prior_extraction():
    engine = DocumentReconstructionEngine()
    
    text = "# Properties of Matter\nSolids, liquids, and gases fill a bucket and bottle."
    topic_meta = engine.extract_topic_prior(text)
    
    assert topic_meta["topic_key"] == "matter"
    assert topic_meta["confidence"] > 0.70
    assert len(topic_meta["keywords"]) > 0
