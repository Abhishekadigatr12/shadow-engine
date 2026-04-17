import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_safe_input():
    """Test analyzing safe input"""
    response = client.post(
        "/shadow/analyze",
        json={"raw_data": "Hello world, this is a normal message"},
        headers={"api-key": "shadow-dev-key-12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert data["action"] in ["ALLOW", "ALERT"]


def test_analyze_with_email():
    """Test detecting email"""
    response = client.post(
        "/shadow/analyze",
        json={"raw_data": "Contact me at test@example.com"},
        headers={"api-key": "shadow-dev-key-12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] > 0.3


def test_analyze_without_api_key():
    """Test that API key is required"""
    response = client.post(
        "/shadow/analyze",
        json={"raw_data": "test data"}
    )
    assert response.status_code == 403 or response.status_code == 401


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Shadow Engine"
