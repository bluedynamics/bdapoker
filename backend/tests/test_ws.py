import json

import pytest
from starlette.websockets import WebSocketDisconnect

from app.rooms import create_room


def test_websocket_connect_invalid_room(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/rooms/nonexistent/ws"):
            pass
    assert exc_info.value.code == 4004


def test_websocket_welcome(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "welcome"
        assert msg["payload"]["is_moderator"] is True
        assert "participant_id" in msg["payload"]


def test_websocket_welcome_non_moderator(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "welcome"
        assert msg["payload"]["is_moderator"] is False


def test_websocket_join(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        welcome = json.loads(ws.receive_text())
        pid = welcome["payload"]["participant_id"]

        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Alice"}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "room_state"
        assert pid in msg["payload"]["participants"]
        assert msg["payload"]["participants"][pid]["name"] == "Alice"
        assert msg["payload"]["participants"][pid]["role"] == "moderator"


def test_websocket_join_empty_name(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        json.loads(ws.receive_text())  # welcome
        ws.send_text(json.dumps({"type": "join", "payload": {"name": ""}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "Name is required" in msg["payload"]["message"]


def test_websocket_join_as_spectator(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        welcome = json.loads(ws.receive_text())
        pid = welcome["payload"]["participant_id"]

        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Bob", "role": "spectator"}}))
        msg = json.loads(ws.receive_text())
        assert msg["payload"]["participants"][pid]["role"] == "spectator"


def test_websocket_vote_no_round(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        json.loads(ws.receive_text())  # welcome
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Alice"}}))
        json.loads(ws.receive_text())  # room_state
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "No active round" in msg["payload"]["message"]


def test_full_round_flow(client):
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        mod_welcome = json.loads(mod_ws.receive_text())
        mod_pid = mod_welcome["payload"]["participant_id"]

        # Moderator joins
        mod_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Moderator"}}))
        json.loads(mod_ws.receive_text())  # room_state

        # Start a new round
        mod_ws.send_text(json.dumps({
            "type": "new_round",
            "payload": {"story": "User login", "story_link": "https://example.com/123"}
        }))
        state_msg = json.loads(mod_ws.receive_text())
        assert state_msg["payload"]["current_round"]["story"] == "User login"
        assert state_msg["payload"]["current_round"]["round_number"] == 1

        # Moderator votes
        mod_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        state_msg = json.loads(mod_ws.receive_text())
        votes = state_msg["payload"]["current_round"]["votes"]
        assert mod_pid in votes
        # Value should be hidden
        assert "value" not in votes[mod_pid]
        assert votes[mod_pid]["has_voted"] is True

        # Reveal
        mod_ws.send_text(json.dumps({"type": "reveal"}))
        state_msg = json.loads(mod_ws.receive_text())
        assert state_msg["payload"]["current_round"]["revealed"] is True
        votes = state_msg["payload"]["current_round"]["votes"]
        assert votes[mod_pid]["value"] == "5"
        assert "stats" in state_msg["payload"]


def test_reset_round(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())  # welcome
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())  # room_state

        # Start round and vote
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        json.loads(ws.receive_text())  # room_state
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "3"}}))
        json.loads(ws.receive_text())  # room_state

        # Reset
        ws.send_text(json.dumps({"type": "reset_round"}))
        msg = json.loads(ws.receive_text())
        assert msg["payload"]["current_round"]["votes"] == {}
        assert msg["payload"]["current_round"]["revealed"] is False
        assert msg["payload"]["current_round"]["round_number"] == 2


def test_spectator_cannot_vote(client):
    room, token = create_room("fibonacci", "technical")

    # Start round as moderator
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        json.loads(mod_ws.receive_text())
        mod_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(mod_ws.receive_text())
        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        json.loads(mod_ws.receive_text())

        # Spectator connects and tries to vote
        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as spec_ws:
            json.loads(spec_ws.receive_text())  # welcome
            # Moderator also gets a room_state broadcast from spectator connecting? No, spectator hasn't joined yet.
            spec_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Watcher", "role": "spectator"}}))
            json.loads(spec_ws.receive_text())  # room_state for spectator
            json.loads(mod_ws.receive_text())  # room_state broadcast to moderator

            spec_ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
            msg = json.loads(spec_ws.receive_text())
            assert msg["type"] == "error"
            assert "Spectators cannot vote" in msg["payload"]["message"]


def test_non_moderator_cannot_reveal(client):
    room, token = create_room("fibonacci", "technical")

    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        json.loads(mod_ws.receive_text())
        mod_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(mod_ws.receive_text())
        mod_ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        json.loads(mod_ws.receive_text())

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            json.loads(voter_ws.receive_text())  # welcome
            voter_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Voter"}}))
            json.loads(voter_ws.receive_text())  # room_state
            json.loads(mod_ws.receive_text())  # broadcast

            voter_ws.send_text(json.dumps({"type": "reveal"}))
            msg = json.loads(voter_ws.receive_text())
            assert msg["type"] == "error"
            assert "Only moderator" in msg["payload"]["message"]


def test_change_deck(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())

        ws.send_text(json.dumps({
            "type": "change_deck",
            "payload": {"deck_type": "tshirt", "description_flavor": "animals"}
        }))
        msg = json.loads(ws.receive_text())
        assert msg["payload"]["deck_type"] == "tshirt"
        assert msg["payload"]["description_flavor"] == "animals"


def test_change_deck_invalid(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())

        ws.send_text(json.dumps({
            "type": "change_deck",
            "payload": {"deck_type": "invalid"}
        }))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"


def test_kick_participant(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as mod_ws:
        json.loads(mod_ws.receive_text())
        mod_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(mod_ws.receive_text())

        with client.websocket_connect(f"/api/rooms/{room.id}/ws") as voter_ws:
            voter_welcome = json.loads(voter_ws.receive_text())
            voter_pid = voter_welcome["payload"]["participant_id"]
            voter_ws.send_text(json.dumps({"type": "join", "payload": {"name": "Voter"}}))
            json.loads(voter_ws.receive_text())  # room_state
            json.loads(mod_ws.receive_text())  # broadcast

            # Kick
            mod_ws.send_text(json.dumps({"type": "kick", "payload": {"participant_id": voter_pid}}))
            msg = json.loads(mod_ws.receive_text())
            assert voter_pid not in msg["payload"]["participants"]


def test_timer_start_stop(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        json.loads(ws.receive_text())

        ws.send_text(json.dumps({"type": "start_timer", "payload": {"seconds": 60}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "timer_start"
        assert msg["payload"]["seconds"] == 60

        ws.send_text(json.dumps({"type": "stop_timer"}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "timer_stop"


def test_unknown_message_type(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Alice"}}))
        json.loads(ws.receive_text())

        ws.send_text(json.dumps({"type": "unknown_type"}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "Unknown message type" in msg["payload"]["message"]


def test_invalid_json(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        json.loads(ws.receive_text())  # welcome
        ws.send_text("not valid json")
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "Invalid JSON" in msg["payload"]["message"]


def test_new_round_archives_previous(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())

        # Round 1
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Story 1"}}))
        json.loads(ws.receive_text())

        # Round 2 — should archive round 1
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Story 2"}}))
        msg = json.loads(ws.receive_text())
        assert msg["payload"]["current_round"]["story"] == "Story 2"
        assert msg["payload"]["current_round"]["round_number"] == 2


def test_vote_after_reveal_fails(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "new_round", "payload": {"story": "Test"}}))
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "reveal"}))
        json.loads(ws.receive_text())

        # Try to vote after reveal
        ws.send_text(json.dumps({"type": "vote", "payload": {"value": "5"}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "already revealed" in msg["payload"]["message"]


def test_join_invalid_role(client):
    room, _ = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws") as ws:
        json.loads(ws.receive_text())
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Test", "role": "invalid"}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "Invalid role" in msg["payload"]["message"]


def test_kick_self_fails(client):
    room, token = create_room("fibonacci", "technical")
    with client.websocket_connect(f"/api/rooms/{room.id}/ws?token={token}") as ws:
        welcome = json.loads(ws.receive_text())
        pid = welcome["payload"]["participant_id"]
        ws.send_text(json.dumps({"type": "join", "payload": {"name": "Mod"}}))
        json.loads(ws.receive_text())

        ws.send_text(json.dumps({"type": "kick", "payload": {"participant_id": pid}}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert "Cannot kick yourself" in msg["payload"]["message"]
