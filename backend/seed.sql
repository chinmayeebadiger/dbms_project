-- The analyzer catalog is defined in app/services/risk_catalog.py.
-- This seed file provides a portable PostgreSQL catalog table for inspection,
-- reporting, and future database-driven matching.
CREATE TABLE IF NOT EXISTS risk_catalog (
    operation VARCHAR(80) PRIMARY KEY,
    risk_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    explanation TEXT NOT NULL,
    impact TEXT NOT NULL,
    alternative TEXT NOT NULL
);

INSERT INTO risk_catalog(operation, risk_type, severity, explanation, impact, alternative) VALUES
('DROP_TABLE', 'DATA_LOSS', 'CRITICAL', 'Dropping a table permanently removes its stored data.', 'All rows and dependent application queries may be lost.', 'Back up the table, disable usage, and drop it in a later migration.'),
('DROP_COLUMN', 'DATA_LOSS', 'CRITICAL', 'Dropping the column permanently removes stored values.', 'Existing data and application queries may be affected.', 'Deprecate the column, back it up, and remove it later.'),
('TRUNCATE_TABLE', 'DATA_LOSS', 'CRITICAL', 'TRUNCATE removes every row from the target table.', 'The complete table contents may be lost immediately.', 'Back up the table and require explicit approval before truncating.'),
('DELETE_WITHOUT_WHERE', 'FULL_TABLE_DELETION', 'CRITICAL', 'DELETE without a WHERE clause affects every row in the table.', 'All records could be deleted unintentionally.', 'Add a WHERE clause and preview the affected rows first.'),
('UPDATE_WITHOUT_WHERE', 'MASS_UPDATE', 'HIGH', 'UPDATE without a WHERE clause changes every row in the table.', 'All records could be modified unintentionally.', 'Add a condition, preview affected rows, and define a rollback plan.'),
('ALTER_COLUMN_TYPE', 'TYPE_CHANGE', 'HIGH', 'Changing a column type can fail conversion or hold locks during deployment.', 'Existing values may not convert and application writes may be blocked.', 'Add a new column, backfill in batches, validate, and switch gradually.'),
('RENAME_COLUMN', 'COMPATIBILITY_BREAK', 'HIGH', 'Renaming a column can break application queries that still use the old name.', 'Old application versions may fail after deployment.', 'Add a new column and migrate callers gradually.'),
('ADD_NOT_NULL', 'DEPLOYMENT_FAILURE', 'HIGH', 'Applying NOT NULL to existing data without a default or backfill can fail.', 'The migration may be rejected when existing rows contain null values.', 'Add the column as nullable, backfill values, then apply NOT NULL.'),
('ADD_UNIQUE', 'CONSTRAINT_FAILURE', 'MEDIUM_HIGH', 'A unique constraint can fail when duplicate values already exist.', 'Deployment may fail and the constraint will not be created.', 'Detect and resolve duplicates before adding the constraint.'),
('ADD_FOREIGN_KEY', 'REFERENTIAL_FAILURE', 'MEDIUM_HIGH', 'A foreign key can fail when existing rows reference missing parent records.', 'Orphan records or locking can block deployment.', 'Check orphan records first and validate the relationship before applying it.'),
('CREATE_INDEX', 'DEPLOYMENT_LOCK', 'MEDIUM', 'Creating an index can hold locks or slow deployment on a large table.', 'Reads and writes may be delayed while the index is built.', 'Use concurrent or another non-blocking index option where supported.'),
('DROP_INDEX', 'PERFORMANCE_DEGRADATION', 'MEDIUM', 'Dropping an index can remove an access path used by important queries.', 'Query performance may degrade after deployment.', 'Check index usage before removing it.')
ON CONFLICT (operation) DO UPDATE SET risk_type=EXCLUDED.risk_type, severity=EXCLUDED.severity, explanation=EXCLUDED.explanation, impact=EXCLUDED.impact, alternative=EXCLUDED.alternative;
