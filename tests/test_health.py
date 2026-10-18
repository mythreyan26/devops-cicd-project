"""Unit tests for the health check and runtime info endpoints."""

from datetime import datetime


def test_health_check_success(client):
    """Verify that GET /health returns 200 OK with healthy status and valid UTC timestamp."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

    # Verify that timestamp is valid ISO format
    parsed_time = datetime.fromisoformat(data["timestamp"])
    assert parsed_time.tzinfo is not None


def test_app_info_success(client):
    """Verify that GET /api/v1/info returns application metadata and environment details."""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data["app_name"] == "DevOps-CICD-Service"
    assert data["version"] == "1.0.0"
    assert "python_version" in data
    assert data["environment"] == "testing"
    assert "timestamp" in data

    parsed_time = datetime.fromisoformat(data["timestamp"])
    assert parsed_time.tzinfo is not None
