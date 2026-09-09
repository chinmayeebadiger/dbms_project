# Migration Safety Frontend

Phase 1 establishes the React shell and integration contract for the Database Migration Safety Platform.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173`. The backend base URL is read from `VITE_API_BASE_URL`; if it is not set, the client defaults to `http://localhost:8000`.

## Phase 1 boundary

The Analyze, Report, History, Dashboard, and Knowledge Graph screens are connected to the analyzer and SQLAlchemy-backed history endpoints. The graph uses React Flow for draggable nodes, zoom/pan controls, a minimap, and labeled relationships. Mock fallback data keeps the shell usable when the backend is unavailable. PostgreSQL is the target database, with SQLite available for local development without PostgreSQL.
