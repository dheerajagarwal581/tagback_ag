import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_healthy(client: AsyncClient):
    """Test that the /api/v1/health endpoint responds with 200 and healthy database status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["service"] == "qr-temporary-communication-api"


@pytest.mark.asyncio
async def test_root_endpoint_returns_api_metadata(client: AsyncClient):
    """Test that the / root endpoint returns API links."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["health"] == "/api/v1/health"
