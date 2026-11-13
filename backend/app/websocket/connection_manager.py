from typing import Dict, List, Tuple
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps room_id (as str) to list of (WebSocket, participant_id, role: 'owner'|'finder')
        self.active_rooms: Dict[str, List[Tuple[WebSocket, str, str]]] = {}

    async def connect(self, room_id: str, websocket: WebSocket, participant_id: str, role: str):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
        self.active_rooms[room_id].append((websocket, participant_id, role))

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_rooms:
            self.active_rooms[room_id] = [
                conn for conn in self.active_rooms[room_id] if conn[0] != websocket
            ]
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_rooms:
            for connection, _, _ in list(self.active_rooms[room_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def close_room(self, room_id: str, reason: str = "Room has been closed"):
        if room_id in self.active_rooms:
            for connection, _, _ in list(self.active_rooms[room_id]):
                try:
                    await connection.send_json({
                        "type": "ROOM_TERMINATED",
                        "reason": reason,
                    })
                    await connection.close(code=1000)
                except Exception:
                    pass
            del self.active_rooms[room_id]


manager = ConnectionManager()
