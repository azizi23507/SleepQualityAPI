# Sleep Quality API

REST API for storing patient sleep readings and returning sleep quality assessments.

**Live demo:** https://sleepqualityapi.onrender.com/docs

> Hosted on Render's free tier. The service sleeps after inactivity, so the first request may take up to a minute.

## Stack

FastAPI · PostgreSQL · SQLAlchemy · Alembic · Pydantic v2 · Docker · Docker Compose

## Features

• Full CRUD for patients and sleep readings  
• Filtering, pagination, and date range queries on list endpoints  
• Sleep quality prediction endpoint using rule based logic, designed for a trained model swap  
• API key authentication via request header  
• Database constraints enforced at both the schema and application level  
• Alembic migrations for all schema changes  
• Health check endpoint reporting database connectivity  

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/patients` | Create a patient |
| GET | `/patients` | List patients with pagination |
| GET | `/patients/{id}` | Get one patient |
| PATCH | `/patients/{id}` | Update a patient |
| DELETE | `/patients/{id}` | Delete a patient, blocked if readings exist |
| GET | `/patients/{id}/readings` | List a patient's readings |
| POST | `/readings` | Create a sleep reading |
| GET | `/readings` | List readings with filtering and pagination |
| GET | `/readings/{id}` | Get one reading |
| PATCH | `/readings/{id}` | Update a reading |
| DELETE | `/readings/{id}` | Delete a reading |
| GET | `/readings/{id}/prediction` | Sleep quality assessment |
| GET | `/health` | Service and database status |

All endpoints except `/health` require an `X API Key` header.

## Running locally

```bash
git clone https://github.com/azizi23507/SleepQualityAPI.git
cd SleepQualityAPI
cp .env.example .env
docker compose up --build -d
docker compose exec api alembic upgrade head