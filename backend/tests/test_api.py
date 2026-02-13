def test_create_room(client):
    resp = client.post("/api/rooms", json={"deck_type": "fibonacci", "description_flavor": "technical"})
    assert resp.status_code == 200
    data = resp.json()
    assert "room_id" in data
    assert "moderator_token" in data


def test_create_room_defaults(client):
    resp = client.post("/api/rooms", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "room_id" in data


def test_create_room_invalid_deck(client):
    resp = client.post("/api/rooms", json={"deck_type": "invalid"})
    assert resp.status_code == 400


def test_create_room_invalid_flavor(client):
    resp = client.post("/api/rooms", json={"description_flavor": "invalid"})
    assert resp.status_code == 400


def test_get_room(client):
    create_resp = client.post("/api/rooms", json={})
    room_id = create_resp.json()["room_id"]

    resp = client.get(f"/api/rooms/{room_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == room_id
    assert data["deck_type"] == "fibonacci"
    assert "deck_cards" in data
    assert len(data["deck_cards"]) > 0


def test_get_room_not_found(client):
    resp = client.get("/api/rooms/nonexistent")
    assert resp.status_code == 404


def test_get_decks(client):
    resp = client.get("/api/decks")
    assert resp.status_code == 200
    data = resp.json()
    assert "deck_types" in data
    assert "flavors" in data
    assert "decks" in data
    assert "fibonacci" in data["decks"]
    assert "technical" in data["decks"]["fibonacci"]
