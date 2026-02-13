import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.connection_manager import ConnectionManager


@pytest.fixture
def cm():
    return ConnectionManager()


def make_mock_ws():
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


def test_connect_and_get(cm):
    ws = make_mock_ws()
    cm.connect("room1", "p1", ws)
    conns = cm.get_connections("room1")
    assert "p1" in conns
    assert conns["p1"] is ws


def test_disconnect(cm):
    ws = make_mock_ws()
    cm.connect("room1", "p1", ws)
    cm.disconnect("room1", "p1")
    assert cm.get_connections("room1") == {}


def test_disconnect_last_removes_room(cm):
    ws = make_mock_ws()
    cm.connect("room1", "p1", ws)
    cm.disconnect("room1", "p1")
    # Internal dict should be clean
    assert "room1" not in cm._connections


def test_disconnect_nonexistent(cm):
    # Should not raise
    cm.disconnect("room1", "p1")


def test_get_connections_empty(cm):
    assert cm.get_connections("nonexistent") == {}


@pytest.mark.asyncio
async def test_send_to(cm):
    ws = make_mock_ws()
    cm.connect("room1", "p1", ws)
    await cm.send_to("room1", "p1", {"type": "test"})
    ws.send_text.assert_called_once_with(json.dumps({"type": "test"}))


@pytest.mark.asyncio
async def test_send_to_nonexistent(cm):
    # Should not raise
    await cm.send_to("room1", "p1", {"type": "test"})


@pytest.mark.asyncio
async def test_broadcast(cm):
    ws1 = make_mock_ws()
    ws2 = make_mock_ws()
    cm.connect("room1", "p1", ws1)
    cm.connect("room1", "p2", ws2)

    await cm.broadcast("room1", {"type": "update"})
    expected = json.dumps({"type": "update"})
    ws1.send_text.assert_called_once_with(expected)
    ws2.send_text.assert_called_once_with(expected)


@pytest.mark.asyncio
async def test_broadcast_handles_closed_connection(cm):
    ws1 = make_mock_ws()
    ws2 = make_mock_ws()
    ws1.send_text.side_effect = Exception("connection closed")
    cm.connect("room1", "p1", ws1)
    cm.connect("room1", "p2", ws2)

    # Should not raise even though ws1 throws
    await cm.broadcast("room1", {"type": "update"})
    ws2.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_empty_room(cm):
    # Should not raise
    await cm.broadcast("nonexistent", {"type": "test"})
