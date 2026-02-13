from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Tracks WebSocket connections per room."""

    def __init__(self) -> None:
        # room_id -> {participant_id -> websocket}
        self._connections: dict[str, dict[str, WebSocket]] = {}

    def connect(self, room_id: str, participant_id: str, ws: WebSocket) -> None:
        if room_id not in self._connections:
            self._connections[room_id] = {}
        existing = self._connections[room_id].get(participant_id)
        if existing is not None and existing is not ws:
            asyncio.create_task(self._close_stale(existing))
        self._connections[room_id][participant_id] = ws

    async def _close_stale(self, ws: WebSocket) -> None:
        try:
            await ws.close(code=4001, reason="Reconnected from another session")
        except Exception:
            pass

    def disconnect(self, room_id: str, participant_id: str) -> None:
        conns = self._connections.get(room_id)
        if conns:
            conns.pop(participant_id, None)
            if not conns:
                del self._connections[room_id]

    async def send_to(
        self, room_id: str, participant_id: str, message: dict[str, Any]
    ) -> None:
        conns = self._connections.get(room_id, {})
        ws = conns.get(participant_id)
        if ws:
            await ws.send_text(json.dumps(message))

    async def broadcast(self, room_id: str, message: dict[str, Any]) -> None:
        conns = self._connections.get(room_id, {})
        data = json.dumps(message)
        for ws in list(conns.values()):
            try:
                await ws.send_text(data)
            except Exception:
                pass  # connection already closed

    def get_connections(self, room_id: str) -> dict[str, WebSocket]:
        return self._connections.get(room_id, {})


manager = ConnectionManager()
