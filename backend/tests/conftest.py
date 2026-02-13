import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import rooms as rooms_module


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_rooms():
    """Clear all rooms between tests."""
    rooms_module._rooms.clear()
    rooms_module._moderator_tokens.clear()
    rooms_module._reconnect_tokens.clear()
    yield
    rooms_module._rooms.clear()
    rooms_module._moderator_tokens.clear()
    rooms_module._reconnect_tokens.clear()
