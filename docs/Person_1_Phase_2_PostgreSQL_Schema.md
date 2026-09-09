# Person 1 Phase 2 PostgreSQL Schema

## Plan

Create repeatable PostgreSQL schema and seed scripts for migrations, findings, graph nodes, graph edges, and the risk catalog.

## Implementation

Added `backend/schema.sql` with the four required tables, foreign keys, cascade rules, uniqueness constraints, and indexes. Added `backend/seed.sql` with all twelve risk catalog entries. SQLAlchemy metadata mirrors the schema for local initialization.

## Review checklist

- [x] Migration and finding tables exist.
- [x] Graph tables have migration and node foreign keys.
- [x] Risk catalog seed covers all twelve operations.
- [x] Indexes and unique constraints are declared.
- [x] Schema is safe to rerun.

## Issues found

Live PostgreSQL execution could not be performed because `psql` is unavailable in the environment.

## Fixes applied

Added a SQLite-compatible development path through SQLAlchemy while keeping PostgreSQL `JSONB`, UUID, and timestamp definitions in the standalone production SQL script.

## Evidence

SQLAlchemy initialization creates the mirrored local schema and catalog automatically; the backend test suite exercises the resulting tables.

## Sign-off status

Complete pending live PostgreSQL execution in the deployment environment.
