# Person 2 Implementation Plan

## Database Migration Safety Platform

**Owner:** Shruti Agnihotri (24BCE2758)  
**Project role:** SQL parser, risk matching, frontend, knowledge-graph visualization, and integration  
**Complexity target:** Medium  
**Working rule:** Complete one phase through plan, implementation, review, and fixes before starting the next phase.

## 1 Purpose and boundaries

This plan converts the Person 2 responsibilities from the project master document into an ordered implementation roadmap. Person 2 owns the higher-complexity analysis and product experience work:

- Integrating `sqlglot`.
- Extracting operations, tables, columns, and conditions.
- Matching parsed signals to the seeded risk catalog and graph relationships.
- Generating detailed findings.
- Building the React analysis screen.
- Building the risk report, dashboard, and history experience.
- Building the interactive knowledge-graph view.
- Connecting the frontend to the backend.
- Running integration and end-to-end tests.

Person 2 does not own PostgreSQL schema creation, backend service scaffolding, database migrations, or the final scoring helper. Those are Person 1 responsibilities. Person 2 must, however, define and test the parser output that Person 1 stores and scores.

The repository initially contains documentation only. The implementation will be added incrementally under a separate `frontend/` and `backend/` structure, while all phase notes, test evidence, screenshots, sample payloads, and review records will be stored under `docs/`.

## 2 Shared contract Person 2 must use

### 2.1 Required finding fields

Every detected finding must expose:

```json
{
  "operation": "DROP_COLUMN",
  "affected_object": "customers.email",
  "risk_type": "DATA_LOSS",
  "severity": "CRITICAL",
  "explanation": "Dropping the column permanently removes stored values.",
  "impact": "Existing data and application queries may be affected.",
  "alternative": "Deprecate the column, back it up, and remove it later.",
  "line_number": 3
}
```

Field names are part of the integration boundary. If a field must change, update the API examples and tests in `docs/` before changing the implementation.

### 2.2 Supported risk catalog

Person 2 must implement matching for these initial cases without expanding into a general-purpose SQL linter:

| Canonical operation | Detection signal | Expected severity | Main alternative |
|---|---|---|---|
| `DROP_TABLE` | `DROP TABLE` | Critical | Back up and drop later |
| `DROP_COLUMN` | `ALTER TABLE ... DROP COLUMN` | Critical | Deprecate, back up, and remove later |
| `TRUNCATE_TABLE` | `TRUNCATE TABLE` | Critical | Back up and require approval |
| `DELETE_WITHOUT_WHERE` | `DELETE` with no `WHERE` | Critical | Add a condition and preview rows |
| `UPDATE_WITHOUT_WHERE` | `UPDATE` with no `WHERE` | High | Add a condition and rollback plan |
| `ALTER_COLUMN_TYPE` | Column type change | High | Add new column, backfill, validate |
| `RENAME_COLUMN` | Column rename | High | Add new column and migrate gradually |
| `ADD_NOT_NULL` | `NOT NULL` on existing data without safe backfill/default | High | Add nullable, backfill, then constrain |
| `ADD_UNIQUE` | New unique constraint/index | Medium/High | Detect duplicates first |
| `ADD_FOREIGN_KEY` | New foreign key | Medium/High | Check orphan records first |
| `CREATE_INDEX` | New index creation | Medium | Use concurrent/non-blocking creation where supported |
| `DROP_INDEX` | Index removal | Medium | Check index usage first |

## 3 Working method for every phase

Every phase follows the same controlled loop:

1. **Plan:** Write or update the phase note in `docs/` before changing code.
2. **Implement:** Make only the work assigned to that phase.
3. **Review:** Run focused tests, inspect the output, check the phase acceptance criteria, and record findings.
4. **Fix:** Correct every issue found during review and repeat the focused checks.
5. **Sign off:** Add a short completion note to the phase document. Only then begin the next phase.

The assistant will return to the user after the plan is approved and after each phase has passed its fix-and-review loop. No later phase should be silently started while an earlier phase is awaiting review.

## 4 Phase roadmap

### Phase 1 - Frontend foundation and integration contract

**Goal:** Create a stable React application shell and a testable API client without building the full product yet.

**Person 2 work:**

- Create the frontend application structure.
- Add routing or page-level navigation for:
  - Dashboard.
  - Analyze Migration.
  - Risk Report.
  - Migration History.
  - Knowledge Graph.
- Add a shared API client with a configurable backend base URL.
- Define frontend TypeScript or JavaScript types for analyze requests, findings, analysis responses, history items, graph nodes, and graph edges.
- Add reusable loading, empty, validation-error, server-error, and success states.
- Choose React Flow or Cytoscape.js and document the choice.
- Add a basic responsive layout and accessible form labels.
- Create the first frontend mock data file so pages can be developed before the backend is complete.

**Expected files:**

```text
frontend/
├── package.json
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── services/api.js
│   ├── types.js
│   ├── components/
│   └── pages/
└── README.md
```

**Review evidence:** frontend starts locally, every page is reachable, mock findings render, API errors do not crash the application, and the API type definitions match the agreed backend JSON.

**Phase 1 gate:** Do not start parser implementation until the page structure and JSON contract are reviewed and accepted.

### Phase 2 - SQL parser integration and signal extraction

**Goal:** Convert supported SQL statements into deterministic canonical signals.

**Person 2 work:**

- Add the `sqlglot` dependency to the backend parser area or the agreed shared analyzer package.
- Parse one statement at a time while retaining the original statement and line number.
- Extract, where available:
  - Operation type.
  - Table name.
  - Column name.
  - Column type.
  - Constraint name.
  - Presence or absence of `WHERE`.
  - Presence or absence of a default value.
  - Relevant conditions such as `WITHOUT_WHERE_CLAUSE`.
- Normalize parser output into canonical operation keys from the catalog.
- Return an explicit unsupported or parse-warning result when a statement cannot be safely classified.
- Do not execute SQL during parsing.
- Add parser fixtures for safe, critical, high, medium, mixed, malformed, and unsupported statements.

**Expected output shape:**

```json
{
  "statement_index": 1,
  "line_number": 2,
  "raw_sql": "DELETE FROM users;",
  "operation": "DELETE_WITHOUT_WHERE",
  "affected_object": "users",
  "signals": ["DELETE", "WITHOUT_WHERE_CLAUSE"],
  "parse_status": "classified"
}
```

**Review evidence:** each supported catalog case has a fixture and expected output; malformed SQL returns a useful warning; line numbers are stable; parser output is deterministic across repeated runs.

**Phase 2 gate:** Do not begin graph matching until the parser outputs have been reviewed and accepted.

### Phase 3 - Risk matching and finding generation

**Goal:** Turn canonical parser signals into explanatory findings connected to the risk catalog.

**Person 2 work:**

- Load risk catalog data through the agreed backend service or endpoint.
- Match canonical operations and conditions to risk definitions.
- Resolve affected database objects into readable labels.
- Generate one or more findings per statement when multiple risks are present.
- Populate severity, explanation, impact, safer alternative, and line reference.
- Preserve a stable relationship key for graph generation, for example:
  - `DROP_COLUMN -> AFFECTS -> COLUMN`.
  - `DROP_COLUMN -> MAY_CAUSE -> DATA_LOSS`.
  - `DATA_LOSS -> HAS_SEVERITY -> CRITICAL`.
  - `DATA_LOSS -> HAS_ALTERNATIVE -> DEPRECATE_BEFORE_DROP`.
- Handle duplicate findings so one SQL statement does not produce accidental repeated warnings.
- Handle unsupported operations as warnings rather than silently reporting Low risk.

**Review evidence:** sample SQL produces findings that agree with the source catalog; every finding has all required fields; critical cases are never downgraded because of missing optional metadata; duplicate findings are controlled.

**Phase 3 gate:** Do not build the final report UI until the finding JSON is accepted against at least safe, critical, and mixed examples.

### Phase 4 - Analyze Migration screen

**Goal:** Give users a complete and understandable way to submit SQL.

**Person 2 work:**

- Build a title input.
- Build a multi-line SQL editor or textarea.
- Add `.sql` file upload.
- Add file type and client-side size checks.
- Add an Analyze button with disabled/loading states.
- Connect the screen to `POST /analyze`.
- Display backend validation and parser warnings without losing the submitted SQL.
- Add a small example migration selector for demo convenience if it does not complicate the product.
- Navigate to the Risk Report only after a successful response.
- Preserve the latest result in frontend state and make refresh behavior explicit.

**Review evidence:** paste flow works, file flow works, empty input is blocked, loading is visible, server errors are readable, and successful analysis navigates to a complete report.

**Phase 4 gate:** Do not start dashboard polish until the full analyze-to-report flow works with real backend responses.

### Phase 5 - Risk Report and history experience

**Goal:** Present results clearly and make previous analyses retrievable.

**Person 2 work:**

- Build the risk summary with overall score and risk level.
- Display findings in a readable table or stacked list.
- Show operation, affected object, severity, explanation, impact, alternative, and line number.
- Add filters or grouping by severity when useful.
- Make critical findings visually prominent without relying on color alone.
- Link line numbers back to the relevant statement or show the statement excerpt.
- Build Migration History using `GET /history`.
- Add history filters for risk level and date if supported by the API.
- Build a detail route or panel using `GET /history/{id}`.
- Add empty-history and failed-history states.

**Review evidence:** report values match API response; history displays saved analyses; opening a history item reproduces the report; the UI remains readable for many findings.

**Phase 5 gate:** Do not build graph interactions until report and history data are stable.

### Phase 6 - Dashboard and knowledge-graph visualization

**Goal:** Add the project’s explainability and exploration layer.

**Person 2 work:**

- Build dashboard cards for recent analyses, average score, and critical-risk count.
- Add a recent-analysis list with links to reports.
- Consume `GET /graph/{migration_id}`.
- Render nodes for operation, database object, risk, severity, condition, and safer alternative.
- Render labeled edges for `AFFECTS`, `MAY_CAUSE`, `HAS_SEVERITY`, `HAS_CONDITION`, `INCREASES`, and `HAS_ALTERNATIVE`.
- Add node hover or click details.
- Add a clear empty state when a migration has no graph data.
- Keep graph rendering bounded to the selected migration so the page remains responsive.
- Ensure graph labels and report findings use the same IDs and text.

**Review evidence:** dashboard metrics match backend data; graph nodes and edges correspond to report findings; graph is readable for a mixed migration; empty and error states work.

**Phase 6 gate:** Do not move to final testing until report, history, dashboard, and graph agree on the same migration ID and findings.

### Phase 7 - Integration testing and final frontend hardening

**Goal:** Verify the complete system and prepare Person 2’s delivery evidence.

**Person 2 work:**

- Test safe `ADD COLUMN`.
- Test `DROP COLUMN` and `DROP TABLE` critical findings.
- Test unqualified `DELETE` and `UPDATE`.
- Test mixed migrations with multiple findings.
- Test malformed SQL and unsupported statements.
- Test `.sql` upload and invalid file type.
- Test history after page refresh.
- Test graph for one critical migration and one mixed migration.
- Test loading, empty, validation, parser-warning, server-error, and success states.
- Check browser console for errors and network calls for incorrect payloads.
- Capture screenshots for the final demo.
- Write a 5-8 minute demo script.
- Record known limitations and unsupported syntax.

**Review evidence:** integration test results, screenshots, demo script, and a list of fixed issues.

**Phase 7 gate:** Person 2 work is complete only when the full browser demo runs from a clean setup and no must-pass issue remains open.

## 5 Required documentation under `docs/`

Person 2 must keep these artifacts in the `docs/` folder as the work progresses:

| File | When to create/update | Purpose |
|---|---|---|
| `Person_2_Implementation_Plan.md` | Created before Phase 1 | This roadmap and ownership boundary |
| `Person_2_Phase_1_Frontend_Foundation.md` | Phase 1 | Plan, files changed, tests, review notes, fixes, sign-off |
| `Person_2_Phase_2_Parser.md` | Phase 2 | Parser rules, fixtures, expected output, review record |
| `Person_2_Phase_3_Risk_Matching.md` | Phase 3 | Matching rules, finding examples, review record |
| `Person_2_Phase_4_Analyze_Screen.md` | Phase 4 | UI states, API integration, screenshots, review record |
| `Person_2_Phase_5_Report_History.md` | Phase 5 | Report and history behavior, test evidence, review record |
| `Person_2_Phase_6_Dashboard_Graph.md` | Phase 6 | Dashboard metrics, graph mapping, review record |
| `Person_2_Phase_7_Integration.md` | Phase 7 | End-to-end tests, demo script, limitations, final review |
| `Person_2_API_Examples.md` | After Phase 1 and whenever the contract changes | Stable sample requests and responses |
| `Person_2_Review_Log.md` | Throughout | Cross-phase issue and fix history |

Each phase note must use this structure:

```markdown
# Phase N - Name

## Plan

## Implementation

## Review checklist

## Issues found

## Fixes applied

## Evidence

## Sign-off status
```

## 6 Definition of done for Person 2

Person 2’s work is complete when:

- The supported SQL catalog is parsed and classified deterministically.
- Findings are detailed, stable, and compatible with Person 1’s API and scoring work.
- The React frontend supports paste, upload, analysis, report, history, dashboard, and graph views.
- The frontend handles loading, empty, invalid, unsupported, and server-error states.
- The browser flow works against the real backend, not only mock data.
- Graph relationships accurately explain the report.
- Integration tests cover safe, unsafe, mixed, malformed, and uploaded inputs.
- Documentation and evidence for every phase are stored in `docs/`.
- Every phase has completed the plan → implement → review → fix cycle and has a recorded sign-off.

## 7 First user review point

This plan is the first deliverable. No Person 2 implementation phase should begin until this plan is reviewed and approved. After approval, implementation starts with Phase 1: Frontend foundation and integration contract.
