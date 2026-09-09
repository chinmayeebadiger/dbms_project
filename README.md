# Database Migration Safety Platform

## Project overview

The Database Migration Safety Platform is a medium-complexity database systems project that checks SQL migration scripts before they are executed against an existing database. It accepts pasted SQL or an uploaded `.sql` file, identifies potentially unsafe operations, explains the likely impact, assigns a severity and an overall score, and recommends safer alternatives.

The project is based on the attached course master document for **BCSE302L - Database Systems Review 1 and Review 2**. That document is the source of the academic scope, proposed technology stack, risk catalog, knowledge-graph model, and the named two-person work split. This README turns those requirements into an implementation-ready plan. It does not claim that code already exists: the repository currently contains only Git metadata, so the first phase creates the application foundation.

Team:

- Person 1: Chinmayee Badiger (24BAI0251)
- Person 2: Shruti Agnihotri (24BCE2758)

## What the system should do

1. Receive migration SQL from a text editor or `.sql` upload.
2. Normalize the input and separate it into statements while preserving line references.
3. Parse statements with `sqlglot` and extract the operation, affected table, affected column, and safety conditions.
4. Match extracted signals with a PostgreSQL-backed migration-risk catalog and knowledge graph.
5. Produce findings containing the operation, affected object, risk type, severity, explanation, impact, safer alternative, and SQL line number.
6. Calculate an overall score from 0 to 100 and map it to Low, Medium, High, or Critical.
7. Store the submitted migration, score, level, findings, and timestamp for later review.
8. Display a report, searchable history, dashboard metrics, and an interactive operation-risk-alternative graph.

The application is an analysis and reporting tool. It must never execute a submitted migration against a production database.

## Scope and complexity control

### Included in the medium-scope release

- PostgreSQL persistence.
- FastAPI REST API with automatic OpenAPI documentation.
- React single-page frontend.
- `sqlglot` parsing for the supported SQL catalog.
- Rule and graph-assisted risk matching.
- Twelve initial risk patterns.
- Analysis history.
- Dashboard summary metrics.
- React Flow or Cytoscape.js graph visualization.
- Automated backend tests and a small end-to-end test set.

### Intentionally excluded

- Executing migrations or connecting to a user's production database.
- Full SQL support for every vendor and dialect.
- A machine-learning risk classifier.
- Authentication, multi-tenant permissions, and cloud deployment.
- Automatic rollback generation.
- Distributed graph infrastructure such as Neo4j. PostgreSQL tables are sufficient for this project.

These exclusions keep the project demonstrable and academically meaningful within a two-person team.

## Risk catalog

| SQL pattern | Main risk | Severity | Safer alternative |
|---|---|---|---|
| `DROP TABLE` | Permanent data loss and application breakage | Critical | Back up, disable usage, then drop later |
| `DROP COLUMN` | Data loss and application breakage | Critical | Deprecate, back up, and remove later |
| `TRUNCATE TABLE` | Full-table data loss | Critical | Back up and require explicit approval |
| `DELETE` without `WHERE` | Full-table deletion | Critical | Add a condition and preview affected rows |
| `UPDATE` without `WHERE` | Unintended mass update | High | Add a condition and define a rollback plan |
| `ALTER COLUMN TYPE` | Conversion errors, corruption, or locking | High | Add a new column, backfill, and validate |
| `RENAME COLUMN` | Application compatibility issue | High | Add a new column and migrate gradually |
| `ADD NOT NULL` without a default/backfill | Deployment failure on existing rows | High | Add nullable, backfill, then apply `NOT NULL` |
| `ADD UNIQUE` | Failure due to duplicate data | Medium/High | Detect and resolve duplicates first |
| `ADD FOREIGN KEY` | Orphan-row validation failure or locking | Medium/High | Check orphan records first |
| `CREATE INDEX` | Locking or slow deployment | Medium | Use concurrent/non-blocking creation where supported |
| `DROP INDEX` | Performance degradation | Medium | Check index usage before removal |

The first release may represent the catalog as seed rows and a small matching service. It does not need a general-purpose SQL linter.

## Architecture

```text
React frontend
  -> FastAPI API
      -> Input validation and normalization
      -> SQL parser and signal extraction
      -> Knowledge-graph/risk matching
      -> Risk scoring and report generation
      -> PostgreSQL persistence
```

The master document specifies React, FastAPI, `sqlglot`, PostgreSQL, and React Flow/Cytoscape.js. Use those technologies unless the team records a reason to substitute one.

## Recommended repository layout

```text
dbms_project/
├── README.md
├── docs/
│   ├── architecture/
│   ├── person1/
│   └── person2/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes.py
│   │   ├── models/schemas.py
│   │   ├── services/normalizer.py
│   │   ├── services/analyzer.py
│   │   ├── services/scoring.py
│   │   └── db/
│   │       ├── connection.py
│   │       ├── schema.sql
│   │       └── seed.sql
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/api.js
│   │   └── App.jsx
│   └── package.json
├── sample_migrations/
│   ├── safe_add_column.sql
│   ├── unsafe_destructive.sql
│   └── mixed_risk.sql
└── .env.example
```

## Data model

The minimum database model is:

- `migrations`: `id`, `title`, `sql_text`, `risk_score`, `risk_level`, `created_at`.
- `detected_risks`: `id`, `migration_id`, `operation`, `affected_object`, `risk_type`, `severity`, `explanation`, `impact`, `alternative`, `line_number`.
- `kg_nodes`: `id`, `node_type`, `node_key`, `label`.
- `kg_edges`: `id`, `source_node_id`, `relationship`, `target_node_id`.

Use foreign keys from `detected_risks.migration_id` to `migrations.id`, and from both graph edge endpoints to `kg_nodes.id`. Add indexes on migration date, risk level, and graph node type. Store timestamps in UTC. Prefer stable keys such as `DROP_COLUMN`, `DATA_LOSS`, and `BACKUP_BEFORE_CHANGE` so seed data and matching logic remain deterministic.

The graph contains these node types: Operation, Database Object, Risk, Severity, Condition, and Safer Alternative. The important relationships are `AFFECTS`, `MAY_CAUSE`, `HAS_SEVERITY`, `HAS_CONDITION`, `INCREASES`, `HAS_ALTERNATIVE`, and `RELATED_TO`.

## API contract

The team should agree on this contract before frontend integration.

### `GET /health`

Returns:

```json
{"status":"ok"}
```

### `POST /analyze`

Accept either JSON or multipart upload. The JSON form is:

```json
{
  "title": "Customer table migration",
  "sql_text": "ALTER TABLE customers ADD COLUMN phone TEXT;"
}
```

The response should contain `migration_id`, `overall_score`, `risk_level`, `findings`, and `statements`. Each finding should include `operation`, `affected_object`, `risk_type`, `severity`, `explanation`, `impact`, `alternative`, and `line_number`.

### `GET /history`

Returns recent analyses. Support optional `risk_level` and date filters if time permits.

### `GET /history/{id}`

Returns one stored analysis with its findings.

### `GET /graph/{migration_id}`

Returns graph nodes and edges needed by the visualization. Keep the shape compatible with the chosen graph library.

## Analysis pipeline

```text
Normalize SQL
  -> Split statements with line metadata
  -> Parse with sqlglot
  -> Extract operation/object/condition signals
  -> Match risk catalog and graph relationships
  -> Score findings
  -> Generate report
  -> Save history
```

Normalization must be predictable and should not silently alter SQL semantics. Preserve the original SQL for storage and reporting. If a statement cannot be parsed, return a user-facing parser warning with its line number; do not crash the entire analysis.

## Scoring model

Use the proposal's formula:

```text
overall_score = min(100, max_individual_risk + 0.10 * sum(other_risks))
```

Use numeric severity values consistently, for example: Medium = 40, High = 65, Critical = 90, and Low = 15. The highest finding establishes the base risk; remaining findings contribute 10 percent. Map the final score as follows:

- 0-25: Low
- 26-50: Medium
- 51-75: High
- 76-100: Critical

Document the exact numeric mapping in code and tests so scores are reproducible.

## Phased implementation and ownership

The detailed, person-by-person execution plan is in [DBMS Project Phases](docs/architecture/DBMS_Project_Phases.docx). The owner-specific plans are [Person 1](docs/person1/Person_1_Implementation_Plan.md) and [Person 2](docs/person2/Person_2_Implementation_Plan.md). At a high level:

| Phase | Person 1 | Person 2 | Shared checkpoint |
|---|---|---|---|
| 0. Agreement | Confirm scope, repo, environment | Confirm UI and parser assumptions | Freeze API and catalog |
| 1. Foundation | FastAPI, models, DB schema, seed data | React shell, API client, UX wireframe | Both run the skeleton |
| 2. Core analysis | Normalization, endpoint shell, scoring | `sqlglot` parser, signal extraction, matching | Sample JSON is stable |
| 3. Product flow | Persistence, history APIs, error handling | Analyze screen and risk report | One complete analysis flow |
| 4. Explainability | Graph storage and graph endpoint | Graph UI, dashboard, history UI | Findings and graph agree |
| 5. Verification | Backend tests and fixtures | Frontend/integration tests and demo | Acceptance checklist passes |
| 6. Delivery | README, setup, schema explanation | Screenshots, demo script, final polish | Review 2 package is ready |

## Setup target

The implementation should eventually support:

```bash
createdb migration_safety
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

cd ../frontend
npm install
npm run dev
```

Create `.env` from `.env.example` and keep credentials out of Git. The backend should expose its interactive API documentation at `/docs` during development.

## Test scenarios

At minimum, verify:

1. Empty input is rejected with a clear validation message.
2. A safe `ADD COLUMN` is accepted and produces Low or no risk.
3. `DROP COLUMN` produces a Critical data-loss finding and a deprecation alternative.
4. `DELETE FROM users;` produces a Critical full-table deletion finding.
5. `UPDATE users SET active = false;` produces a High mass-update finding.
6. A mixed migration produces multiple findings and a score capped at 100.
7. An invalid statement reports a parse problem with its line reference.
8. The saved history item can be retrieved after analysis.
9. The graph endpoint returns nodes and edges matching the displayed findings.
10. File upload rejects non-`.sql` files and oversized input.

## Definition of done

The project is ready for demonstration when a user can upload or paste a migration, receive a detailed report in the browser, see the result saved in history, and open a graph showing at least Operation -> Risk -> Severity and Risk -> Safer Alternative relationships. The repository must include reproducible setup instructions, seeded catalog data, sample migrations, tests, and a short demo script.

## Distinguishing the source brief from this README

The attached master document supplies the academic requirements: topic, objectives, literature context, technology choices, initial catalog, graph model, scoring formula, screens, and named responsibilities. This README adds implementation decisions needed to execute those requirements in an empty repository: the suggested folder layout, API shapes, numeric severity examples, test cases, scope exclusions, setup target, and definition of done. If the course instructor changes a requirement, update this README and the phase document together.
