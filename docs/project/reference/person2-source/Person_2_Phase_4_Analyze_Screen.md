# Phase 4 - Analyze Migration Screen

## Plan

Replace the Phase 1 preview-only submission behavior with the real analyzer API flow. Support pasted SQL, `.sql` uploads, title submission, loading, validation, backend errors, parser warnings, and navigation to the real report response.

## Implementation

Replaced the Phase 1 preview-only submission behavior with the real analyzer flow:

- `POST /analyze` is used for pasted SQL.
- `POST /analyze-file` is used for `.sql` uploads.
- The title and returned analysis are preserved in session storage.
- Successful analysis navigates to the report page.
- The report reads the real response and falls back to Phase 1 mock data when opened directly.
- Parser warnings and empty findings are displayed explicitly.
- Empty text and empty-file submissions are blocked before sending.
- Loading disables duplicate submissions and backend errors are displayed as validation messages.

## Review checklist

- Paste flow submits to the backend and renders the returned result.
- File upload submits multipart data and preserves the title.
- Empty input is blocked before a request.
- Loading state disables duplicate submissions.
- Validation and parser warnings remain understandable.
- Backend errors are shown without crashing the app.
- The report page receives the actual analysis response.

## Issues found

The first review found that the frontend API client used `/analyze` for file uploads even though the backend file endpoint is `/analyze-file`. The report page also still referenced mock data after a live response was stored.

## Fixes applied

Updated the file API path and changed the report page to read the latest stored analysis, including warnings, statement count, score, risk level, and findings.

## Evidence

`npm run build` passes with 34 modules transformed. `GET /health`, `GET /docs`, JSON `POST /analyze`, and multipart `POST /analyze-file` all return HTTP 200. The multipart test correctly detected a `DROP_TABLE` Critical finding.

## Sign-off status

Complete. The Analyze screen is connected to the real Phase 2/3 analyzer API.
