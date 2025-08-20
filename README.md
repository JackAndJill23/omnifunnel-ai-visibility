# OmniFunnel AI Visibility Platform (MVP Scaffold)

This repository contains a runnable MVP scaffold for the OmniFunnel AI Visibility Platform described in the spec. It includes:

- Backend services (FastAPI): `tracker`, `generator`, `analytics`, `score`, `authz`, `deployer`, `telemetry`, `billing`
- Shared DB schemas and connection utilities
- PostgreSQL (with pgvector), Redis, and a minimal Next.js web app
- Docker Compose for local development

## Quick start

1) Prereqs: Docker Desktop (Windows/macOS/Linux)

2) Copy env and start

```bash
cp .env.example .env
# Adjust secrets if needed, then:
docker compose up -d --build
```

3) Open services
- API Gateway (authz + docs aggregator TBD): http://localhost:8080
- tracker: http://localhost:8001/docs
- generator: http://localhost:8002/docs
- analytics: http://localhost:8003/docs
- score: http://localhost:8004/docs
- deployer: http://localhost:8005/docs
- telemetry: http://localhost:8006/docs
- billing: http://localhost:8007/docs
- Web (Next.js): http://localhost:3000
- Postgres: localhost:5432 (DB: `omnifunnel`)
- Redis: localhost:6379

4) Run DB migrations (first startup runs automatically). SQL is under `db/migrations`.

## Structure

```
backend/
  common/
  services/
    tracker/
    generator/
    analytics/
    score/
    authz/
    deployer/
    telemetry/
    billing/
  requirements.txt
frontend/
  web/ (Next.js)
db/
  migrations/
wordpress/
  plugin/ (answer_hub skeleton)
```

## Notes
- This is a scaffold with minimal endpoints matching the spec’s API. Engines and CMS adapters are stubbed.
- pgvector is enabled via the `ankane/pgvector` image for future embedding features.
- Replace stub adapters with real integrations as you progress through milestones M1–M3.

## Scripts (Windows PowerShell)
- Start: `docker compose up -d --build`
- Stop: `docker compose down`
- Logs: `docker compose logs -f service_name`

## Licensing
Internal scaffold — add appropriate license before external distribution.

