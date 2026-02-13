from datetime import datetime, timezone

from app.models import (
    CreateRoomRequest,
    CreateRoomResponse,
    Participant,
    Role,
    Room,
    Round,
    Vote,
)


def test_participant_defaults():
    p = Participant(id="abc", name="Alice", role=Role.VOTER)
    assert p.connected is True
    assert p.role == "voter"


def test_participant_spectator():
    p = Participant(id="x", name="Bob", role=Role.SPECTATOR)
    assert p.role == "spectator"


def test_vote():
    v = Vote(participant_id="p1", value="5")
    assert v.value == "5"


def test_round_defaults():
    r = Round()
    assert r.story == ""
    assert r.story_link is None
    assert r.votes == {}
    assert r.revealed is False
    assert r.round_number == 1


def test_room_defaults():
    r = Room(id="test123")
    assert r.deck_type == "fibonacci"
    assert r.description_flavor == "technical"
    assert r.participants == {}
    assert r.current_round is None
    assert r.history == []


def test_room_touch():
    r = Room(id="test123")
    old_activity = r.last_activity
    r.touch()
    assert r.last_activity >= old_activity


def test_room_public_state_no_round():
    r = Room(id="test123")
    state = r.public_state([])
    assert state["id"] == "test123"
    assert state["current_round"] is None
    assert state["participants"] == {}


def test_room_public_state_with_unrevealed_votes():
    r = Room(id="test123")
    r.participants["p1"] = Participant(id="p1", name="Alice", role=Role.VOTER)
    r.current_round = Round(
        story="Test story",
        votes={"p1": Vote(participant_id="p1", value="5")},
    )
    state = r.public_state([])
    votes = state["current_round"]["votes"]
    # Should NOT expose the value
    assert "value" not in votes["p1"]
    assert votes["p1"]["has_voted"] is True


def test_room_public_state_with_revealed_votes():
    r = Room(id="test123")
    r.participants["p1"] = Participant(id="p1", name="Alice", role=Role.VOTER)
    r.current_round = Round(
        story="Test story",
        votes={"p1": Vote(participant_id="p1", value="5")},
        revealed=True,
    )
    state = r.public_state([])
    votes = state["current_round"]["votes"]
    assert votes["p1"]["value"] == "5"


def test_create_room_request_defaults():
    req = CreateRoomRequest()
    assert req.deck_type == "fibonacci"
    assert req.description_flavor == "technical"


def test_create_room_response():
    resp = CreateRoomResponse(room_id="abc", moderator_token="tok")
    assert resp.room_id == "abc"
