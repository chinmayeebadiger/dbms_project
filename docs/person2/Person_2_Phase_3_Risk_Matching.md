# Phase 3 - Risk Matching and Finding Generation

## Plan

Connect canonical parser signals to a local, explicit risk catalog and generate detailed findings with stable operation keys, affected objects, severity, explanation, impact, safer alternatives, line references, and graph relationship data.

## Implementation

Implemented `backend/app/services/risk_catalog.py` and `backend/app/services/analyzer.py`. The analyzer now:

- Contains explicit catalog entries for all twelve initial operations.
- Generates stable findings with operation, object, risk type, severity, explanation, impact, alternative, and line number.
- Deduplicates repeated findings by operation, affected object, and line.
- Calculates the documented score using numeric severity values and caps at 100.
- Returns explicit parser warnings for unsupported or malformed statements.
- Builds graph nodes and labeled edges for affected objects, risks, severity, and safer alternatives.

The minimal FastAPI surface in `backend/app/main.py` exposes the analyzer through JSON `POST /analyze` and multipart `POST /analyze-file` so the frontend can use real results.

## Review checklist

- All twelve initial risk catalog cases are represented.
- Safe statements do not receive destructive-risk findings.
- Multiple findings are supported for mixed migrations.
- Duplicate findings are removed deterministically.
- Unsupported statements become warnings rather than silent Low risk.
- Generated findings are compatible with the frontend contract.

## Issues found

The first graph pass created generic object IDs and risk IDs that did not always match the normalized node IDs. The score test also exposed the need to remove the largest finding before summing the remaining risks.

## Fixes applied

Graph edges now point to the actual affected-object node and normalized risk node. Score calculation removes one maximum severity value before applying the 10 percent contribution rule.

## Evidence

The analyzer test suite passes 5 tests. A mixed migration returned `DROP_COLUMN` and `UPDATE_WITHOUT_WHERE`, score `96.5`, level `Critical`, and a graph containing 10 nodes and 8 edges.

## Sign-off status

Complete. Risk matching and finding generation are ready for frontend consumption.
