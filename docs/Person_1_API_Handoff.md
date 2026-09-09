# Person 1 API Handoff

## Start the backend locally

```bash
cd backend
python3 -m pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Without PostgreSQL installed, the backend defaults to a local SQLite file named `migration_safety.db`. For PostgreSQL, set:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/migration_safety
```

## Database scripts

- `schema.sql` creates the PostgreSQL tables and indexes.
- `seed.sql` creates/updates the standalone `risk_catalog` table.
- SQLAlchemy initialization creates the same application tables and seeds the catalog when the API starts.

## API contract

The endpoints are documented in the existing `docs/Person_2_API_Examples.md`. The frontend expects the response fields to remain stable, especially finding fields and graph node/edge IDs.

## Scoring

```text
score = min(100, max(individual risk) + 0.10 * sum(other risks))
```

Numeric severity values are Low 15, Medium 40, Medium High 58, High 65, and Critical 90. Score levels are Low 0-25, Medium 26-50, High 51-75, and Critical 76-100.

## Replacement note

The old in-memory adapter has been replaced by SQLAlchemy persistence. The frontend does not need to change when `DATABASE_URL` points at PostgreSQL.
