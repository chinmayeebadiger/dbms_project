# Migration Safety Backend

## Run locally

```bash
cd backend
python3 -m pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

The default local database is SQLite at `backend/migration_safety.db` so the project can run without a separate database service. The production target is PostgreSQL; set `DATABASE_URL` to a `postgresql+psycopg://...` URL before startup.

## Test

From the repository root:

```bash
PYTHONPATH=backend pytest -q backend/tests
```

## Database files

- `schema.sql` creates the PostgreSQL application tables, constraints, and indexes.
- `seed.sql` creates/updates the standalone PostgreSQL risk catalog table.
- `app/db.py` mirrors the schema for SQLAlchemy startup initialization and local testing.
