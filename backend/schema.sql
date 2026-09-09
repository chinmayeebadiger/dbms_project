CREATE TABLE IF NOT EXISTS migrations (
    id UUID PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    sql_text TEXT NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    statements JSONB NOT NULL DEFAULT '[]'::jsonb,
    warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detected_risks (
    id BIGSERIAL PRIMARY KEY,
    migration_id UUID NOT NULL REFERENCES migrations(id) ON DELETE CASCADE,
    operation VARCHAR(80) NOT NULL,
    affected_object VARCHAR(255),
    risk_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    explanation TEXT NOT NULL,
    impact TEXT NOT NULL,
    alternative TEXT NOT NULL,
    line_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS kg_nodes (
    id BIGSERIAL PRIMARY KEY,
    migration_id UUID NOT NULL REFERENCES migrations(id) ON DELETE CASCADE,
    node_type VARCHAR(80) NOT NULL,
    node_key VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    UNIQUE(migration_id, node_key)
);

CREATE TABLE IF NOT EXISTS kg_edges (
    id BIGSERIAL PRIMARY KEY,
    migration_id UUID NOT NULL REFERENCES migrations(id) ON DELETE CASCADE,
    source_node_id BIGINT NOT NULL REFERENCES kg_nodes(id) ON DELETE CASCADE,
    relationship VARCHAR(80) NOT NULL,
    target_node_id BIGINT NOT NULL REFERENCES kg_nodes(id) ON DELETE CASCADE,
    UNIQUE(migration_id, source_node_id, relationship, target_node_id)
);

CREATE INDEX IF NOT EXISTS idx_migrations_created_at ON migrations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_migrations_risk_level ON migrations(risk_level);
CREATE INDEX IF NOT EXISTS idx_detected_risks_migration_id ON detected_risks(migration_id);
CREATE INDEX IF NOT EXISTS idx_kg_nodes_migration_type ON kg_nodes(migration_id, node_type);
CREATE INDEX IF NOT EXISTS idx_kg_edges_migration_id ON kg_edges(migration_id);
