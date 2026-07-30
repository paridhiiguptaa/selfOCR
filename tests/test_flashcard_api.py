import pytest
from fastapi.testclient import TestClient
from src.ocr_pipeline.api import app

client = TestClient(app)

def test_flashcard_api_endpoints():
    # 1. Generate Flashcard Deck API
    payload = {
        "exported_text": "She write a letter yesterday.",
        "accepted_suggestions": [
            {
                "suggestion_id": "sug_1",
                "original_text": "write",
                "proposed_correction": "wrote",
                "category": "Grammar Correction",
                "confidence_score": 0.94,
                "explanation": "Use past tense 'wrote'.",
                "start_offset": 4,
                "end_offset": 9
            }
        ],
        "document_title": "API Test Document.pdf"
    }

    response = client.post("/api/flashcards/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "deck" in data
    assert "telemetry" in data
    deck_id = data["deck"]["deck_id"]
    card_id = data["deck"]["cards"][0]["id"]

    # 2. List Decks API
    list_res = client.get("/api/flashcards/decks")
    assert list_res.status_code == 200
    decks = list_res.json()["decks"]
    assert any(d["deck_id"] == deck_id for d in decks)

    # 3. Get Deck by ID API
    get_res = client.get(f"/api/flashcards/decks/{deck_id}")
    assert get_res.status_code == 200
    assert get_res.json()["deck_id"] == deck_id

    # 4. Patch Progress API
    patch_payload = {
        "card_updates": [{"id": card_id, "is_mastered": True, "is_bookmarked": True}]
    }
    patch_res = client.patch(f"/api/flashcards/decks/{deck_id}/progress", json=patch_payload)
    assert patch_res.status_code == 200
    assert patch_res.json()["mastery_percentage"] == 100.0

    # 5. Delete Deck API
    del_res = client.delete(f"/api/flashcards/decks/{deck_id}")
    assert del_res.status_code == 200

    # Verify deleted
    get_after_del = client.get(f"/api/flashcards/decks/{deck_id}")
    assert get_after_del.status_code == 404
