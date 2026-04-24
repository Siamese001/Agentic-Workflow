-- =====================================================================
-- Ledger Base Schema — SSOT for all intelligence-capture ledgers
-- =====================================================================
-- This DDL is the canonical shape every ledger under artifacts/ledgers/
-- must conform to. Per-ledger schema files (.windsurf/schemas/<name>_ledger.schema.sql)
-- may extend this base with ledger-specific columns via additive ALTER
-- semantics, but must never remove or rename base columns.
--
-- Applied by: tools/ledgers/apply_schema.py (idempotent, multi-ledger)
-- Referenced by:
--   - tools/ledgers/writer.py (writer contract)
--   - tools/ledgers/consulter.py (precedent lookup)
--   - ops_scripts/ci/check_ledger_writer_contract.py (W5 gate)
--
-- Design invariants:
--   - Additive only: never DROP or RENAME a base column
--   - All PRAGMAs idempotent
--   - All timestamps ISO-8601 UTC TEXT
--   - event_id is the idempotency key — writers MUST compute deterministically
--   - JSON blobs validated at write time; consulter never trusts them
-- =====================================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ---------------------------------------------------------------------
-- events — one row per captured intelligence event
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS events (
    -- Identity
    event_id              TEXT PRIMARY KEY,                   -- deterministic hash of (kind, ts, repo_area, payload)
    event_kind            TEXT NOT NULL,                      -- ledger-specific taxonomy (e.g., "tool_routing", "mcp_invocation")
    ts_utc                TEXT NOT NULL,                      -- ISO-8601 UTC event timestamp

    -- Context
    repo_area             TEXT,                               -- file/module path most relevant to event
    session_id            TEXT,                               -- cross-hook correlation id
    branch                TEXT,
    commit_sha            TEXT,
    adg_snapshot_id       TEXT,                               -- adg_indexed_<ts>.sqlite tag

    -- Core prediction vs outcome (both JSON blobs; schema per ledger)
    prediction_json       TEXT,                               -- what the system predicted/decided
    outcome_json          TEXT,                               -- what actually happened (may be NULL until bound)

    -- Deterministic score (per-ledger scorer; base holds final band + numeric)
    score_band            TEXT,                               -- ledger-specific (e.g., "P1".."P5", "strong"|"weak", "correct"|"miss")
    score_numeric         REAL,                               -- raw score before banding

    -- Performance
    latency_ms            INTEGER,                            -- duration from prediction→outcome or prediction→writer

    -- Freeform metadata (JSON) — validated per ledger
    metadata_json         TEXT,

    -- Lifecycle
    status                TEXT NOT NULL DEFAULT 'predicted',  -- predicted | bound | calibrated | retired
    bound_at              TEXT,                               -- when outcome was attached
    calibrated_at         TEXT                                -- when consumed by calibration run
);

CREATE INDEX IF NOT EXISTS idx_events_kind       ON events(event_kind);
CREATE INDEX IF NOT EXISTS idx_events_ts         ON events(ts_utc);
CREATE INDEX IF NOT EXISTS idx_events_session    ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_status     ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_repo_area  ON events(repo_area);
CREATE INDEX IF NOT EXISTS idx_events_commit     ON events(commit_sha);
CREATE INDEX IF NOT EXISTS idx_events_score_band ON events(score_band);

-- ---------------------------------------------------------------------
-- event_scope — files/symbols touched by an event (optional detail table)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS event_scope (
    scope_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    TEXT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    file_path   TEXT,
    symbol_name TEXT,
    symbol_kind TEXT,
    layer       TEXT,
    tags        TEXT
);
CREATE INDEX IF NOT EXISTS idx_event_scope_event ON event_scope(event_id);
CREATE INDEX IF NOT EXISTS idx_event_scope_file  ON event_scope(file_path);

-- ---------------------------------------------------------------------
-- events_fts — FTS5 index for precedent lookup across prediction/outcome/metadata
-- ---------------------------------------------------------------------
CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
    event_id        UNINDEXED,
    event_kind,
    repo_area,
    prediction_json,
    outcome_json,
    metadata_json,
    content=events,
    content_rowid=rowid
);

-- ---------------------------------------------------------------------
-- schema_version — tracks applied migrations per ledger
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL,
    description TEXT
);
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (1, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'W0: ledger base schema - events, event_scope, events_fts, schema_version');
