"""
Integration tests for the FAQ management API endpoints.
Tests CRUD operations on /api/faq routes.
"""
import pytest


def test_list_faqs(client, seed_faqs):
    """GET /api/faq returns a list of FAQs."""
    response = client.get("/api/faq/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_create_faq(client, seed_faqs):
    """POST /api/faq creates a new entry."""
    new_faq = {
        "question": "Do you offer discounts?",
        "answer": "Yes, we have seasonal sales and promotions.",
        "category": "Sales"
    }
    response = client.post("/api/faq/", json=new_faq)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == new_faq["question"]
    assert "id" in data


def test_get_faq_by_id(client, seed_faqs):
    """GET /api/faq/{id} returns the correct entry."""
    faq_id = seed_faqs[0].id
    response = client.get(f"/api/faq/{faq_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == faq_id
    assert data["question"] == seed_faqs[0].question


def test_update_faq(client, seed_faqs):
    """PUT /api/faq/{id} updates fields."""
    faq_id = seed_faqs[0].id
    update_data = {
        "answer": "Updated: We are open 24/7 now!"
    }
    response = client.put(f"/api/faq/{faq_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Updated: We are open 24/7 now!"


def test_delete_faq(client, seed_faqs):
    """DELETE /api/faq/{id} removes entry."""
    faq_id = seed_faqs[-1].id
    response = client.delete(f"/api/faq/{faq_id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = client.get(f"/api/faq/{faq_id}")
    assert get_response.status_code == 404


def test_filter_by_category(client, seed_faqs):
    """GET /api/faq?category=Shipping filters correctly."""
    response = client.get("/api/faq/?category=Shipping")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for faq in data:
        assert faq["category"] == "Shipping"


def test_get_nonexistent_faq(client, seed_faqs):
    """GET /api/faq/{id} for nonexistent ID returns 404."""
    response = client.get("/api/faq/99999")
    assert response.status_code == 404
