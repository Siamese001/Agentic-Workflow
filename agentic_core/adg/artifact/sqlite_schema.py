"""Single authoritative SQLite DDL contract for canonical ADG artifacts."""

from __future__ import annotations

from hashlib import sha256

SQLITE_SCHEMA_VERSION = "4.0.0"

DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id            INTEGER PRIMARY KEY,
    adg_name      TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    identity_kind TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    resolved_path TEXT NOT NULL,
    precision_type        TEXT DEFAULT 'symbol',
    span_start            INTEGER DEFAULT 0,
    span_end              INTEGER DEFAULT 0,
    span_line             INTEGER DEFAULT 0,
    span_column           INTEGER DEFAULT 0,
    span_end_line         INTEGER DEFAULT 0,
    span_end_column       INTEGER DEFAULT 0,
    logical_sequence_id   INTEGER DEFAULT 0,
    control_path_id       TEXT DEFAULT '',
    temporal_order        INTEGER DEFAULT 0,
    type_surface          TEXT DEFAULT '',
    enclosing_symbol      TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_nodes_type  ON nodes(entity_type);
CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer);
CREATE INDEX IF NOT EXISTS idx_nodes_name  ON nodes(adg_name);
CREATE INDEX IF NOT EXISTS idx_nodes_precision_type ON nodes(precision_type)
    WHERE precision_type != 'symbol';
CREATE INDEX IF NOT EXISTS idx_nodes_sequence ON nodes(logical_sequence_id)
    WHERE logical_sequence_id != 0;

CREATE TABLE IF NOT EXISTS edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id        INTEGER NOT NULL REFERENCES nodes(id),
    dst_id        INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL,
    edge_kind     TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    line_no       INTEGER NOT NULL,
    symbol        TEXT NOT NULL DEFAULT '',
    semantic_type      TEXT DEFAULT '',
    confidence_score   REAL DEFAULT 1.0,
    source_span_start  INTEGER DEFAULT 0,
    source_span_end    INTEGER DEFAULT 0,
    source_span_line   INTEGER DEFAULT 0,
    source_span_column INTEGER DEFAULT 0,
    target_span_start  INTEGER DEFAULT 0,
    target_span_end    INTEGER DEFAULT 0,
    target_span_line   INTEGER DEFAULT 0,
    target_span_column INTEGER DEFAULT 0,
    dynamic_resolution TEXT DEFAULT '',

    -- 2026-04-28 Graph Authority axis (legacy single-axis enum).
    -- SSOT: agentic_core/adg/artifact/edge_authority.py
    -- Closed enum: verified | unresolved | dynamic | external | test_only | runtime_observed
    -- Kept for back-compat; superseded by the (bucket, resolution_status,
    -- authority_status) triplet below.
    authority          TEXT DEFAULT NULL,

    -- 2026-04-29 Three-bucket authority model (the canonical model).
    -- SSOT: agentic_core/adg/artifact/edge_authority.py
    -- Closed enums:
    --   bucket            ∈ {static, runtime, registry}
    --   resolution_status ∈ {VERIFIED_MODULE, VERIFIED_SYMBOL, UNRESOLVED_MODULE,
    --                        UNRESOLVED_SYMBOL, UNRESOLVED_DYNAMIC, PARTIAL,
    --                        NOT_CHECKED, NOT_APPLICABLE, UNKNOWN,
    --                        VERIFIED_RUNTIME, VERIFIED_TRACE, VERIFIED_RECEIPT,
    --                        PARTIAL_TRACE, MISSING_TRACE, VERIFIED_REGISTRY,
    --                        VERIFIED_CONFIG, UNRESOLVED_REGISTRY, STALE_REGISTRY,
    --                        MISMATCHED_REGISTRY, SUBSTITUTED_REGISTRY}
    --   authority_status  ∈ {AUTHORITATIVE, AUTHORITATIVE_RUNTIME,
    --                        AUTHORITATIVE_REGISTRY, PARTIAL,
    --                        NON_AUTHORITATIVE_HINT, RISK_SIGNAL_ONLY,
    --                        EXCLUDED_TEST_ONLY, EXCLUDED_TYPE_ONLY,
    --                        EXTERNAL_ONLY, UNKNOWN_NOT_PROOF}
    --   evidence_refs     JSON array of evidence pointers
    --                     (source_file:line for static, run_id+trace_id for
    --                      runtime, registry_digest for registry).
    -- Nullable in W1 (Phase 1). Graduates to NOT NULL in W5 once
    -- ADG_CERTIFIED gate passes.
    bucket             TEXT DEFAULT NULL,
    resolution_status  TEXT DEFAULT NULL,
    authority_status   TEXT DEFAULT NULL,
    evidence_refs      TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_edges_src  ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst  ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_authority ON edges(authority)
    WHERE authority IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_edges_bucket ON edges(bucket)
    WHERE bucket IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_edges_authority_status ON edges(authority_status)
    WHERE authority_status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_edges_resolution_status ON edges(resolution_status)
    WHERE resolution_status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_edges_rel  ON edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_edges_semantic_type ON edges(semantic_type)
    WHERE semantic_type != '';

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS violations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id       INTEGER NOT NULL REFERENCES edges(id),
    category      TEXT NOT NULL,
    evidence      TEXT NOT NULL DEFAULT '',
    file_path     TEXT NOT NULL DEFAULT '',
    line_no       INTEGER NOT NULL DEFAULT 0,
    disposition   TEXT NOT NULL DEFAULT 'untriaged',
    disposition_source TEXT DEFAULT '',
    disposition_date TEXT DEFAULT '',
    severity      TEXT NOT NULL DEFAULT 'MEDIUM',
    violation_class TEXT NOT NULL DEFAULT 'hygiene'
);
CREATE INDEX IF NOT EXISTS idx_violations_cat  ON violations(category);
CREATE INDEX IF NOT EXISTS idx_violations_file ON violations(file_path);
CREATE INDEX IF NOT EXISTS idx_violations_disp ON violations(disposition);
CREATE INDEX IF NOT EXISTS idx_violations_class ON violations(violation_class);

CREATE VIEW IF NOT EXISTS edge_view AS
    SELECT
        e.id            AS edge_id,
        src.adg_name    AS from_name,
        e.relation_type AS relation_type,
        dst.adg_name    AS to_name,
        e.edge_kind     AS edge_kind,
        src.entity_type AS from_type,
        dst.entity_type AS to_type,
        src.layer       AS from_layer,
        dst.layer       AS to_layer,
        e.source_file   AS source_file,
        e.line_no       AS line_no,
        e.symbol        AS symbol,
        e.semantic_type AS semantic_type,
        e.confidence_score AS edge_confidence,
        src.precision_type AS from_precision_type,
        dst.precision_type AS to_precision_type,
        src.logical_sequence_id AS from_sequence_id,
        dst.logical_sequence_id AS to_sequence_id,
        e.authority     AS authority   -- 2026-04-28 Graph Authority axis
    FROM edges e
    JOIN nodes src ON src.id = e.src_id
    JOIN nodes dst ON dst.id = e.dst_id;

CREATE VIEW IF NOT EXISTS precision_metrics_view AS
SELECT
    COUNT(*) AS total_edges,
    SUM(CASE WHEN e.semantic_type != '' THEN 1 ELSE 0 END) AS semantic_edges,
    COUNT(DISTINCT n.id) AS total_nodes,
    SUM(CASE WHEN n.precision_type != 'symbol' THEN 1 ELSE 0 END) AS precision_nodes,
    SUM(CASE WHEN n.precision_type = 'code_block' THEN 1 ELSE 0 END) AS code_blocks,
    SUM(CASE WHEN n.precision_type = 'expression_unit' THEN 1 ELSE 0 END) AS expression_units,
    SUM(CASE WHEN n.precision_type = 'control_branch' THEN 1 ELSE 0 END) AS control_branches
FROM edges e
JOIN nodes n ON n.id = e.src_id;
"""

DDL_SHA256 = sha256(DDL.encode("utf-8")).hexdigest()

__all__ = ["DDL", "DDL_SHA256", "SQLITE_SCHEMA_VERSION"]
