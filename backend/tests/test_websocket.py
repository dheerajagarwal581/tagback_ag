import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_websocket_lifecycle_and_messaging_rules(sync_client: TestClient):
    """Test full WebSocket flow: handshake auth -> pending reply block -> acceptance -> live chat."""
    owner_client = sync_client
    finder_client = TestClient(app)
    unauth_client = TestClient(app)

    # 1. Register Owner
    reg = owner_client.post(
        "/api/v1/auth/register",
        json={"email": "ws_owner@example.com", "password": "Password123!", "display_name": "WS Owner"},
    )
    assert reg.status_code == 201
    public_token = reg.json()["public_token"]

    # 2. Finder submits report -> creates Pending room
    contact = finder_client.post(
        "/api/v1/contact/submit",
        json={
            "public_token": public_token,
            "item_name": "Camera",
            "finder_display_name": "Finder Bob",
            "initial_message": "Found Nikon camera",
        },
    )
    assert contact.status_code == 201
    room_id = contact.json()["room_id"]

    # 3. Unauthorized WebSocket connection receives 4403
    with pytest.raises(Exception):
        with unauth_client.websocket_connect(f"/api/v1/ws/room/{room_id}") as ws:
            pass

    # 4. Finder connects via WebSocket (Pending state)
    with finder_client.websocket_connect(f"/api/v1/ws/room/{room_id}") as finder_ws:
        # Finder can send while Pending
        finder_ws.send_json({"type": "SEND_MESSAGE", "content": "I am waiting by the gate."})
        res_frame = finder_ws.receive_json()
        assert res_frame["type"] == "NEW_MESSAGE"
        assert res_frame["message"]["content"] == "I am waiting by the gate."
        assert res_frame["message"]["sender_type"] == "finder"

    # 5. Owner connects while Pending and attempts to send reply -> BLOCKED with CANNOT_REPLY_PENDING
    with owner_client.websocket_connect(f"/api/v1/ws/room/{room_id}") as owner_ws:
        owner_ws.send_json({"type": "SEND_MESSAGE", "content": "On my way!"})
        err_frame = owner_ws.receive_json()
        assert err_frame["type"] == "ERROR"
        assert err_frame["code"] == "CANNOT_REPLY_PENDING"

    # 6. Owner accepts request -> changes to Active
    accept_res = owner_client.post(f"/api/v1/rooms/{room_id}/accept")
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "Active"

    # 7. Now Owner connects and sends message in Active state -> SUCCEEDS!
    with owner_client.websocket_connect(f"/api/v1/ws/room/{room_id}") as owner_ws:
        owner_ws.send_json({"type": "SEND_MESSAGE", "content": "Thanks! Heading to the gate now."})
        owner_msg_frame = owner_ws.receive_json()
        assert owner_msg_frame["type"] == "NEW_MESSAGE"
        assert owner_msg_frame["message"]["content"] == "Thanks! Heading to the gate now."
        assert owner_msg_frame["message"]["sender_type"] == "owner"
