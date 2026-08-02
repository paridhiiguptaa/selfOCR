import pytest
from fastapi.testclient import TestClient
from src.ocr_pipeline.api import app, _CORRECTION_CACHE

client = TestClient(app)

def test_proofreading_endpoint_caching():
    payload = {"text": "The boy road the bicycle to school.", "language": "en"}
    
    # First request - computes and populates cache
    response1 = client.post("/api/correct-text", json=payload)
    assert response1.status_code == 200
    data1 = response1.json()
    assert "suggestions" in data1

    # Verify cache has item
    assert len(_CORRECTION_CACHE) > 0

    # Second request with exact same text - returns cached response
    response2 = client.post("/api/correct-text", json=payload)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data1 == data2

def test_proofreading_endpoint_text_change_invalidation():
    payload1 = {"text": "Original text before edit.", "language": "en"}
    payload2 = {"text": "Original text after manual edit.", "language": "en"}

    response1 = client.post("/api/correct-text", json=payload1)
    response2 = client.post("/api/correct-text", json=payload2)

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["original_text"] == "Original text before edit."
    assert response2.json()["original_text"] == "Original text after manual edit."
