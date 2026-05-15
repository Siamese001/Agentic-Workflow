-- Memory MCP knowledge_graph Schema Migrations
-- Tracks additive migrations applied to the base schema
-- Location: .cursor/schemas/knowledge_graph_migrations.sql

-- Migration: 1.1.0 - Add decay tracking columns (confidence, last_reinforced, access_count)
-- Applied: Idempotent via sqlite_memory_store.py _migrate_decay_columns()

-- Entities table additions
ALTER TABLE entities ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0;
ALTER TABLE entities ADD COLUMN last_reinforced REAL;
ALTER TABLE entities ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0;

-- Observations table additions
ALTER TABLE observations ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0;
ALTER TABLE observations ADD COLUMN last_reinforced REAL;
ALTER TABLE observations ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0;

-- Index for confidence-filtered reads
CREATE INDEX IF NOT EXISTS idx_ent_confidence ON entities (confidence, last_reinforced);

-- Record migration
INSERT OR IGNORE INTO _schema_version (version, applied_at, description)
VALUES (
    '1.1.0',
    CAST(strftime('%s', 'now') AS REAL),
    'Add decay tracking: confidence, last_reinforced, access_count on entities and observations'
);
