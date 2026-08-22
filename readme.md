# Sleep Quality API

REST API for storing patient sleep readings and returning sleep quality assessments.

**Live demo:** https://sleepqualityapi.onrender.com/docs

> Hosted on Render's free tier — the service sleeps after inactivity, so the first
> request may take up to a minute.

## Stack

FastAPI · PostgreSQL · SQLAlchemy · Alembic · Pydantic v2 · Docker · Docker Compose

## Features

- Full CRUD for patients and sleep readings
- Filtering, pagination, and date-range queries on list endpoints
- Sleep quality prediction endpoint (rule-based, designed for a trained model swap)
- API key authentication via request header
- Database constraints enforced at both the schema and application layer
- Alembic migrations for all schema changes
- Health check endpoint reporting database connectivity

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/patients` | Create a patient |
| GET | `/patients` | List patients (paginated) |
| GET | `/patients/{id}` | Get one patient |
| PATCH | `/patients/{id}` | Update a patient |
| DELETE | `/patients/{id}` | Delete a patient (blocked if readings exist) |
| GET | `/patients/{id}/readings` | List a patient's readings |
| POST | `/readings` | Create a sleep reading |
| GET | `/readings` | List readings (filtered, paginated) |
| GET | `/readings/{id}` | Get one reading |
| PATCH | `/readings/{id}` | Update a reading |
| DELETE | `/readings/{id}` | Delete a reading |
| GET | `/readings/{id}/prediction` | Sleep quality assessment |
| GET | `/health` | Service and database status |

All endpoints except `/health` require an `X-API-Key` header.

## Running locally

```bash
git clone https://github.com/azizi23507/SleepQualityAPI.git
cd SleepQualityAPI
cp .env.example .env      # then fill in your values
docker compose up --build -d
docker compose exec api alembic upgrade head
```

API at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

## Design decisions

**`ON DELETE RESTRICT` over `CASCADE`** — deleting a patient with existing readings
returns `409` rather than silently destroying their sleep history. For health data,
losing records as a side effect of another action is the wrong default.

**Validation at two layers** — Pydantic rejects invalid input with a `422` before it
reaches the database; Postgres `CHECK` constraints enforce the same rules regardless
of how a row is inserted. The application layer gives good error messages; the
database layer guarantees data integrity.

**Synchronous endpoints** — `psycopg2` is a blocking driver, so FastAPI runs these in
a threadpool. Using `async def` with a blocking driver would stall the event loop.

**Prediction behind a function boundary** — the scoring logic lives in `prediction.py`
with a stable signature, so a trained model can replace the rule-based placeholder
without touching the endpoint.