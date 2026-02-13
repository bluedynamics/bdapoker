import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .decks import DECK_TYPES, FLAVORS, get_all_decks, get_deck_cards
from .models import CreateRoomRequest, CreateRoomResponse
from .rooms import create_room, get_room, periodic_cleanup
from .ws import websocket_endpoint

STATIC_DIR = Path(os.environ.get("STATIC_DIR", "static"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(periodic_cleanup())
    yield
    task.cancel()


app = FastAPI(title="BDA Poker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/rooms", response_model=CreateRoomResponse)
def api_create_room(req: CreateRoomRequest) -> CreateRoomResponse:
    if req.deck_type not in DECK_TYPES:
        raise HTTPException(400, f"Invalid deck_type. Choose from: {DECK_TYPES}")
    if req.description_flavor not in FLAVORS:
        raise HTTPException(400, f"Invalid flavor. Choose from: {FLAVORS}")
    room, token = create_room(req.deck_type, req.description_flavor)
    return CreateRoomResponse(room_id=room.id, moderator_token=token)


@app.get("/api/rooms/{room_id}")
def api_get_room(room_id: str) -> dict:
    room = get_room(room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    deck_cards = get_deck_cards(room.deck_type, room.description_flavor)
    return {
        "id": room.id,
        "deck_type": room.deck_type,
        "description_flavor": room.description_flavor,
        "deck_cards": deck_cards,
        "participant_count": len(room.participants),
    }


@app.get("/api/decks")
def api_get_decks() -> dict:
    return {
        "deck_types": DECK_TYPES,
        "flavors": FLAVORS,
        "decks": get_all_decks(),
    }


@app.websocket("/api/rooms/{room_id}/ws")
async def ws_endpoint(websocket: WebSocket, room_id: str) -> None:
    await websocket_endpoint(websocket, room_id)


# --- Static file serving (production: SvelteKit build output) ---

if STATIC_DIR.is_dir():
    # Serve static assets (JS, CSS, etc.) under /_app/
    app.mount("/_app", StaticFiles(directory=STATIC_DIR / "_app"), name="static_app")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str) -> FileResponse:
        # Try to serve a static file first
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # SPA fallback: serve index.html for all non-API routes
        return FileResponse(STATIC_DIR / "index.html")
