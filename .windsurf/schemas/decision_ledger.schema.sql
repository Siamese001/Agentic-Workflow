-- =====================================================================
-- Decision Ledger — Canonical DDL (SSOT)
-- =====================================================================
-- Location: .windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite
-- Applied by: .windsurf/scripts/apply_ledger_schema.py (idempotent)
-- Referenced by:
--   - .windsurf/scripts/post_cascade_hitl_capture.py (writer)
--   - .windsurf/scripts/post_commit_outcome_binder.py (outcome writer)
--   - .windsurf/skills/refactor-decision-memory/lookup_refactor_decisions.py (reader)
--   - ops_scripts/ci/author_gate/check_ledger_schema.py (validator)
--   - ops_scripts/ci/author_gate/check_outcome_coverage.py (validator)
--
-- Design invariants:
--   - Additive only: never DROP or RENAME a column used by prior releases
--   - All PRAGMAs idempotent
--   - Hash chain columns (prev_hash, row_hash) are optional in v1 (NULL ok)
--   - ALL timestamps are ISO-8601 UTC strings (sqlite stores TEXT)
-- =====================================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ---------------------------------------------------------------------
-- decisions — one row per HITL/author-gate decision surfaced
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decisions (
    -- Identity
    decision_id           TEXT PRIMARY KEY,
    created_at            TEXT NOT NULL,                      -- ISO-8601 UTC
    branch                TEXT,
    commit_sha            TEXT,

    -- Classification
    decision_type         TEXT NOT NULL,                      -- architecture_choice | refactor_scope | anti_pattern |
                                                              -- dependency_addition | test_strategy | deletion_strategy |
                                                              -- error_handling | unknown
    request_summary       TEXT,
    normalized_intent     TEXT,
    user_goal             TEXT,                               -- W2: "what the user was trying to accomplish"
    principle_at_stake    TEXT,                               -- W2: didactic field (e.g., "layer gravity", "fail-closed")

    -- Recommendation vs selection
    recommended_option_id TEXT,
    selected_option_id    TEXT,
    selection_rationale   TEXT,
    options_json          TEXT,                               -- JSON blob of ALL candidates (surfaced + suppressed)

    -- Scoring telemetry (W2 additions)
    confidence_top        REAL,                               -- winning candidate score
    confidence_dominance_gap REAL,                            -- gap to next-best
    override_vs_recommendation INTEGER DEFAULT 0,             -- 1 iff user picked non-top option
    selection_latency_ms  INTEGER,                            -- surface → selection wall time

    -- Context binding (W2)
    policy_snapshot       TEXT,                               -- e.g., "hitl-enforcement.md@<sha>"
    context_fingerprint_json TEXT,                            -- adg_snapshot, git_sha, files_in_scope, blast_radius

    -- Integrity (W5 placeholder — NULL ok in v1)
    prev_hash             TEXT,
    row_hash              TEXT,
    sig_alg               TEXT,
    signature             TEXT,

    -- Lifecycle
    status                TEXT NOT NULL DEFAULT 'surfaced'    -- surfaced | executed | rolled_back | failed
);

CREATE INDEX IF NOT EXISTS idx_decisions_type      ON decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_decisions_status    ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_created   ON decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_decisions_commit    ON decisions(commit_sha);

-- ---------------------------------------------------------------------
-- decision_scope — files/symbols touched by a decision
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decision_scope (
    scope_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
    file_path   TEXT,
    symbol_name TEXT,
    symbol_kind TEXT,
    layer       TEXT,
    repo_area   TEXT,
    tags        TEXT
);
CREATE INDEX IF NOT EXISTS idx_scope_decision ON decision_scope(decision_id);
CREATE INDEX IF NOT EXISTS idx_scope_file     ON decision_scope(file_path);

-- ---------------------------------------------------------------------
-- decision_outcomes — executed decisions' downstream signals
-- Written by: post_commit_outcome_binder.py
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id           TEXT NOT NULL REFERENCES decisions(decision_id),

    -- Core binary signals
    execution_completed   INTEGER DEFAULT 0,
    tests_passed          INTEGER DEFAULT 0,
    regression_found      INTEGER DEFAULT 0,
    rollback_required     INTEGER DEFAULT 0,
    promote_to_pattern    INTEGER DEFAULT 0,

    -- Evidence (W2 additions)
    commit_shas_json      TEXT,                               -- ["<sha>", ...]
    files_written_json    TEXT,                               -- ["path/a.py", ...]
    tests_run_json        TEXT,                               -- ["tests/x/test_y.py::test_z", ...]
    latency_to_outcome_s  INTEGER,                            -- decision surfaced → outcome bound
    pattern_promotion_eligible INTEGER DEFAULT 0,             -- promote candidacy flag
    outcome_label         TEXT,                               -- success | rework | rollback | undecided

    -- Freeform + timing
    bound_at              TEXT,                               -- ISO-8601 UTC when this row was written
    outcome_notes         TEXT
);
CREATE INDEX IF NOT EXISTS idx_outcomes_decision ON decision_outcomes(decision_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_label    ON decision_outcomes(outcome_label);

-- ---------------------------------------------------------------------
-- decisions_fts — FTS5 index for precedent lookup
-- ---------------------------------------------------------------------
CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id       UNINDEXED,
    normalized_intent,
    request_summary,
    user_goal,
    selection_rationale,
    content=decisions,
    content_rowid=rowid
);

-- ---------------------------------------------------------------------
-- schema_version — tracks applied migrations
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL,
    description TEXT
);
INSERT OR IGNORE INTO schema_version(version, applied_at, description)
VALUES (2, strftime('%Y-%m-%dT%H:%M:%SZ','now'),
        'W2: outcome binding, scoring telemetry, didactic fields, hash chain placeholders');
