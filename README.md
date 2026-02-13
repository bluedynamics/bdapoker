# BDA Poker

A planning poker web application for agile estimation sessions. Share a link, join a room, vote simultaneously, discuss.

## Features

- **Link-only joining** — no accounts, no signup. Create a room, share the URL.
- **Simultaneous reveal** — votes are hidden until the moderator reveals them, preventing anchoring bias.
- **Multiple deck types** — Fibonacci (0–100), T-shirt (XS–XXL), Powers of 2 (1–64).
- **Card description flavors** — each card value comes with a description to help calibrate estimates:
  - *Technical* — straightforward complexity language
  - *Idioms* — "Falling off a log", "Here be monsters", etc.
  - *Animals* — complexity by creature size (Ant → Whale)
  - *Software* — developer analogies ("Config change" → "Full rewrite")
- **Special cards** — `?` (need more info), `☕` (break), `∞` (too large, must split)
- **Moderator controls** — reveal, re-vote, new story, kick, timer, deck change
- **Statistics** — average, median, range, and consensus detection after reveal
- **Timer** — optional countdown for timeboxed discussions
- **Responsive** — works on desktop and mobile

## Quick Start

### Development

Start the backend and frontend in separate terminals:

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev -- --port 5173
```

The frontend dev server proxies `/api` requests to the backend automatically.

Open http://localhost:5173 to use the app.

### Docker

```bash
docker build -t bdapoker .
docker run -p 8000:8000 bdapoker
```

Open http://localhost:8000. The single container serves both the API and the SvelteKit static build.

## Architecture

```
backend/           Python 3.11+, FastAPI, uvicorn
  app/
    main.py        FastAPI app, REST endpoints, static file serving
    models.py      Pydantic data models (Room, Participant, Round, Vote)
    decks.py       Deck definitions with descriptions per flavor
    rooms.py       In-memory room store, creation, expiry cleanup
    connection_manager.py   WebSocket connection tracking per room
    ws.py          WebSocket endpoint, message handler, state broadcast

frontend/          SvelteKit 2, Svelte 5, TypeScript
  src/
    routes/
      +page.svelte              Landing page (create room)
      room/[id]/+page.svelte    Room page (join + game view)
    lib/
      stores/
        websocket.ts    WS connection, send, message handler
        room.ts         Room state, stats, timer stores
      components/
        JoinForm.svelte          Name + role selection
        CardDeck.svelte          Votable card grid
        Card.svelte              Single card with tooltip
        ParticipantList.svelte   Participants + vote status
        VoteResults.svelte       Post-reveal statistics
        StoryField.svelte        Current story display
        ModeratorControls.svelte Reveal, reset, new story, timer
        Timer.svelte             Countdown display
      types.ts       TypeScript interfaces
```

### How It Works

1. **Create a room** — POST `/api/rooms` with deck type and description flavor. Returns a room ID and moderator token.
2. **Join** — open `/room/{id}`, enter a name, pick voter or spectator.
3. **Vote** — voters pick a card. Others see a checkmark but not the value.
4. **Reveal** — moderator reveals all votes. Statistics are computed and outliers highlighted.
5. **Discuss & re-vote** — moderator can reset for another round or start a new story.

All state is synchronized via WebSocket. The server broadcasts full room state on every change, with vote values conditionally hidden until reveal.

### WebSocket Protocol

All messages are JSON `{"type": "...", "payload": {...}}`.

**Client → Server:** `join`, `vote`, `reveal`, `new_round`, `reset_round`, `kick`, `change_deck`, `start_timer`, `stop_timer`

**Server → Client:** `welcome`, `room_state`, `timer_start`, `timer_stop`, `error`

### REST API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/rooms` | Create room |
| GET | `/api/rooms/{id}` | Get room info |
| GET | `/api/decks` | List all decks, flavors, descriptions |
| WS | `/api/rooms/{id}/ws` | WebSocket connection |

## Deployment

### Kubernetes (Helm)

```bash
helm install poker oci://ghcr.io/bluedynamics/charts/bdapoker \
  --set ingress.enabled=true \
  --set ingress.host=poker.example.com
```

Or from the repo:

```bash
helm install poker ./helm/bdapoker \
  --set ingress.enabled=true \
  --set ingress.host=poker.example.com
```

**Important:** The app uses in-memory state. All rooms and WebSocket connections live in a single process. Do not scale beyond 1 replica without adding a shared state backend (e.g. Redis). The Helm chart defaults to `replicas: 1` and `strategy: Recreate` to prevent split-brain during rollouts.

The ingress template includes nginx annotations for WebSocket support (1h proxy timeouts, connection upgrade headers).

### Docker image

The CI pipeline builds and pushes to `ghcr.io/bluedynamics/bdapoker` on every push to main.

```bash
docker pull ghcr.io/bluedynamics/bdapoker:latest
docker run -p 8000:8000 ghcr.io/bluedynamics/bdapoker:latest
```

## Testing

```bash
# Backend (pytest, 90% coverage)
cd backend
pip install pytest pytest-cov pytest-asyncio httpx
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Frontend (type checking)
cd frontend
npx svelte-check --threshold error
```

## Design Decisions

- **No database** — rooms are ephemeral (auto-expire after 4 hours of inactivity). In-memory state keeps the stack simple.
- **Full state broadcast** — the server sends the complete room state after every mutation. This eliminates sync bugs and keeps the frontend simple.
- **Single container** — the SvelteKit frontend is built as a static SPA and served by FastAPI alongside the API. One process, one port.
- **Plain UI** — no CSS framework, no animations, no decorative elements. System fonts, black/white/grey palette with minimal accent color.

## License

[MIT](LICENSE)
