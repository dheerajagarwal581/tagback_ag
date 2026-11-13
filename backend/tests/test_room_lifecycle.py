import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_owner_room_triage_lifecycle(client: AsyncClient):
    """Test full owner triage lifecycle: list pending -> accept -> active -> mark recovered."""
    # 1. Register owner
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "lifecycle_owner@example.com", "password": "Password123!", "display_name": "Triage Owner"},
    )
    public_token = reg.json()["public_token"]

    # 2. Finder submits contact request
    contact_res = await client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": public_token,
            "item_name": "Leather Wallet",
            "finder_display_name": "Finder Dave",
            "initial_message": "Found near cafe counter.",
        },
    )
    room_id = contact_res.json()["room_id"]

    # 3. Owner lists pending rooms
    rooms_res = await client.get("/api/v1/rooms?status=Pending")
    assert rooms_res.status_code == 200
    pending_rooms = rooms_res.json()
    assert len(pending_rooms) == 1
    assert pending_rooms[0]["room_id"] == room_id
    assert pending_rooms[0]["item_name"] == "Leather Wallet"

    # 4. Check owner received notification
    notifs_res = await client.get("/api/v1/notifications")
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()
    assert len(notifs) >= 1
    assert "Leather Wallet" in notifs[0]["title"]

    # 5. Owner accepts contact request
    accept_res = await client.post(f"/api/v1/rooms/{room_id}/accept")
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "Active"

    # 6. Verify room is now Active
    active_rooms = (await client.get("/api/v1/rooms?status=Active")).json()
    assert len(active_rooms) == 1
    assert active_rooms[0]["room_id"] == room_id

    # 7. Owner marks belonging as recovered
    rec_res = await client.post(f"/api/v1/rooms/{room_id}/recover")
    assert rec_res.status_code == 200
    assert rec_res.json()["status"] == "Recovered"

    # 8. Room is now in Recovered archive
    recovered_rooms = (await client.get("/api/v1/rooms?status=Recovered")).json()
    assert len(recovered_rooms) == 1
    assert recovered_rooms[0]["room_id"] == room_id


@pytest.mark.asyncio
async def test_owner_cannot_access_or_accept_another_owners_room(client: AsyncClient):
    """Security Test: Owner B cannot accept or tamper with Owner A's room."""
    # 1. Owner A registers and gets a contact request
    reg_a = await client.post(
        "/api/v1/auth/register",
        json={"email": "ownera@example.com", "password": "Password123!", "display_name": "Owner A"},
    )
    pub_a = reg_a.json()["public_token"]

    contact = await client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": pub_a,
            "item_name": "Watch",
            "finder_display_name": "Finder",
            "initial_message": "Found watch",
        },
    )
    room_a_id = contact.json()["room_id"]

    # 2. Owner B registers
    await client.post(
        "/api/v1/auth/register",
        json={"email": "ownerb@example.com", "password": "Password123!", "display_name": "Owner B"},
    )

    # 3. Owner B attempts to accept Owner A's room -> 404
    bad_accept = await client.post(f"/api/v1/rooms/{room_a_id}/accept")
    assert bad_accept.status_code == 404
