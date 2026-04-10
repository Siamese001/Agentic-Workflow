# pylint: disable=protected-access
"""
test_lookup_refactor_decisions.py

Unit tests for .windsurf/skills/refactor-decision-memory/lookup_refactor_decisions.py

Coverage:
    _sanitize_fts_query — strips specials, collapses whitespace, truncates
    lookup              — failure path (no DB), edge case (empty intent)
    _run_query          — happy path via seeded in-memory DB (suggestive/strong)
    main()              — stdin round-trip exits 0
"""

import json
import sqlite3
import sys
from io import StringIO
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[4] / ".windsurf" / "skills" / "refactor-decision-memory"),
)

import lookup_refactor_decisions as _m  # noqa: E402
from lookup_refactor_decisions import (  # noqa: E402
    _run_query,
    _sanitize_fts_query,
    lookup,
    main,
)

# ---------------------------------------------------------------------------
# Minimal DDL to seed a test DB (mirrors post_cascade_hitl_capture._DDL)
# ---------------------------------------------------------------------------

_SEED_DDL = """\
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS decisions (
    decision_id           TEXT PRIMARY KEY,
    created_at            TEXT NOT NULL,
    branch                TEXT,
    commit_sha            TEXT,
    task_id               TEXT,
    decision_type         TEXT NOT NULL DEFAULT 'unknown',
    request_summary       TEXT,
    normalized_intent     TEXT,
    user_goal             TEXT,
    constraints_json      TEXT,
    risk_profile_json     TEXT,
    blast_radius_estimate TEXT,
    options_json          TEXT,
    recommended_option_id TEXT,
    selected_option_id    TEXT,
    selection_rationale   TEXT,
    status                TEXT NOT NULL DEFAULT 'surfaced'
);

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

CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id           TEXT NOT NULL REFERENCES decisions(decision_id),
    execution_completed   INTEGER DEFAULT 0,
    tests_passed          INTEGER DEFAULT 0,
    regression_found      INTEGER DEFAULT 0,
    rollback_required     INTEGER DEFAULT 0,
    followup_decision_id  TEXT,
    promote_to_pattern    INTEGER DEFAULT 0,
    outcome_notes         TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id       UNINDEXED,
    normalized_intent,
    request_summary,
    user_goal,
    selection_rationale,
    content=decisions,
    content_rowid=rowid
);
"""


def _seeded_db_path(tmp_path: Path, promoted: bool = False) -> Path:
    """Create a seeded ledger at tmp_path/ledger.sqlite. Returns path."""
    db = tmp_path / "refactor_decision_ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SEED_DDL)
    conn.execute(
        """
        INSERT INTO decisions
            (decision_id, created_at, decision_type, request_summary,
             normalized_intent, recommended_option_id, status)
        VALUES
            ('dec_aabbccdd0001', '2026-04-10T10:00:00+00:00',
             'refactor_scope',
             'Refactor L2 execution adapters into dedicated module',
             'extract execution adapter into single-responsibility module',
             'Minimal scope refactor', 'resolved')
        """
    )
    conn.execute(
        """
        INSERT INTO decision_scope (decision_id, repo_area, layer)
        VALUES ('dec_aabbccdd0001', 'agentic_core/L2_execution', 'L2')
        """
    )
    conn.execute(
        """
        INSERT INTO decision_outcomes
            (decision_id, tests_passed, regression_found, rollback_required, promote_to_pattern)
        VALUES ('dec_aabbccdd0001', 1, 0, 0, ?)
        """,
        (1 if promoted else 0,),
    )
    conn.execute(
        """
        INSERT INTO decisions_fts
            (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
        VALUES ('dec_aabbccdd0001',
                'extract execution adapter into single-responsibility module',
                'Refactor L2 execution adapters into dedicated module', '', '')
        """
    )
    conn.commit()
    conn.close()
    return db


# ---------------------------------------------------------------------------
# _sanitize_fts_query
# ---------------------------------------------------------------------------


class TestSanitizeFtsQuery:
    def test_strips_special_chars(self):
        result = _sanitize_fts_query('refactor "scope" (exact*)')
        assert '"' not in result
        assert "(" not in result
        assert "*" not in result
        assert "refactor" in result
        assert "scope" in result

    def test_keeps_alphanumeric_hyphen_underscore(self):
        result = _sanitize_fts_query("refactor_scope L2-execution")
        assert "refactor_scope" in result
        assert "L2-execution" in result

    def test_empty_string_returns_empty(self):
        assert _sanitize_fts_query("") == ""

    def test_truncates_at_200(self):
        long_text = "a " * 200
        result = _sanitize_fts_query(long_text)
        assert len(result) <= 200


# ---------------------------------------------------------------------------
# lookup — failure path and edge cases (no seeded DB needed)
# ---------------------------------------------------------------------------


class TestLookupNoDb:
    def test_missing_db_returns_none_verdict(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "nonexistent.sqlite")
        result = lookup({"decision_type": "refactor_scope", "normalized_intent": "extract adapter"})
        assert result["verdict"] == "none"
        assert result["matches"] == []
        assert "reason" in result

    def test_empty_normalized_intent_returns_none_verdict(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "nonexistent.sqlite")
        result = lookup({"decision_type": "refactor_scope", "normalized_intent": ""})
        assert result["verdict"] == "none"
        assert "reason" in result

    def test_missing_normalized_intent_key_returns_none_verdict(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "nonexistent.sqlite")
        result = lookup({"decision_type": "refactor_scope"})
        assert result["verdict"] == "none"


# ---------------------------------------------------------------------------
# _run_query — happy path via seeded DB
# ---------------------------------------------------------------------------


class TestRunQueryWithDb:
    def test_suggestive_match_returned(self, tmp_path, monkeypatch):
        db = _seeded_db_path(tmp_path, promoted=False)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract execution adapter",
                "repo_area": "agentic_core/L2_execution",
            }
        )
        assert result["verdict"] in ("suggestive", "strong")
        assert len(result["matches"]) >= 1
        assert result["matches"][0]["decision_id"] == "dec_aabbccdd0001"

    def test_strong_verdict_when_promoted(self, tmp_path, monkeypatch):
        db = _seeded_db_path(tmp_path, promoted=True)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract execution adapter single responsibility",
            }
        )
        assert result["verdict"] == "strong"
        assert result["matches"][0]["promote_to_pattern"] is True

    def test_type_mismatch_filters_result(self, tmp_path, monkeypatch):
        db = _seeded_db_path(tmp_path, promoted=False)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "architecture_choice",
                "normalized_intent": "extract execution adapter",
            }
        )
        # decision_type='refactor_scope' doesn't match 'architecture_choice' → no matches
        assert result["verdict"] == "none"

    def test_query_echo_matches_input(self, tmp_path, monkeypatch):
        db = _seeded_db_path(tmp_path, promoted=False)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract execution adapter",
                "repo_area": "agentic_core",
            }
        )
        assert result["query_echo"]["decision_type"] == "refactor_scope"
        assert "extract" in result["query_echo"]["normalized_intent"]


# ---------------------------------------------------------------------------
# main() — stdin round-trip
# ---------------------------------------------------------------------------


class TestMain:
    def test_valid_query_exits_0_and_emits_json(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "nonexistent.sqlite")
        monkeypatch.setattr(
            sys,
            "stdin",
            StringIO(json.dumps({"decision_type": "refactor_scope", "normalized_intent": "extract adapter"})),
        )
        assert main() == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "verdict" in parsed
        assert parsed["verdict"] == "none"  # no DB → none

    def test_empty_stdin_exits_0(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "stdin", StringIO(""))
        assert main() == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed["verdict"] == "none"

    def test_invalid_json_exits_0(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "stdin", StringIO("not json <<<"))
        assert main() == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "verdict" in parsed
