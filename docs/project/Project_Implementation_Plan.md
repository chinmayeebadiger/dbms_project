# Database Migration Safety Platform Project Plan

## Unified implementation plan

This is one integrated project. The work is organized by product phase and dependency, not by team member. Each phase combines backend, database, analyzer, frontend, testing, and documentation tasks where they belong together.

## Project objective

Build a medium-complexity web application that checks SQL migration scripts before deployment. The application accepts pasted SQL or a `.sql` file, identifies unsafe operations, explains the impact, recommends safer alternatives, calculates a risk score, stores the analysis, and visualizes the operation-risk relationship as a knowledge graph.

## Technology stack

- Frontend: React, Vite, React Flow.
- Backend: FastAPI, Pydantic, SQLAlchemy.
- Parser: `sqlglot`.
- Database: PostgreSQL for the target environment, SQLite fallback for local development without PostgreSQL.
- Testing: Pytest and frontend production builds.

## Phase workflow

Every phase follows the same loop:

1. Plan the phase and define its acceptance criteria.
2. Implement the phase in the application.
3. Review tests, API behavior, layout, and documentation.
4. Fix every issue found during review.
5. Record evidence and mark the phase complete.

## Phase 1 - Foundation

- Create the repository structure.
- Configure frontend and backend environments.
- Add the React application shell and navigation.
- Add FastAPI startup, health check, CORS, and OpenAPI docs.
- Define the shared API response contract.
- Add local environment examples and setup documentation.

## Phase 2 - SQL analysis

- Normalize and split SQL while preserving line numbers.
- Integrate `sqlglot`.
- Extract operations, tables, columns, constraints, and conditions.
- Classify the twelve supported migration-risk patterns.
- Return warnings for malformed or unsupported statements.
- Add parser fixtures and deterministic tests.

## Phase 3 - Risk engine and knowledge graph

- Define and seed the risk catalog.
- Match parser signals to risk rules.
- Generate detailed findings with severity, impact, explanation, alternative, and line reference.
- Implement the scoring formula and score-level mapping.
- Generate graph nodes and labeled relationships.
- Add analyzer and graph tests.

## Phase 4 - Analyze and report flow

- Build the SQL editor and `.sql` upload flow.
- Add title, validation, loading, warning, and error states.
- Connect the frontend to the analysis API.
- Display score, level, findings, explanations, impacts, alternatives, and line numbers.
- Store the latest result for report navigation.

## Phase 5 - Persistence and history

- Create the PostgreSQL schema, constraints, indexes, and seed scripts.
- Use SQLAlchemy persistence for migrations, findings, statements, warnings, graph nodes, and edges.
- Implement history listing, risk filtering, detail retrieval, and dashboard statistics.
- Ensure analysis data survives backend restarts when PostgreSQL or the SQLite fallback is used.
- Add persistence and API tests.

## Phase 6 - Dashboard and graph exploration

- Connect dashboard cards and recent analyses to live API data.
- Build history search and risk-level filtering.
- Connect graph retrieval to the selected migration.
- Render an interactive React Flow graph with draggable nodes, zoom/pan controls, minimap, relationship labels, and animated risk edges.
- Add empty and unavailable-data fallbacks.

## Phase 7 - Verification and delivery

- Run backend tests and Python compilation.
- Run the frontend production build.
- Test safe, critical, mixed, malformed, unsupported, and file-upload migrations.
- Verify report, history, dashboard, and graph consistency.
- Complete setup documentation, schema diagrams, API examples, and demo instructions.
- Perform live PostgreSQL and browser visual QA in the final environment.

## Definition of done

The project is complete when a clean checkout can start the application, analyze SQL, produce a detailed risk report, save and retrieve history, show dashboard metrics, render the interactive graph, pass the automated tests, and follow the documented PostgreSQL setup path.

## Current status

Phases 1 through 6 are implemented. Phase 7 automated verification is complete. Live PostgreSQL verification and browser visual QA remain environment-level final checks because those services are not available in the current workspace.

## Reference archive

Earlier owner-specific planning notes are retained in `docs/project/reference/` for traceability. They are not the active project organization; this unified plan is the source of truth going forward.
