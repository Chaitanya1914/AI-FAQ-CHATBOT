"""
Integration tests for the chat API endpoints.
Tests the /api/chat route for message processing and feedback.
"""
import pytest


def test_chat_returns_response(client, seed_faqs):
    """POST /api/chat with a valid message returns 200 with expected schema."""
    response = client.post("/api/chat/", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert "confidence" in data
    assert "log_id" in data


def test_chat_generates_session_id(client, seed_faqs):
    """If no session_id provided, one is generated."""
    response = client.post("/api/chat/", json={"message": "Hi"})
    data = response.json()
    assert data["session_id"] is not None
    assert len(data["session_id"]) > 0


def test_chat_preserves_session_id(client, seed_faqs):
    """If session_id provided, same one is returned."""
    test_session_id = "test-session-123"
    response = client.post("/api/chat/", json={
        "message": "Hi",
        "session_id": test_session_id
    })
    data = response.json()
    assert data["session_id"] == test_session_id


def test_chat_confident_match(client, seed_faqs):
    """Asking a question close to a seeded FAQ returns the correct answer."""
    response = client.post("/api/chat/", json={
        "message": "How long does shipping take?"
    })
    data = response.json()
    # Should match the seeded "How long does shipping take?" FAQ
    assert data["confidence"] > 0.5
    assert data["matched_faq"] is not None
    assert "shipping" in data["matched_faq"].lower() or "shipping" in data["response"].lower()


def test_chat_fallback_response(client, seed_faqs):
    """Asking gibberish returns low confidence fallback."""
    response = client.post("/api/chat/", json={
        "message": "xyzzy plugh foobar baz"
    })
    data = response.json()
    # Should not match any FAQ with high confidence
    assert "rephras" in data["response"].lower() or "not sure" in data["response"].lower()


def test_feedback_endpoint(client, seed_faqs):
    """POST /{log_id}/feedback updates the log entry."""
    # First, create a chat log
    chat_response = client.post("/api/chat/", json={"message": "Hello"})
    log_id = chat_response.json()["log_id"]

    # Submit positive feedback
    feedback_response = client.post(
        f"/api/chat/{log_id}/feedback?feedback=positive"
    )
    assert feedback_response.status_code == 200
    assert "success" in feedback_response.json()["message"].lower()
