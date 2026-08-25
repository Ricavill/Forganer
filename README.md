# Friends Activity Planner

An AI-assisted meetup organizer: add friends, record what activities you and
they like or dislike, and let a chat assistant (backed by an LLM with tool
access to your data) plan and schedule meetups for you — or do it all by hand
through the web app.

## Features

- **AI assistant chat** — plan a meetup in plain language ("set up a board
  games night with Maria and Tomás this weekend"). The assistant can look up
  your friends' opinions on activities, create schedules/groups/meetups, send
  friend requests, and email calendar invites, by calling tools over MCP
  against the same API the web app uses.
- **Activities & opinions** — a shared catalog of activities with
  typo-tolerant search and duplicate-name blocking (trigram similarity), and
  a 5-point sentiment (strongly dislike → strongly like) per user per
  activity.
- **Friends** — search for people by name or email, send/accept/reject/cancel
  friend requests, and see who's already interested in a given activity.
- **Groups & meetups** — named groups of people, schedules (start/end time,
  rejects overlaps and past dates), and meetups tying a schedule to a group.
- **Calendar-invite emails** — optional `.ics` calendar invites sent via
  [Resend](https://resend.com) when a meetup is created; the assistant only
  offers this when it's configured.
- **Web frontend** — a React app (`frontend/`) with the same 5 sections as
  the assistant: chat, calendar, meetup creation, friends, and your profile
  (opinions/activities).
- **Terminal client** (`terminal_client/`) — a minimal signup/login + chat
  REPL against the API, useful for quick testing without the browser.
- **MCP server** (`mcp_server/`) — exposes the API as MCP tools so the
  assistant (or any MCP-compatible client) can act on a user's behalf,
  authenticated with that user's own bearer token per request.

## Architecture

```
frontend/        React + Vite + TypeScript web app
app/              FastAPI backend (feature-based: app/features/<domain>/)
mcp_server/       Standalone MCP server, proxies to the API over HTTP
terminal_client/  Minimal CLI client
migrations/       Alembic migrations
tests/            Pytest suite (runs against a real Postgres, SAVEPOINT-isolated)
```

The backend is FastAPI + SQLAlchemy (sync) + Postgres (with the `pgvector`
and `pg_trgm` extensions), JWT auth, and a domain-exception pattern (services
raise `NotFoundError`/`ConflictError`/etc., translated to HTTP by a global
exception handler — routers never raise `HTTPException` directly).

## Prerequisites

- Docker and Docker Compose
- An OpenAI API key (for the assistant chat)
- Node.js 20+ and npm (only if you want to run the frontend)

## Setup

1. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set at least `SECRET_KEY` (any long random string)
   and `OPENAI_API_KEY`. `RESEND_API_KEY`/`RESEND_FROM_EMAIL` are optional —
   leave them blank to disable calendar-invite emails.

2. **Start the backend stack** (API + MCP server + Postgres)

   ```bash
   docker-compose up -d --build
   ```

3. **Run database migrations**

   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **Verify the API is up**

   ```bash
   curl http://localhost:8000/health/
   # {"status":"ok"}
   ```

   The API is now available at `http://localhost:8000` (interactive docs at
   `http://localhost:8000/docs`), and the MCP server at
   `http://localhost:8765/mcp`.

### Running the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It talks to the API at
`http://localhost:8000` by default (see `frontend/.env`,
`VITE_API_BASE_URL`).

### Using the terminal client

```bash
cd terminal_client
pip install -r requirements.txt
python client.py
```

Follow the prompts to sign up or log in, then chat with the assistant
directly from the terminal.

## Running tests and lint

Backend tests run against a real Postgres database (not mocks), so point
`DATABASE_URL` at one before running them — the easiest way is against the
same database the Docker stack uses:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
ruff check .
ruff format --check .
```

CI (`.github/workflows/ci.yml`) runs lint, the test suite against a fresh
Postgres service container, and a basic MCP server import check on every
push and pull request.

## Design prototype

`design/` contains a clickable design prototype of the mobile app UI
(Warm Editorial style) built with Claude Design's Design Components format,
plus a plain standalone HTML version (`design/prototype.html`) you can open
directly in any browser — no build step required.
