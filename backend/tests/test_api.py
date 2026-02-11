from fastapi.testclient import TestClient
from backend.main import app
import pytest

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["data_loaded"] is True

def test_recommendation_endpoint_structure():
    """Test standard recommendation request structure."""
    payload = {
        "query": "Italian food in Bangalore",
        "top_k": 3
    }
    with TestClient(app) as client:
        response = client.post("/api/recommend", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "restaurants" in data
        assert "ai_analysis" in data
        assert isinstance(data["restaurants"], list)
        assert len(data["restaurants"]) <= 3

def test_recommendation_results_content():
    """Test that results contain expected fields."""
    payload = {
        "query": "Pizza",
        "top_k": 1
    }
    with TestClient(app) as client:
        response = client.post("/api/recommend", json=payload)
        data = response.json()
        
        if len(data["restaurants"]) > 0:
            restaurant = data["restaurants"][0]
            assert "name" in restaurant
            assert "cuisine" in restaurant
            assert "location" in restaurant
            assert "rating" in restaurant
