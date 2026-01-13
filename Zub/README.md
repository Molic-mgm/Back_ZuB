# Unity Game Backend (FastAPI + PostgreSQL)

Features:
- OAuth-style login via Telegram Login Widget verification (server-side hash check)
- VK OAuth `code` exchange
- Subscription check: Telegram channel/group (getChatMember) and VK group (groups.isMember)
- User profile: provider ID (Telegram/VK), nickname (unique), currency ("Зубные щётки"), skins JSON
- Points: total/daily/weekly + configurable daily cap N points/day (admin setting)
- Leaderboard: top-10 by total points
- Admin panel prototype: SQLAdmin (users, score events, settings)
- Alembic migrations
- Docker + docker-compose for production-ish start

## Quick start (Docker)
1) Copy env:
```bash
cp .env.example .env
```

2) Start:
```bash
docker compose up -d --build
```

3) Run migrations:
```bash
docker compose exec api alembic upgrade head
```

API:
- http://localhost:8000/docs
Admin:
- http://localhost:8000/admin

## Local (without docker)
- Create a Postgres DB and set DATABASE_URL in .env
- Install deps:
```bash
pip install -r requirements.txt
```
- Migrate:
```bash
alembic upgrade head
```
- Run:
```bash
uvicorn app.main:app --reload
```

## Key endpoints
- POST `/auth/telegram` body: Telegram Login Widget payload (must include `hash`)
- POST `/auth/vk` body: `{ "code": "..." }`
- POST `/auth/nickname` body: `{ "nickname": "Name" }`
- GET `/users/me`
- POST `/points/add` body: `{ "amount": 10, "reason": "level_complete" }`
- GET `/leaderboard/top10`

## Unity integration
Use `Authorization: Bearer <token>` for authenticated requests.

> Note about Telegram subscription check: bot often must be admin in the channel to access member status.
