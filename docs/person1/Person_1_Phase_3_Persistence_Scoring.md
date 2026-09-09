# Person 1 Phase 3 Persistence and Scoring

## Plan

Replace the temporary in-memory history adapter with transactional database persistence and keep the documented score formula stable.

## Implementation

Replaced `backend/app/services/store.py` with SQLAlchemy persistence. Each analysis saves the migration, findings, warnings, statements, graph nodes, and graph edges in one transaction. Retrieval reconstructs the same frontend contract. The score calculation remains in the analyzer and is stored as a numeric value.

## Review checklist

- [x] Analysis receives a generated ID.
- [x] Child records are saved with the migration foreign key.
- [x] Graph edges resolve to stored graph nodes.
- [x] History survives request boundaries and process restart when using a file/PostgreSQL database.
- [x] Score and risk level are preserved on retrieval.

## Issues found

The existing frontend expects the graph and findings in one response, so retrieval needed reconstruction rather than returning only summary rows.

## Fixes applied

Added reconstruction logic for findings and graph data and persisted statements/warnings in JSON columns.

## Evidence

API tests save an analysis and retrieve it by ID, including findings and graph data.

## Sign-off status

Complete.
