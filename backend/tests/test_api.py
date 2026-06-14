"""Tests for API endpoints."""
import pytest


class TestAPIEndpoints:
    """Test API routes using sync TestClient inside async tests for fixture resolution."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "python_info" in response.text

    @pytest.mark.asyncio
    async def test_github_webhook_no_signature(self, client):
        payload = {
            "action": "completed",
            "workflow_run": {"conclusion": "failure"}
        }
        response = client.post("/api/v1/webhooks/github", json=payload)
        assert response.status_code in (202, 403)

    @pytest.mark.asyncio
    async def test_login_endpoint(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login", 
            data={"username": "admin@test.com", "password": "testpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login", 
            data={"username": "admin@test.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_incidents(self, client, auth_headers):
        response = client.get("/api/v1/incidents/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_incidents_unauthorized(self, client):
        response = client.get("/api/v1/incidents/")
        assert response.status_code == 401
