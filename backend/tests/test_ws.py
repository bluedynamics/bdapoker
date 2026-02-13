import json

import pytest
from starlette.websockets import WebSocketDisconnect

from app.rooms import create_room


def _recv(ws):
    """Read and parse one WebSocket message."""
    return json.loads(ws.receive_text())


def _join(ws, name, role=None):
    """Send join, consume room_state + reconnect_token. Return (state, reconnect_token)."""
    payload = {"name": name}
    if role:
        payload["role"] = role
    ws.send_text(json.dumps({"type": "join", "payload": payload}))
    state = _recv(ws)
    assert state["type"] == "room_state"
    token_msg = _recv(ws)
    assert token_msg["type"] == "reconnect_token"
    return state, token_msg["payload"]["reconnect_token"]


def test_websocket_connect_invalid_room(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/rooms/nonexistent/ws"):
            pass
    assert exc_info.value.code == 4004


def test_websocket_welcome(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        msg = _recv(ws)
        assert msg["type"] == "welcome"
        assert msg["payload"]["is_moderator"] is True
        assert msg["payload"]["reconnected"] is False
        assert "participant_id" in msg["payload"]


def test_websocket_welcome_non_moderator(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        msg = _recv(ws)
        assert msg["type"] == "welcome"
        assert msg["payload"]["is_moderator"] is False


def test_websocket_join(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]

        state, reconnect_token = _join(ws, "Alice")
        assert pid in state["payload"]["participants"]
        assert state["payload"]["participants"][pid]["name"] == "Alice"
        assert state["payload"]["participants"][pid]["role"] == "moderator"
        assert reconnect_token  # non-empty


def test_websocket_join_empty_name(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        _recv(ws)  # welcome
        ws.send_text(json.dumps({"type": "join", "payload": {"name": ""}}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "Name is required" in msg["payload"]["message"]


def test_websocket_join_as_spectator(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]

        state, _ = _join(ws, "Bob", role="spectator")
        assert state["payload"]["participants"][pid]["role"] == "spectator"


def test_websocket_vote_no_round(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        _recv(ws)  # welcome
        _join(ws, "Alice")
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "No active round" in msg["payload"]["message"]


def test_full_round_flow(client):
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        mod_welcome = _recv(mod_ws)
        mod_pid = mod_welcome["payload"]["participant_id"]

        # Moderator joins
        _join(mod_ws, "Moderator")

        # Start a new round
        mod_ws.send_text(json.dumps({
            "type": "new_round",
            "payload": {"story": "User login", "story_link": "https://example.com/123"}
        }))
        state_msg = _recv(mod_ws)
        assert state_msg["payload"]["current_round"]["story"] == "User login"
        assert state_msg["payload"]["current_round"]["round_number"] == 1

        # Moderator votes
        mod_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        state_msg = _recv(mod_ws)
        votes = state_msg["payload"]["current_round"]["votes"]
        assert mod_pid in votes
        # Value should be hidden
        assert "value" not in votes[mod_pid]
        assert votes[mod_pid]["has_voted"] is True

        # Reveal
        mod_ws.send_text(json.dumps({"type": "reveal"}))
        state_msg = _recv(mod_ws)
        assert state_msg["payload"]["current_round"]["revealed"] is True
        votes = state_msg["payload"]["current_round"]["votes"]
        assert votes[mod_pid]["value"] == "5"
        assert "stats" in state_msg["payload"]


def test_reset_round(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)  # welcome
        _join(ws, "Mod")

        # Start round and vote
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(ws)  # room_state
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "3"}}))
        _recv(ws)  # room_state

        # Reset
        ws.send_text(json.dumps({"type": "reset_round"}))
        msg = _recv(ws)
        assert msg["payload"]["current_round"]["votes"] == {}
        assert msg["payload"]["current_round"]["revealed"] is False
        assert msg["payload"]["current_round"]["round_number"] == 2


def test_spectator_cannot_vote(client):
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)
        _join(mod_ws, "Mod")
        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(mod_ws)

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as spec_ws:
            _recv(spec_ws)  # welcome
            _join(spec_ws, "Watcher", role="spectator")
            _recv(mod_ws)  # broadcast to moderator

            spec_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
            msg = _recv(spec_ws)
            assert msg["type"] == "error"
            assert "Spectators cannot vote" in msg["payload"]["message"]


def test_non_moderator_cannot_reveal(client):
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)
        _join(mod_ws, "Mod")
        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(mod_ws)

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            _recv(voter_ws)  # welcome
            _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            voter_ws.send_text(json.dumps({"type": "reveal"}))
            msg = _recv(voter_ws)
            assert msg["type"] == "error"
            assert "Only moderator" in msg["payload"]["message"]


def test_change_deck(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)
        _join(ws, "Mod")

        ws.send_text(json.dumps({
            "type": "change_deck",
            "payload": {"deck_type": "tshirt", "description_flavor": "animals"}
        }))
        msg = _recv(ws)
        assert msg["payload"]["deck_type"] == "tshirt"
        assert msg["payload"]["description_flavor"] == "animals"


def test_change_deck_invalid(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)
        _join(ws, "Mod")

        ws.send_text(json.dumps({
            "type": "change_deck",
            "payload": {"deck_type": "invalid"}
        }))
        msg = _recv(ws)
        assert msg["type"] == "error"


def test_kick_participant(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)
        _join(mod_ws, "Mod")

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            voter_welcome = _recv(voter_ws)
            voter_pid = voter_welcome["payload"]["participant_id"]
            _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            # Kick
            mod_ws.send_text(json.dumps({"type": "kick", "payload": {"participant_id": voter_pid}}))
            msg = _recv(mod_ws)
            assert voter_pid not in msg["payload"]["participants"]


def test_timer_start_stop(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)
        _join(ws, "Mod")
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(ws)

        ws.send_text(json.dumps({"type": "start_timer", "payload": {"seconds": 60}}))
        msg = _recv(ws)
        assert msg["type"] == "timer_start"
        assert msg["payload"]["seconds"] == 60

        ws.send_text(json.dumps({"type": "stop_timer"}))
        msg = _recv(ws)
        assert msg["type"] == "timer_stop"


def test_unknown_message_type(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        _recv(ws)
        _join(ws, "Alice")

        ws.send_text(json.dumps({"type": "unknown_type"}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "Unknown message type" in msg["payload"]["message"]


def test_invalid_json(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        _recv(ws)  # welcome
        ws.send_text("not valid json")
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "Invalid JSON" in msg["payload"]["message"]


def test_new_round_archives_previous(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)
        _join(ws, "Mod")

        # Round 1
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Story 1"}}))
        _recv(ws)

        # Round 2 — should archive round 1
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Story 2"}}))
        msg = _recv(ws)
        assert msg["payload"]["current_round"]["story"] == "Story 2"
        assert msg["payload"]["current_round"]["round_number"] == 2


def test_vote_after_reveal_fails(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        _recv(ws)
        _join(ws, "Mod")
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(ws)
        ws.send_text(json.dumps({"type": "reveal"}))
        _recv(ws)

        # Try to vote after reveal
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "already revealed" in msg["payload"]["message"]


def test_join_invalid_role(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        _recv(ws)
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Test", "role": "invalid"}}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "Invalid role" in msg["payload"]["message"]


def test_kick_self_fails(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]
        _join(ws, "Mod")

        ws.send_text(json.dumps({"type": "kick", "payload": {"participant_id": pid}}))
        msg = _recv(ws)
        assert msg["type"] == "error"
        assert "Cannot kick yourself" in msg["payload"]["message"]


# --- Special vote tests ---


def _reveal_with_special_vote(client, special_value, numeric_value="5"):
    """Helper: one voter votes numeric, another votes a special card, then reveal."""
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)  # welcome
        _join(mod_ws, "Mod")

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            _recv(voter_ws)  # welcome
            _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            # Start round
            mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
            _recv(mod_ws)
            _recv(voter_ws)

            # Mod votes numeric, voter votes special
            mod_ws.send_text(json.dumps({"type": "vote", "payload": {"value": numeric_value}}))
            _recv(mod_ws)
            _recv(voter_ws)

            voter_ws.send_text(json.dumps({"type": "vote", "payload": {"value": special_value}}))
            _recv(voter_ws)
            _recv(mod_ws)

            # Reveal
            mod_ws.send_text(json.dumps({"type": "reveal"}))
            msg = _recv(mod_ws)
            assert msg["type"] == "room_state"
            assert msg["payload"]["current_round"]["revealed"] is True
            return msg["payload"]


def test_reveal_with_infinity_vote(client):
    """Infinity votes must be excluded from stats (float('infinity') is valid Python)."""
    payload = _reveal_with_special_vote(client, "infinity")
    stats = payload["stats"]
    assert stats["average"] == 5.0
    assert stats["median"] == 5.0


def test_reveal_with_question_mark_vote(client):
    """'?' votes should be excluded from stats."""
    payload = _reveal_with_special_vote(client, "?")
    stats = payload["stats"]
    assert stats["average"] == 5.0
    assert stats["median"] == 5.0


def test_reveal_with_coffee_vote(client):
    """'coffee' votes should be excluded from stats."""
    payload = _reveal_with_special_vote(client, "coffee")
    stats = payload["stats"]
    assert stats["average"] == 5.0
    assert stats["median"] == 5.0


def test_reveal_all_special_votes(client):
    """When all votes are non-numeric, stats should be empty."""
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)  # welcome
        _join(mod_ws, "Mod")

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            _recv(voter_ws)  # welcome
            _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
            _recv(mod_ws)
            _recv(voter_ws)

            # Both vote special
            mod_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "?"}}))
            _recv(mod_ws)
            _recv(voter_ws)

            voter_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "infinity"}}))
            _recv(voter_ws)
            _recv(mod_ws)

            mod_ws.send_text(json.dumps({"type": "reveal"}))
            msg = _recv(mod_ws)
            assert msg["payload"]["current_round"]["revealed"] is True
            assert msg["payload"]["stats"] == {}


def test_reveal_with_tshirt_votes(client):
    """T-shirt size votes (non-numeric) should be excluded from stats."""
    room, token = create_room("tshirt", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)  # welcome
        _join(mod_ws, "Mod")

        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(mod_ws)

        mod_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "xl"}}))
        _recv(mod_ws)

        mod_ws.send_text(json.dumps({"type": "reveal"}))
        msg = _recv(mod_ws)
        assert msg["payload"]["current_round"]["revealed"] is True
        assert msg["payload"]["stats"] == {}


# --- Reconnect tests ---


def test_reconnect_with_valid_token(client):
    """Participant can reconnect and reclaim their identity."""
    room, _ = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]
        _, reconnect_token = _join(ws, "Alice")

    # Participant disconnected
    assert room.participants[pid].connected is False

    # Reconnect with token
    url = f"/api/rooms/{room.id}/ws?reconnect_id={pid}&reconnect_token={reconnect_token}"
    with client.websocket_connect(url) as ws:
        welcome = _recv(ws)
        assert welcome["payload"]["participant_id"] == pid
        assert welcome["payload"]["reconnected"] is True
        assert welcome["payload"]["reconnect_token"] == reconnect_token
        # Should receive room_state broadcast (connected again)
        state = _recv(ws)
        assert state["type"] == "room_state"
        assert state["payload"]["participants"][pid]["connected"] is True


def test_reconnect_with_invalid_token(client):
    """Invalid reconnect token falls through to new participant."""
    room, _ = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]
        _join(ws, "Alice")

    # Reconnect with wrong token
    url = f"/api/rooms/{room.id}/ws?reconnect_id={pid}&reconnect_token=wrong"
    with client.websocket_connect(url) as ws:
        welcome = _recv(ws)
        assert welcome["payload"]["participant_id"] != pid
        assert welcome["payload"]["reconnected"] is False


def test_moderator_reconnect_preserves_role(client):
    """Moderator reconnecting keeps moderator status without needing mod token."""
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        welcome = _recv(ws)
        pid = welcome["payload"]["participant_id"]
        assert welcome["payload"]["is_moderator"] is True
        _, reconnect_token = _join(ws, "Mod")

    # Reconnect with reconnect token only (no mod token needed)
    url = f"/api/rooms/{room.id}/ws?reconnect_id={pid}&reconnect_token={reconnect_token}"
    with client.websocket_connect(url) as ws:
        welcome = _recv(ws)
        assert welcome["payload"]["participant_id"] == pid
        assert welcome["payload"]["is_moderator"] is True
        assert welcome["payload"]["reconnected"] is True


def test_reconnect_preserves_vote(client):
    """Reconnected participant's vote is still visible."""
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)
        _join(mod_ws, "Mod")

        # Start round
        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        _recv(mod_ws)

        # Voter joins and votes
        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            voter_welcome = _recv(voter_ws)
            voter_pid = voter_welcome["payload"]["participant_id"]
            _, voter_reconnect = _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            voter_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "8"}}))
            _recv(voter_ws)
            _recv(mod_ws)

        # Voter disconnected — reconnect
        _recv(mod_ws)  # disconnect broadcast
        url = f"/api/rooms/{room.id}/ws?reconnect_id={voter_pid}&reconnect_token={voter_reconnect}"
        with client.websocket_connect(url) as voter_ws:
            welcome = _recv(voter_ws)
            assert welcome["payload"]["participant_id"] == voter_pid
            state = _recv(voter_ws)  # room_state broadcast
            _recv(mod_ws)  # reconnect broadcast
            # Vote should still be there (hidden since not revealed)
            assert voter_pid in state["payload"]["current_round"]["votes"]

            # Moderator reveals — voter's vote shows
            mod_ws.send_text(json.dumps({"type": "reveal"}))
            reveal_msg = _recv(mod_ws)
            assert reveal_msg["payload"]["current_round"]["votes"][voter_pid]["value"] == "8"


def test_kicked_participant_cannot_reconnect(client):
    """Kicked participant's reconnect token is invalidated."""
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        _recv(mod_ws)
        _join(mod_ws, "Mod")

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            voter_welcome = _recv(voter_ws)
            voter_pid = voter_welcome["payload"]["participant_id"]
            _, voter_reconnect = _join(voter_ws, "Voter")
            _recv(mod_ws)  # broadcast

            # Kick the voter
            mod_ws.send_text(json.dumps({"type": "kick", "payload": {"participant_id": voter_pid}}))
            _recv(mod_ws)  # room_state

        # Voter tries to reconnect with old token
        url = f"/api/rooms/{room.id}/ws?reconnect_id={voter_pid}&reconnect_token={voter_reconnect}"
        with client.websocket_connect(url) as ws:
            welcome = _recv(ws)
            # Should get a new ID, not the kicked one
            assert welcome["payload"]["participant_id"] != voter_pid
            assert welcome["payload"]["reconnected"] is False
