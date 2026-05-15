-- Memory MCP knowledge_graph Schema
-- Canonical SSOT for Memory MCP SQLite schema
-- Location: .cursor/schemas/knowledge_graph.schema.sql
-- Version: 1.0.0

-- Core entities table
CREATE TABLE IF NOT EXISTS entities (
    name        TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL DEFAULT 'general',
    created_at  REAL NOT NULL,
    updated_at  REAL NOT NULL
);

-- Observations linked to entities
CREATE TABLE IF NOT EXISTS observations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name  TEXT NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
    content      TEXT NOT NULL,
    created_at   REAL NOT NULL,
    UNIQUE (entity_name, content)
);

-- Relations between entities
CREATE TABLE IF NOT EXISTS relations (
    from_entity   TEXT NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    to_entity     TEXT NOT NULL,
    created_at    REAL NOT NULL,
    PRIMARY KEY (from_entity, relation_type, to_entity)
);

-- Base indexes for performance
CREATE INDEX IF NOT EXISTS idx_obs_entity ON observations (entity_name);
CREATE INDEX IF NOT EXISTS idx_rel_from   ON relations (from_entity);
CREATE INDEX IF NOT EXISTS idx_rel_to     ON relations (to_entity);
CREATE INDEX IF NOT EXISTS idx_ent_type   ON entities (entity_type);

-- Schema version tracking (enables migration system)
CREATE TABLE IF NOT EXISTS _schema_version (
    version     TEXT PRIMARY KEY,
    applied_at  REAL NOT NULL,
    description TEXT NOT NULL
);

-- Insert current schema version
INSERT OR IGNORE INTO _schema_version (version, applied_at, description)
VALUES ('1.0.0', CAST(strftime('%s', 'now') AS REAL), 'Initial schema with entities, observations, relations');
