from __future__ import annotations

import json
import math
import statistics
from typing import Any

import shortuuid
from fastapi import WebSocket, WebSocketDisconnect

from .connection_manager import manager
from .decks import get_deck_cards
from .models import Participant, Role, Round, Vote
from .rooms import (
    create_reconnect_token,
    get_moderator_token,
    get_reconnect_token,
    get_room,
    remove_reconnect_token,
    validate_reconnect_token,
)


async def _broadcast_state(room_id: str) -> None:
    room = get_room(room_id)
    if room is None:
        return
    deck_cards = get_deck_cards(room.deck_type, room.description_flavor)
    state = room.public_state(deck_cards)
    await manager.broadcast(room_id, {"type": "room_state", "payload": state})


async def _send_error(room_id: str, participant_id: str, message: str) -> None:
    await manager.send_to(
        room_id, participant_id, {"type": "error", "payload": {"message": message}}
    )


def _is_moderator(room_id: str, participant_id: str) -> bool:
    room = get_room(room_id)
    if room is None:
        return False
    p = room.participants.get(participant_id)
    return p is not None and p.role == Role.MODERATOR


def _compute_stats(votes: dict[str, Vote]) -> dict[str, Any]:
    """Compute average, median, and outlier info from numeric votes."""
    numeric_values: list[float] = []
    for v in votes.values():
        try:
            fval = float(v.value)
        except (ValueError, TypeError):
            continue  # skip ?, coffee, etc.
        if not math.isfinite(fval):
            continue  # skip infinity, -infinity, NaN
        numeric_values.append(fval)

    if not numeric_values:
        return {}

    avg = statistics.mean(numeric_values)
    med = statistics.median(numeric_values)
    result: dict[str, Any] = {
        "average": round(avg, 1),
        "median": round(med, 1),
        "min": min(numeric_values),
        "max": max(numeric_values),
    }
    if len(numeric_values) >= 2:
        result["consensus"] = len(set(numeric_values)) == 1
    return result


async def handle_message(
    room_id: str, participant_id: str, raw: str, *, is_moderator: bool = False
) -> None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        await _send_error(room_id, participant_id, "Invalid JSON")
        return

    msg_type = data.get("type")
    payload = data.get("payload", {})
    room = get_room(room_id)
    if room is None:
        await _send_error(room_id, participant_id, "Room not found")
        return

    room.touch()

    if msg_type == "join":
        await _handle_join(room, participant_id, payload, is_moderator=is_moderator)
    elif msg_type == "vote":
        await _handle_vote(room, participant_id, payload)
    elif msg_type == "reveal":
        await _handle_reveal(room, participant_id)
    elif msg_type == "new_round":
        await _handle_new_round(room, participant_id, payload)
    elif msg_type == "reset_round":
        await _handle_reset_round(room, participant_id)
    elif msg_type == "kick":
        await _handle_kick(room, participant_id, payload)
    elif msg_type == "change_deck":
        await _handle_change_deck(room, participant_id, payload)
    elif msg_type == "start_timer":
        await _handle_start_timer(room, participant_id, payload)
    elif msg_type == "stop_timer":
        await _handle_stop_timer(room, participant_id)
    else:
        await _send_error(room.id, participant_id, f"Unknown message type: {msg_type}")


async def _handle_join(
    room: Any, participant_id: str, payload: dict, *, is_moderator: bool = False
) -> None:
    name = payload.get("name", "").strip()
    if not name:
        await _send_error(room.id, participant_id, "Name is required")
        return

    if is_moderator:
        role = Role.MODERATOR
    else:
        role_str = payload.get("role", "voter")
        try:
            role = Role(role_str)
        except ValueError:
            await _send_error(room.id, participant_id, f"Invalid role: {role_str}")
            return
        # Don't allow joining as moderator via message
        if role == Role.MODERATOR:
            role = Role.VOTER

    room.participants[participant_id] = Participant(
        id=participant_id, name=name, role=role
    )
    await _broadcast_state(room.id)

    # Issue reconnect token so participant can reclaim identity after disconnect
    token = create_reconnect_token(room.id, participant_id)
    await manager.send_to(
        room.id,
        participant_id,
        {"type": "reconnect_token", "payload": {"reconnect_token": token}},
    )


async def _handle_vote(room: Any, participant_id: str, payload: dict) -> None:
    if room.current_round is None:
        await _send_error(room.id, participant_id, "No active round")
        return
    if room.current_round.revealed:
        await _send_error(room.id, participant_id, "Round already revealed")
        return
    p = room.participants.get(participant_id)
    if p is None:
        await _send_error(room.id, participant_id, "Not in room")
        return
    if p.role == Role.SPECTATOR:
        await _send_error(room.id, participant_id, "Spectators cannot vote")
        return
    value = payload.get("value", "")
    room.current_round.votes[participant_id] = Vote(
        participant_id=participant_id, value=value
    )
    await _broadcast_state(room.id)


async def _handle_reveal(room: Any, participant_id: str) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can reveal")
        return
    if room.current_round is None:
        await _send_error(room.id, participant_id, "No active round")
        return
    room.current_round.revealed = True
    # Compute and attach stats
    stats = _compute_stats(room.current_round.votes)
    await manager.broadcast(
        room.id,
        {
            "type": "room_state",
            "payload": {
                **room.public_state(
                    get_deck_cards(room.deck_type, room.description_flavor)
                ),
                "stats": stats,
            },
        },
    )


async def _handle_new_round(
    room: Any, participant_id: str, payload: dict
) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can start new round")
        return
    # Archive current round
    round_number = 1
    if room.current_round:
        room.history.append(room.current_round)
        round_number = room.current_round.round_number + 1
    room.current_round = Round(
        story=payload.get("story", ""),
        story_link=payload.get("story_link"),
        round_number=round_number,
    )
    await _broadcast_state(room.id)


async def _handle_reset_round(room: Any, participant_id: str) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can reset round")
        return
    if room.current_round is None:
        await _send_error(room.id, participant_id, "No active round")
        return
    room.current_round.votes = {}
    room.current_round.revealed = False
    room.current_round.round_number += 1
    await _broadcast_state(room.id)


async def _handle_kick(room: Any, participant_id: str, payload: dict) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can kick")
        return
    target_id = payload.get("participant_id", "")
    if target_id == participant_id:
        await _send_error(room.id, participant_id, "Cannot kick yourself")
        return
    room.participants.pop(target_id, None)
    if room.current_round:
        room.current_round.votes.pop(target_id, None)
    remove_reconnect_token(room.id, target_id)
    manager.disconnect(room.id, target_id)
    await _broadcast_state(room.id)


async def _handle_change_deck(
    room: Any, participant_id: str, payload: dict
) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can change deck")
        return
    deck_type = payload.get("deck_type", room.deck_type)
    flavor = payload.get("description_flavor", room.description_flavor)
    # Validate
    try:
        get_deck_cards(deck_type, flavor)
    except ValueError as e:
        await _send_error(room.id, participant_id, str(e))
        return
    room.deck_type = deck_type
    room.description_flavor = flavor
    await _broadcast_state(room.id)


async def _handle_start_timer(
    room: Any, participant_id: str, payload: dict
) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can start timer")
        return
    seconds = payload.get("seconds", 60)
    await manager.broadcast(
        room.id, {"type": "timer_start", "payload": {"seconds": seconds}}
    )


async def _handle_stop_timer(room: Any, participant_id: str) -> None:
    if not _is_moderator(room.id, participant_id):
        await _send_error(room.id, participant_id, "Only moderator can stop timer")
        return
    await manager.broadcast(room.id, {"type": "timer_stop", "payload": {}})


async def websocket_endpoint(websocket: WebSocket, room_id: str) -> None:
    room = get_room(room_id)
    if room is None:
        await websocket.close(code=4004, reason="Room not found")
        return

    await websocket.accept()

    # --- Reconnect attempt ---
    reconnect_id = websocket.query_params.get("reconnect_id")
    reconnect_token = websocket.query_params.get("reconnect_token")
    reconnected = False

    if (
        reconnect_id
        and reconnect_token
        and validate_reconnect_token(room_id, reconnect_id, reconnect_token)
        and reconnect_id in room.participants
    ):
        participant_id = reconnect_id
        reconnected = True
    else:
        participant_id = shortuuid.uuid()[:10]

    # Moderator check: for reconnects derive from stored role,
    # for new connections check the mod token query param.
    if reconnected:
        is_mod = room.participants[participant_id].role == Role.MODERATOR
    else:
        mod_token = websocket.query_params.get("token")
        is_mod = mod_token is not None and mod_token == get_moderator_token(room_id)

    manager.connect(room_id, participant_id, websocket)

    if reconnected:
        room.participants[participant_id].connected = True
        existing_token = get_reconnect_token(room_id, participant_id)
        await websocket.send_text(
            json.dumps(
                {
                    "type": "welcome",
                    "payload": {
                        "participant_id": participant_id,
                        "is_moderator": is_mod,
                        "reconnected": True,
                        "reconnect_token": existing_token,
                    },
                }
            )
        )
        await _broadcast_state(room_id)
    else:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "welcome",
                    "payload": {
                        "participant_id": participant_id,
                        "is_moderator": is_mod,
                        "reconnected": False,
                    },
                }
            )
        )

    try:
        while True:
            raw = await websocket.receive_text()
            await handle_message(room_id, participant_id, raw, is_moderator=is_mod)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room_id, participant_id)
        room = get_room(room_id)
        if room and participant_id in room.participants:
            room.participants[participant_id].connected = False
            await _broadcast_state(room_id)
