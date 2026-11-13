import hashlib
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.room import RecoveryCredential


@pytest.mark.asyncio
async def test_contact_submission_creates_pending_room_and_recovery_link(client: AsyncClient):
    """Test that an anonymous finder can submit a found-item report and receive a recovery link."""
    # 1. Register owner to get a valid QR code
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "owner_contact@example.com", "password": "Password123!", "display_name": "Backpack Owner"},
    )
    public_token = reg.json()["public_token"]

    # 2. Anonymous finder submits report
    contact_payload = {
        "public_token": public_token,
        "item_name": "Black North Face Backpack",
        "finder_display_name": "Alex",
        "initial_message": "Found near the library 2nd floor desk.",
        "found_location": "Main Library",
    }
    contact_res = await client.post("/api/v1/contact/submit", json=contact_payload)
    assert contact_res.status_code == 201
    data = contact_res.json()
    assert data["status"] == "Pending"
    assert "room_id" in data
    assert "recovery_token" in data
    assert "recovery_url" in data
    assert data["reused_existing"] is False

    # Check guest session cookie
    assert "qr_guest_session" in contact_res.cookies


@pytest.mark.asyncio
async def test_smart_room_reuse_on_rescan(client: AsyncClient):
    """Test that the same guest session submitting again reuses their existing active room."""
    # 1. Register owner
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "reuse_owner@example.com", "password": "Password123!", "display_name": "Keys Owner"},
    )
    public_token = reg.json()["public_token"]

    # 2. First submission creates Room 1
    res1 = await client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": public_token,
            "item_name": "Car Keys",
            "finder_display_name": "Sam",
            "initial_message": "Found by parking lot B.",
        },
    )
    room1_id = res1.json()["room_id"]

    # 3. Second submission with the same cookies should reuse Room 1
    res2 = await client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": public_token,
            "item_name": "Car Keys",
            "finder_display_name": "Sam",
            "initial_message": "Still waiting by parking lot B.",
        },
    )
    assert res2.status_code == 201
    assert res2.json()["room_id"] == room1_id
    assert res2.json()["reused_existing"] is True


@pytest.mark.asyncio
async def test_conversation_recovery_with_hashed_token(client: AsyncClient, db_session):
    """Test recovery URL validation and verify tokens are stored as SHA-256 hashes in database."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "recover_owner@example.com", "password": "Password123!", "display_name": "Laptop Owner"},
    )
    public_token = reg.json()["public_token"]

    res = await client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": public_token,
            "item_name": "MacBook Pro",
            "finder_display_name": "Finder Charlie",
            "initial_message": "Found in conference room 3.",
        },
    )
    raw_recovery_token = res.json()["recovery_token"]
    room_id = res.json()["room_id"]

    # 1. Verify in database that token is stored HASHED, not in plaintext
    stmt = select(RecoveryCredential)
    result = await db_session.execute(stmt)
    cred = result.scalars().first()
    assert cred is not None
    assert cred.token_hash != raw_recovery_token
    assert cred.token_hash == hashlib.sha256(raw_recovery_token.encode()).hexdigest()

    # 2. Clean client without cookies restores session via recovery URL
    fresh_client = AsyncClient(transport=client._transport, base_url="http://testserver")
    rec_res = await fresh_client.get(f"/api/v1/contact/recover/{raw_recovery_token}")
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["room_id"] == room_id
    assert rec_data["item_name"] == "MacBook Pro"
    assert rec_data["owner_display_name"] == "Laptop Owner"
    assert "qr_guest_session" in rec_res.cookies


@pytest.mark.asyncio
async def test_invalid_recovery_token_rejected(client: AsyncClient):
    """Test that a forged or non-existent recovery token returns 404 Not Found."""
    res = await client.get("/api/v1/contact/recover/fake_token_that_does_not_exist")
    assert res.status_code == 404
    assert "invalid" in res.json()["detail"].lower()
