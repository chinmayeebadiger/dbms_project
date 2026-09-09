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

The screens currently use mock data for the report and summary states. Backend requests are defined in `src/services/api.js` but the real analysis flow will be connected in later phases.
