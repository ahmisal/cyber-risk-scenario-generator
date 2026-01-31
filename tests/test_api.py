"""Pytest tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cyber-risk-generator"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_analyze_endpoint_missing_file():
    """Test analyze endpoint with missing file."""
    response = client.post(
        "/api/v1/analyze",
        data={"asset_name": "Test Asset"}
    )
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_file_type():
    """Test analyze endpoint with invalid file type."""
    response = client.post(
        "/api/v1/analyze",
        data={"asset_name": "Test Asset"},
        files={"file": ("test.jpg", b"fake image content", "image/jpeg")}
    )
    assert response.status_code == 400


def test_analyze_endpoint_empty_asset_name():
    """Test analyze endpoint with empty asset name."""
    response = client.post(
        "/api/v1/analyze",
        data={"asset_name": ""},
        files={"file": ("test.txt", b"Sample content", "text/plain")}
    )
    assert response.status_code == 422  # Validation error
