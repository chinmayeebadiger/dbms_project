# Database Migration Safety Platform

## Detailed project phases and two person work split

**BCSE302L Database Systems | Review 2 implementation plan**

| Project detail | Value |
|---|---|
| Person 1 | Chinmayee Badiger (24BAI0251) |
| Person 2 | Shruti Agnihotri (24BCE2758) |
| Target complexity | Medium: substantial database and UI work with a bounded rule catalog |
| Primary outcome | A browser tool that checks migration SQL before deployment |
| Source used | Attached master document: `dbms_project_masterdoc_work_split.pdf` |

## Purpose

This document converts the attached academic master document into a practical execution sequence. The master document defines the project topic, objectives, technologies, risk catalog, graph model, scoring formula, screens, and broad ownership. This document adds phase gates, concrete tasks, interfaces, test evidence, and handoff rules so two people can work in parallel without losing integration clarity.

**Important scope note:** The repository was empty when reviewed, containing Git metadata but no implementation files. The phases therefore begin with project setup and are written as a build plan rather than a description of completed code.

## 1 Project target

Build a Database Migration Safety Platform that accepts pasted SQL or an uploaded `.sql` file, parses supported migration statements, identifies unsafe operations, explains their likely impact, recommends safer alternatives, calculates a 0-100 risk score, stores the analysis, and visualizes the relationship between operations, objects, risks, severity, conditions, and alternatives.

### 1.1 In scope

- React frontend with analysis, report, history, dashboard, and graph views.
- FastAPI backend with validation, analysis orchestration, scoring, history storage, and graph endpoints.
- PostgreSQL tables for migrations, findings, graph nodes, and graph edges.
- `sqlglot`-based parsing for a bounded initial SQL catalog.
- Seeded risk rules for DROP, TRUNCATE, mass DELETE/UPDATE, type changes, renames, constraints, and indexes.
- Automated tests for input validation, parsing, matching, scoring, persistence, and representative UI/API flows.

### 1.2 Out of scope

- Executing migrations or connecting to production databases.
- Machine-learning classification, authentication, multi-tenancy, cloud deployment, and automatic rollback generation.
- Full support for every SQL dialect or every possible migration framework.

## 2 Shared architecture and contract

The implementation follows the flow below. Person 1 owns the service foundation, storage, and score helper. Person 2 owns parser integration, risk matching, user-facing screens, visualization, and end-to-end integration.

| Layer | Decision | Owner |
|---|---|---|
| Frontend | React; graph with React Flow or Cytoscape.js | Person 2 |
| API | FastAPI REST endpoints and OpenAPI docs | Person 1 |
| Parser | `sqlglot` plus a small normalization layer | Person 2 with Person 1 normalization support |
| Database | PostgreSQL relational tables including knowledge graph tables | Person 1 |
| Integration | JSON contract, error shape, sample migrations | Both |

### 2.1 Minimum API contract

| Endpoint | Input | Output responsibility |
|---|---|---|
| `GET /health` | None | `{"status":"ok"}` |
| `POST /analyze` | JSON `title/sql_text` or multipart `.sql` file | Migration ID, score, level, statements, detailed findings |
| `GET /history` | Optional level/date filters | Recent saved analyses |
| `GET /history/{id}` | Path ID | One analysis with findings |
| `GET /graph/{migration_id}` | Path ID | Nodes and edges for graph view |

The analyze response must use stable field names: `operation`, `affected_object`, `risk_type`, `severity`, `explanation`, `impact`, `alternative`, and `line_number`. Both people must treat this response as the integration boundary. Changes require a short note in the repository and an update to the frontend API client plus backend tests.

## 3 Phase plan

Each phase has a primary owner, a concrete handoff, and an exit gate. Person 1 has more backend work, but it is deliberately scaffolded and beginner-friendly. Person 2 handles the higher-complexity parser, graph matching, frontend, visualization, and integration work described in the course master document.

### Phase 0 - Align scope and create the workspace

**Primary owner:** Both  
**Goal:** Make the project executable and remove ambiguity before coding.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Create the repository layout; add backend/frontend folders; create `.env.example`; record PostgreSQL database name and local ports; create a task board or checklist; write the first API contract draft. |
| Person 2 | Create the React app shell; choose React Flow or Cytoscape.js; sketch the five screens; list the UI states for empty, loading, success, parse warning, and server error. |
| Both | Confirm the twelve risk patterns, severity mapping, graph node types, and sample SQL cases. Agree that submitted SQL is analyzed only and never executed. |

**Exit gate:** Both people can clone the repository, install dependencies, identify their folders, and explain the same response JSON.

### Phase 1 - Build the foundation

**Primary owner:** Person 1  
**Goal:** Create a working backend and database foundation while Person 2 creates a usable shell.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Create `app/main.py` and a router; add `GET /health`; define `AnalyzeRequest`, `AnalyzeResponse`, `RiskFinding`, and `HistoryItem` models; add CORS for local frontend; create PostgreSQL connection settings; write `schema.sql` for `migrations`, `detected_risks`, `kg_nodes`, and `kg_edges`; write `seed.sql` for the risk catalog. |
| Person 2 | Create navigation and page placeholders for Dashboard, Analyze Migration, Risk Report, Migration History, and Knowledge Graph; add a shared API client; create a consistent result state shape and basic responsive layout. |
| Both | Run the health route and database schema locally. Review naming, timestamps, IDs, and error response format before the next phase. |

**Exit gate:** `/health` works, tables and seed rows exist, frontend starts, and pages can be navigated.

### Phase 2 - Implement the analysis engine

**Primary owner:** Person 1  
**Goal:** Establish the pipeline and scoring behavior.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Implement input limits, empty SQL validation, `.sql` file validation, whitespace cleanup, safe statement splitting, line-number retention, and the `POST /analyze` endpoint shell. Implement severity-to-number mapping and the score formula: `min(100, max risk + 0.10 * sum of other risks)`. Add placeholder analyzer wiring so the endpoint returns structured output. |
| Person 2 | Integrate `sqlglot`; parse each statement; extract operation, table, column, and conditions; map parser output to canonical signals such as `DROP_COLUMN` and `WITHOUT_WHERE`; match signals to seeded catalog rows and graph relationships; generate findings with explanations, impacts, alternatives, and line numbers. |
| Both | Use three fixtures: `safe_add_column.sql`, `unsafe_destructive.sql`, and `mixed_risk.sql`. Freeze the exact JSON shape after testing the first unsafe case. |

**Exit gate:** A mixed SQL input produces deterministic structured findings and a deterministic score.

### Phase 3 - Complete the user analysis flow

**Primary owner:** Both  
**Goal:** Make one complete browser journey work.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Connect the analyzer output to database persistence; save the migration, findings, and timestamp in one transaction; implement `GET /history` and `GET /history/{id}`; return clear 4xx errors for invalid input and safe 5xx messages for unexpected failures. |
| Person 2 | Build the SQL editor, file upload, title field, analyze button, loading state, validation message, and report page. Show overall score, risk level, findings table, explanation, impact, alternative, and line reference. Make critical findings visually distinct but readable. |
| Both | Run paste and file-upload flows. Verify that the report shown in the browser matches the persisted history record. |

**Exit gate:** A user can analyze one file from the browser, view the report, refresh, and retrieve it from history.

### Phase 4 - Add explainability and exploration

**Primary owner:** Person 2  
**Goal:** Expose the knowledge graph and make stored results useful.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Implement graph retrieval or graph projection for one migration; return node IDs, labels, types, and edge relationships; add indexes and verify foreign-key joins; provide average score and critical-count query support for dashboard metrics. |
| Person 2 | Implement `GET /graph/{migration_id}` consumption; render Operation -> Database Object/Risk -> Severity/Alternative relationships; add hover or click details; build history filters; build dashboard recent analyses, average score, and critical-risk count. |
| Both | Check that every graph relationship displayed is supported by an actual finding or seeded catalog edge. Test empty-history and no-graph states. |

**Exit gate:** Graph, report, history, and dashboard agree on the same analysis data.

### Phase 5 - Test, harden, and document

**Primary owner:** Both  
**Goal:** Turn the working prototype into a reliable academic submission.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Write backend tests for health, empty input, file type, size limits, normalization, statement splitting, score calculation, schema persistence, and history retrieval. Add database setup/reset instructions and seed verification. |
| Person 2 | Write parser tests for every catalog family; test malformed SQL and line references; test frontend loading/error/empty states; run end-to-end safe, critical, and mixed examples; capture screenshots for the report/demo. |
| Both | Review API docs, README, sample migrations, naming, and console errors. Run the acceptance checklist and record known limitations. |

**Exit gate:** All must-pass tests pass and the demo can be repeated from a clean setup.

### Phase 6 - Prepare Review 2 delivery

**Primary owner:** Both  
**Goal:** Package evidence of database design, implementation, and teamwork.

| Owner | Detailed instructions |
|---|---|
| Person 1 | Finalize schema diagram/table descriptions, API docs, backend test summary, scoring explanation, and setup notes. |
| Person 2 | Finalize UI screenshots, graph explanation, parser examples, end-to-end demo script, and frontend test summary. |
| Both | Prepare a 5-8 minute demo: paste safe SQL, analyze destructive SQL, explain one finding chain, open history, open graph, and mention limitations/future work. |

**Exit gate:** Repository, README, phase document, tests, seed data, screenshots, and demo script are present and consistent.

## 4 Person 1 detailed checklist

| Priority | Deliverable | Evidence |
|---|---|---|
| Must | FastAPI structure and `/health` | Endpoint response and OpenAPI entry |
| Must | Pydantic request/response models | Model tests and example JSON |
| Must | Analyze endpoint shell | Placeholder response before parser integration |
| Must | Validation and normalization | Tests for empty, oversized, non-SQL, whitespace, and line references |
| Must | PostgreSQL schema and seed | `schema.sql`, `seed.sql`, table/foreign-key check |
| Should | History persistence and endpoints | Saved row, findings rows, GET history response |
| Should | Scoring helper | Unit tests for single, mixed, and capped scores |
| Should | Graph endpoint | Nodes/edges response and join query |
| Must | Backend documentation | Runbook and known limitations |

## 5 Person 2 detailed checklist

| Priority | Deliverable | Evidence |
|---|---|---|
| Must | `sqlglot` parser integration | Tests for supported operations |
| Must | Signal extraction and catalog matching | Canonical operation/object/condition output |
| Must | Finding generation | Explanation, impact, alternative, severity, line reference |
| Must | React analyze screen | Paste, upload, loading, validation, success, error |
| Must | Risk report | Score, level, findings and readable details |
| Should | Dashboard and history | Recent rows, filters, average, critical count |
| Should | Knowledge graph view | Interactive nodes and edges with details |
| Must | Integration tests | Safe, critical, mixed, malformed, and upload cases |
| Must | Demo evidence | Screenshots and repeatable demo script |

## 6 Coordination rules

- Work in separate folders or branches when possible; pull and test before handing work over.
- Person 1 publishes the API contract before Person 2 connects screens.
- Person 2 publishes parser output examples before Person 1 finalizes persistence assumptions.
- Every handoff includes: changed files, how to run it, sample request, expected response, and known limitation.
- Use the same sample migrations and risk keys in tests, seed data, and screenshots.
- Do not hide parser uncertainty. Return a warning or unsupported-operation result with a line number.
- Keep the final demo on local or test data only.

## 7 Acceptance checklist

- [ ] Repository setup works from a clean checkout.
- [ ] PostgreSQL schema creates all four required tables and seed data is present.
- [ ] FastAPI `/health` and `/analyze` are visible in OpenAPI docs.
- [ ] Pasted SQL and `.sql` upload both work; empty, wrong-type, and oversized input are rejected.
- [ ] `DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, unqualified `DELETE`, and unqualified `UPDATE` are detected.
- [ ] Constraint, type-change, rename, and index cases are represented in the catalog or clearly marked as unsupported.
- [ ] Every finding includes operation, object, risk, severity, explanation, impact, alternative, and line reference.
- [ ] Scores follow the documented formula and the 0-100 cap.
- [ ] History survives page refresh and can be opened by ID.
- [ ] Graph nodes and edges correspond to the report.
- [ ] Backend, parser, frontend, and integration tests have recorded results.
- [ ] README and this document match the actual repository commands and folder names.

## 8 Future work after Review 2

Possible extensions include dialect-specific parsing, migration-framework adapters, dependency analysis for application queries and views, approval workflows, authenticated projects, richer rollback guidance, asynchronous analysis for large files, and a native graph database. These are deliberately deferred so the Review 2 implementation stays medium in complexity.

## 9 Source brief versus execution plan

**Instructions from the attached PDF:** Use the Database Migration Safety Platform topic; include SQL analysis, knowledge-graph relationships, risk scoring, history, graph visualization, and the React/FastAPI/sqlglot/PostgreSQL stack; follow the named Person 1 and Person 2 responsibilities; and support the listed risk catalog and screens.

**User-requested additions in this document:** Inspect the project as a whole, make the plan detailed, divide the work into phases, provide instructions for both people, and keep the project medium in complexity.

Implementation decisions added here are clearly framed as recommendations because the repository had no source files to inspect.
