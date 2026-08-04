import pytest
from src.ocr_pipeline.modules.subject_detection import SubjectDetectionModule

def test_subject_detection_science():
    detector = SubjectDetectionModule()
    text = "Everything around us is made of matter. Matter exists in three states: solid, liquid and gases. Fill a bucket with water."
    title = "Properties of Matter"

    res = detector.detect_subject(text=text, document_title=title)
    assert res["subject"] == "Science"
    assert res["confidence"] >= 0.70
    assert "matter" in res["keywords"]

def test_subject_detection_mathematics():
    detector = SubjectDetectionModule()
    text = "Solve the linear equation for x. The perimeter of a rectangle is equal to two times the sum of length and width."
    title = "Mathematics Chapter 3 - Geometry and Equations"

    res = detector.detect_subject(text=text, document_title=title)
    assert res["subject"] == "Mathematics"
    assert res["confidence"] >= 0.70

def test_subject_detection_computer_science():
    detector = SubjectDetectionModule()
    text = "An algorithm is a step by step set of instructions. A loop executes code repeatedly in Python."
    title = "Computer Science Notes"

    res = detector.detect_subject(text=text, document_title=title)
    assert res["subject"] == "Computer Science"
