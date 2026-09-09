# Person 1 Implementation Plan

## Database Migration Safety Platform

**Owner:** Chinmayee Badiger (24BAI0251)  
**Project role:** FastAPI foundation, PostgreSQL database, API models, persistence, seed data, scoring, and backend tests  
**Complexity target:** Medium  
**Dependency:** Preserve the existing frontend/API field names while replacing temporary in-memory storage with PostgreSQL.

## 1 Purpose and responsibilities

This plan converts the Person 1 responsibilities from the master document into a buildable roadmap. Person 1 owns the stable backend and database boundary used by Person 2:

- FastAPI project structure and health route.
- Pydantic request and response models.
- Input validation, normalization, and safe statement splitting.
- PostgreSQL schema, foreign keys, indexes, and seed data.
- Migration and finding persistence.
- History, statistics, and graph retrieval endpoints.
- The documented risk-scoring helper.
- Backend tests and local setup instructions.

Person 2 already provides the parser and analyzer contract. Person 1 should integrate it rather than duplicate parser logic. The current repository uses a temporary in-memory store in `backend/app/services/store.py`; replacing that adapter with PostgreSQL is the central remaining task.

## 2 Existing contract to preserve

The following endpoints and response fields are already consumed by the frontend:

| Endpoint | Responsibility |
|---|---|
| `GET /health` | Return `{"status":"ok"}` |
| `POST /analyze` | Analyze JSON `title` and `sql_text`, save the result, and return the full analysis |
| `POST /analyze-file` | Validate and analyze a UTF-8 `.sql` upload |
| `GET /history` | Return saved summary items with optional `risk_level` filtering |
| `GET /history/{id}` | Return one saved analysis with findings and graph |
| `GET /stats` | Return analysis count, average score, and critical count |
| `GET /graph/{id}` | Return graph nodes and edges for one saved migration |

Each finding must retain `operation`, `affected_object`, `risk_type`, `severity`, `explanation`, `impact`, `alternative`, and `line_number`. Do not rename these fields without updating `docs/Person_2_API_Examples.md` and the frontend API client.

## 3 Phased work plan

### Phase 1 - Backend foundation and environment

- Confirm Python version and create `backend/.venv` if required.
- Add or verify `requirements.txt`.
- Organize `app/main.py`, routers, models, services, and tests.
- Keep `/health` and OpenAPI docs working.
- Add `.env.example` with `DATABASE_URL`, host, port, and allowed frontend origins.
- Document backend startup and test commands.

**Gate:** Clean setup starts FastAPI and `/health` returns 200.

### Phase 2 - PostgreSQL schema and seed catalog

- Create a database named `migration_safety`.
- Add `migrations` with ID, title, SQL text, score, risk level, warnings, and timestamp.
- Add `detected_risks` with migration foreign key and all finding fields.
- Add `kg_nodes` and `kg_edges` with graph foreign keys and relationship labels.
- Add indexes on creation time, risk level, migration ID, and node type.
- Add foreign-key delete behavior appropriate for migration-owned findings/graph records.
- Seed all twelve risk catalog operations and their explanations, severities, and alternatives.
- Make schema creation and seeding repeatable.

**Gate:** Schema and seed scripts run on a clean PostgreSQL database and produce the expected tables, keys, indexes, and catalog rows.

### Phase 3 - Persistence adapter and scoring

- Implement a PostgreSQL connection/session module.
- Replace the in-memory store behind a stable service interface.
- Save one migration, its findings, warnings, and graph data in a transaction.
- Roll back the transaction if any child insert fails.
- Implement the score formula exactly:

  ```text
  score = min(100, max(individual risk) + 0.10 * sum(other risks))
  ```

- Keep numeric severity mapping documented and tested.
- Return `Low`, `Medium`, `High`, or `Critical` using the agreed score ranges.

**Gate:** An analysis survives backend restart and the score is identical before and after retrieval.

### Phase 4 - API completion and query behavior

- Connect JSON and file analysis routes to the PostgreSQL service.
- Keep input limits and file validation in place.
- Implement history sorting newest first.
- Implement risk-level filtering.
- Implement detail retrieval with 404 handling.
- Implement dashboard statistics through SQL aggregation.
- Implement graph retrieval through migration-scoped joins.
- Keep error responses clear and safe; do not expose database credentials or stack traces.

**Gate:** The existing frontend works without code changes against the PostgreSQL-backed API.

### Phase 5 - Testing and hardening

- Test health and OpenAPI availability.
- Test empty, oversized, malformed, unsupported, and wrong-file-type input.
- Test all twelve seeded catalog entries.
- Test score calculations for one risk, multiple risks, and 100-point cap.
- Test transaction rollback behavior.
- Test persistence across application restart.
- Test history filters, detail 404, stats, and graph endpoints.
- Add database setup/reset fixtures that do not affect production data.
- Run the full test suite from a clean environment.

**Gate:** All must-pass backend tests pass and the test database can be recreated.

### Phase 6 - Handoff and Review 2 delivery

- Update `README.md` with PostgreSQL setup and environment steps.
- Add schema/table descriptions and a simple ER diagram under `docs/`.
- Update `docs/Person_2_API_Examples.md` if any response details changed.
- Record the final test commands and results.
- Explain the score formula and risk catalog.
- Provide Person 2 with the final database/API handoff note.

**Gate:** A clean checkout can start PostgreSQL, seed the catalog, run FastAPI, and complete the browser demo.

## 4 Required files under `docs/`

- `Person_1_Phase_1_Backend_Foundation.md`
- `Person_1_Phase_2_PostgreSQL_Schema.md`
- `Person_1_Phase_3_Persistence_Scoring.md`
- `Person_1_Phase_4_API_Completion.md`
- `Person_1_Phase_5_Backend_Testing.md`
- `Person_1_Phase_6_Handoff.md`
- `Person_1_API_Handoff.md`
- `Person_1_Review_Log.md`

Each phase note should record the plan, implementation, review checklist, issues found, fixes applied, evidence, and sign-off status.

## 5 Person 1 definition of done

Person 1 is complete when PostgreSQL is the source of truth, all API endpoints work against it, the risk catalog is seeded, scoring is reproducible, history survives restart, graph data is migration-scoped, tests pass, and the README gives a clean setup path.
