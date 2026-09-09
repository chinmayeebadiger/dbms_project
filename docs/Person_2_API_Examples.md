# Person 2 API Examples

These examples document the Phase 2-4 integration contract.

## Health

```http
GET /health
```

```json
{"status":"ok"}
```

## Analyze pasted SQL

```http
POST /analyze
Content-Type: application/json
```

```json
{
  "title": "Customer cleanup",
  "sql_text": "ALTER TABLE customers DROP COLUMN email;\nUPDATE customers SET active = false;"
}
```

Important response fields:

```json
{
  "migration_id": null,
  "title": "Customer cleanup",
  "overall_score": 96.5,
  "risk_level": "Critical",
  "findings": [
    {
      "operation": "DROP_COLUMN",
      "affected_object": "customers.email",
      "risk_type": "DATA_LOSS",
      "severity": "CRITICAL",
      "explanation": "Dropping the column permanently removes stored values.",
      "impact": "Existing data and application queries may be affected.",
      "alternative": "Deprecate the column, back it up, and remove it later.",
      "line_number": 1
    }
  ],
  "warnings": [],
  "graph": {"nodes": [], "edges": []}
}
```

## Analyze a file

```http
POST /analyze-file
Content-Type: multipart/form-data
```

Fields:

- `title`: optional migration title.
- `file`: UTF-8 file with a `.sql` extension and size at most 1 MB.

## Frontend configuration

Set the backend URL in `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```
