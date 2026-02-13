from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import shortuuid

from .models import Room

ROOM_EXPIRY_SECONDS = 4 * 60 * 60  # 4 hours

# In-memory store: room_id -> Room
_rooms: dict[str, Room] = {}

# Moderator tokens: room_id -> token (used to authenticate the creator)
_moderator_tokens: dict[str, str] = {}

# Reconnect tokens: (room_id, participant_id) -> token
_reconnect_tokens: dict[tuple[str, str], str] = {}


def create_room(deck_type: str, description_flavor: str) -> tuple[Room, str]:
    """Create a new room and return (room, moderator_token)."""
    room_id = shortuuid.uuid()[:8]
    token = shortuuid.uuid()
    now = datetime.now(timezone.utc)
    room = Room(
        id=room_id,
        deck_type=deck_type,
        description_flavor=description_flavor,
        created_at=now,
        last_activity=now,
    )
    _rooms[room_id] = room
    _moderator_tokens[room_id] = token
    return room, token


def get_room(room_id: str) -> Room | None:
    return _rooms.get(room_id)


def get_moderator_token(room_id: str) -> str | None:
    return _moderator_tokens.get(room_id)


def create_reconnect_token(room_id: str, participant_id: str) -> str:
    """Generate and store a reconnect token for a participant."""
    token = shortuuid.uuid()
    _reconnect_tokens[(room_id, participant_id)] = token
    return token


def validate_reconnect_token(
    room_id: str, participant_id: str, token: str
) -> bool:
    """Check if a reconnect token is valid."""
    stored = _reconnect_tokens.get((room_id, participant_id))
    return stored is not None and stored == token


def get_reconnect_token(room_id: str, participant_id: str) -> str | None:
    return _reconnect_tokens.get((room_id, participant_id))


def remove_reconnect_token(room_id: str, participant_id: str) -> None:
    _reconnect_tokens.pop((room_id, participant_id), None)


def delete_room(room_id: str) -> None:
    _rooms.pop(room_id, None)
    _moderator_tokens.pop(room_id, None)
    keys_to_remove = [k for k in _reconnect_tokens if k[0] == room_id]
    for k in keys_to_remove:
        del _reconnect_tokens[k]


def cleanup_expired_rooms() -> int:
    """Remove rooms inactive for longer than ROOM_EXPIRY_SECONDS. Returns count removed."""
    now = datetime.now(timezone.utc)
    expired = [
        rid
        for rid, room in _rooms.items()
        if (now - room.last_activity).total_seconds() > ROOM_EXPIRY_SECONDS
    ]
    for rid in expired:
        delete_room(rid)
    return len(expired)


async def periodic_cleanup(interval: int = 300) -> None:
    """Background task that cleans up expired rooms every `interval` seconds."""
    while True:
        await asyncio.sleep(interval)
        cleanup_expired_rooms()
