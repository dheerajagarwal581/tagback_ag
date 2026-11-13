import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_owner_registration_and_qr_auto_provisioning(client: AsyncClient):
    """Test that registering an owner auto-creates their profile and permanent QR code."""
    payload = {
        "email": "testowner@example.com",
        "password": "Password123!",
        "display_name": "Test Owner",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testowner@example.com"
    assert data["display_name"] == "Test Owner"
    assert "public_token" in data
    assert len(data["public_token"]) > 10

    # Verify session cookie was set
    assert "qr_owner_session" in response.cookies


@pytest.mark.asyncio
async def test_duplicate_email_registration_rejected(client: AsyncClient):
    """Test that registering with an existing email returns 400 Bad Request."""
    payload = {
        "email": "dup@example.com",
        "password": "Password123!",
        "display_name": "User 1",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success_and_failure(client: AsyncClient):
    """Test owner login with valid and invalid passwords."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "SecretPassword123", "display_name": "Alex"},
    )

    # 1. Invalid password
    bad_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "WrongPassword"},
    )
    assert bad_res.status_code == 401

    # 2. Valid password
    good_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "SecretPassword123"},
    )
    assert good_res.status_code == 200
    assert "qr_owner_session" in good_res.cookies


@pytest.mark.asyncio
async def test_authenticated_me_and_qr_download(client: AsyncClient):
    """Test /me, /qr/my-code, and /qr/download for an authenticated owner."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "Password123!", "display_name": "Demo User"},
    )
    public_token = reg.json()["public_token"]

    # 1. Check /me
    me_res = await client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me@example.com"
    assert me_res.json()["public_token"] == public_token

    # 2. Check /qr/my-code
    qr_res = await client.get("/api/v1/qr/my-code")
    assert qr_res.status_code == 200
    assert qr_res.json()["public_token"] == public_token

    # 3. Check /qr/download
    download_res = await client.get("/api/v1/qr/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "image/png"
    assert len(download_res.content) > 100  # Valid PNG image bytes


@pytest.mark.asyncio
async def test_qr_regeneration(client: AsyncClient):
    """Test that regenerating a QR code produces a new token and revokes the old one."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "regen@example.com", "password": "Password123!", "display_name": "Regen User"},
    )
    old_token = reg.json()["public_token"]

    # Regenerate QR
    regen_res = await client.post("/api/v1/qr/regenerate")
    assert regen_res.status_code == 200
    new_token = regen_res.json()["new_public_token"]
    assert new_token != old_token

    # Old token lookup should now return 404
    old_lookup = await client.get(f"/api/v1/qr/public/{old_token}")
    assert old_lookup.status_code == 404

    # New token lookup succeeds
    new_lookup = await client.get(f"/api/v1/qr/public/{new_token}")
    assert new_lookup.status_code == 200
    assert new_lookup.json()["display_name"] == "Regen User"


@pytest.mark.asyncio
async def test_public_qr_profile_does_not_leak_private_data(client: AsyncClient):
    """Privacy test: Public QR profile should never expose email or internal user id."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "private@example.com", "password": "Password123!", "display_name": "Private Owner"},
    )
    public_token = reg.json()["public_token"]

    # Public scan by unauthenticated finder
    unauth_client = AsyncClient(transport=client._transport, base_url="http://testserver")
    res = await unauth_client.get(f"/api/v1/qr/public/{public_token}")
    assert res.status_code == 200
    data = res.json()
    assert data["display_name"] == "Private Owner"
    assert "email" not in data
    assert "password_hash" not in data
    assert "user_id" not in data
