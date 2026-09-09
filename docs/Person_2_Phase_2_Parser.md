# Phase 2 - SQL Parser Integration and Signal Extraction

## Plan

Implement a bounded `sqlglot`-based parser that converts supported migration statements into deterministic canonical signals while preserving raw SQL and line numbers. The parser must never execute SQL and must return an explicit warning for malformed or unsupported statements.

## Implementation

Implemented the parser in `backend/app/services/parser.py` using `sqlglot` with PostgreSQL parsing. It now:

- Splits semicolon-delimited migration statements while preserving the first content line.
- Classifies the twelve bounded catalog operations.
- Extracts table and column objects where available.
- Emits canonical signals such as `WITHOUT_WHERE_CLAUSE`, `NOT_NULL`, `FOREIGN_KEY`, and `UNIQUE`.
- Preserves raw SQL, statement index, line number, parse status, and warning text.
- Returns warnings for malformed or syntactically valid but unsupported statements.
- Never executes submitted SQL.

Added parser fixtures in `backend/tests/test_analyzer.py` for catalog operations, qualified updates, malformed SQL, and deterministic line numbers.

## Review checklist

- Supported catalog statements classify correctly.
- Raw SQL and line numbers are preserved.
- Missing `WHERE` and missing safe defaults are represented as conditions.
- Malformed and unsupported statements return warnings instead of crashing.
- Repeated runs produce the same output.

## Issues found

The first review found three issues: line numbers after semicolons were off by one, incomplete `DROP COLUMN` syntax was classified instead of warned, and the score test expected a capped score when the documented formula produced 96.5.

## Fixes applied

Line calculation now uses the first non-whitespace character of each statement. Incomplete column drops become warnings. The score expectation was corrected to the documented two-risk result of 96.5; the score remains capped at 100 for larger combinations.

## Evidence

`PYTHONPATH=backend pytest -q backend/tests` passes 5 tests. The catalog fixture classifies all twelve supported operations and preserves lines 1 through 12.

## Sign-off status

Complete. Parser work is ready for risk matching.
