from datetime import datetime, timedelta, timezone

from app.rooms import (
    _moderator_tokens,
    _rooms,
    cleanup_expired_rooms,
    create_room,
    delete_room,
    get_moderator_token,
    get_room,
)


def test_create_room():
    room, token = create_room("fibonacci", "technical")
    assert room.id in _rooms
    assert room.deck_type == "fibonacci"
    assert room.description_flavor == "technical"
    assert len(token) > 0
    assert get_moderator_token(room.id) == token


def test_get_room():
    room, _ = create_room("tshirt", "animals")
    fetched = get_room(room.id)
    assert fetched is not None
    assert fetched.id == room.id


def test_get_room_nonexistent():
    assert get_room("nonexistent") is None


def test_get_moderator_token_nonexistent():
    assert get_moderator_token("nonexistent") is None


def test_delete_room():
    room, _ = create_room("fibonacci", "technical")
    rid = room.id
    delete_room(rid)
    assert get_room(rid) is None
    assert get_moderator_token(rid) is None


def test_delete_room_nonexistent():
    # Should not raise
    delete_room("nonexistent")


def test_cleanup_expired_rooms():
    room1, _ = create_room("fibonacci", "technical")
    room2, _ = create_room("tshirt", "idioms")

    # Make room1 expired
    _rooms[room1.id].last_activity = datetime.now(timezone.utc) - timedelta(hours=5)

    removed = cleanup_expired_rooms()
    assert removed == 1
    assert get_room(room1.id) is None
    assert get_room(room2.id) is not None


def test_cleanup_no_expired():
    create_room("fibonacci", "technical")
    removed = cleanup_expired_rooms()
    assert removed == 0


def test_room_ids_are_short():
    room, _ = create_room("fibonacci", "technical")
    assert len(room.id) == 8
