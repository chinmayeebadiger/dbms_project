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

The Analyze screen is connected to the Phase 2-4 analyzer endpoints. The dashboard, history, and graph pages still use Phase 1 mock data until the persistence and final graph endpoints are completed.
