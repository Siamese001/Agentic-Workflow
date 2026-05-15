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
# Minimal DDL to seed a test DB (mirrors post_cursor_agent_hitl_capture._DDL)
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

    def test_keeps_alphanumeric_underscore_splits_hyphen(self):
        """Underscores are kept (valid FTS5 token chars); hyphens tokenize as space
        because FTS5 parses ``foo-bar`` as the column-filter ``foo NOT bar``."""
        result = _sanitize_fts_query("refactor_scope L2-execution meta-learning")
        assert "refactor_scope" in result
        # Hyphens become spaces so FTS5 sees distinct tokens
        assert "L2 execution" in result
        assert "meta learning" in result
        assert "-" not in result

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


# ---------------------------------------------------------------------------
# Helpers for area-overlap and JOIN edge-case tests
# ---------------------------------------------------------------------------


def _seeded_db_with_area(tmp_path: Path, row_area: str = "agentic_core/L2_execution") -> Path:
    """Seeded DB: one suggestive (non-promoted) decision with configurable repo_area."""
    db = tmp_path / "ledger_area.sqlite"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SEED_DDL)
    conn.execute(
        """INSERT INTO decisions
               (decision_id, created_at, decision_type, request_summary,
                normalized_intent, recommended_option_id, status)
           VALUES ('dec_area000001', '2026-04-10T10:00:00+00:00',
                   'refactor_scope', 'refactor area test',
                   'extract adapter area overlap', 'Minimal', 'resolved')"""
    )
    conn.execute(
        "INSERT INTO decision_scope (decision_id, repo_area) VALUES ('dec_area000001', ?)",
        (row_area,),
    )
    conn.execute(
        """INSERT INTO decision_outcomes
               (decision_id, tests_passed, regression_found, rollback_required, promote_to_pattern)
           VALUES ('dec_area000001', 1, 0, 0, 0)"""
    )
    conn.execute(
        """INSERT INTO decisions_fts
               (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
           VALUES ('dec_area000001',
                   'extract adapter area overlap', 'refactor area test', '', '')"""
    )
    conn.commit()
    conn.close()
    return db


def _seeded_db_no_scope_no_outcomes(tmp_path: Path) -> Path:
    """Seeded DB: one decision with NO scope row and NO outcomes row (LEFT JOIN edge case)."""
    db = tmp_path / "ledger_minimal.sqlite"
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SEED_DDL)
    conn.execute(
        """INSERT INTO decisions
               (decision_id, created_at, decision_type, request_summary,
                normalized_intent, recommended_option_id, status)
           VALUES ('dec_noscope001', '2026-04-10T10:00:00+00:00',
                   'refactor_scope', 'refactor without scope or outcomes',
                   'extract adapter minimal test', 'Minimal', 'resolved')"""
    )
    conn.execute(
        """INSERT INTO decisions_fts
               (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
           VALUES ('dec_noscope001',
                   'extract adapter minimal test',
                   'refactor without scope or outcomes', '', '')"""
    )
    conn.commit()
    conn.close()
    return db


# ---------------------------------------------------------------------------
# TestRepoAreaOverlap — area_overlaps = row_area.startswith(repo_area[:30])
# ---------------------------------------------------------------------------


class TestRepoAreaOverlap:
    def test_no_query_area_matches_any_row(self, tmp_path, monkeypatch):
        """Empty repo_area in query → area check bypassed entirely."""
        db = _seeded_db_with_area(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter area overlap",
                "repo_area": "",
            }
        )
        assert result["verdict"] in ("suggestive", "strong")

    def test_exact_area_match(self, tmp_path, monkeypatch):
        db = _seeded_db_with_area(tmp_path, row_area="agentic_core/L2_execution")
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter area overlap",
                "repo_area": "agentic_core/L2_execution",
            }
        )
        assert result["verdict"] in ("suggestive", "strong")

    def test_prefix_area_matches(self, tmp_path, monkeypatch):
        """A query area shorter than the row area matches when it is a prefix."""
        db = _seeded_db_with_area(tmp_path, row_area="agentic_core/L2_execution")
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter area overlap",
                "repo_area": "agentic_core",
            }
        )
        assert result["verdict"] in ("suggestive", "strong")

    def test_non_overlapping_area_filters_out(self, tmp_path, monkeypatch):
        """Query area with no prefix overlap → no match returned."""
        db = _seeded_db_with_area(tmp_path, row_area="agentic_core/L2_execution")
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter area overlap",
                "repo_area": "apps_rg",
            }
        )
        assert result["verdict"] == "none"

    def test_query_area_over_30_chars_uses_truncated_prefix(self, tmp_path, monkeypatch):
        """repo_area[:30] truncation: a 31-char query checks only the first 30 chars.
        row_area 'agentic_core/L2_execution/adapters' must start with the 30-char prefix."""
        db = _seeded_db_with_area(tmp_path, row_area="agentic_core/L2_execution/adapters")
        monkeypatch.setattr(_m, "DB_PATH", db)
        query_area = "agentic_core/L2_execution/adapt"  # 31 chars; [:30]="agentic_core/L2_execution/adap"
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter area overlap",
                "repo_area": query_area,
            }
        )
        assert result["verdict"] in ("suggestive", "strong")


# ---------------------------------------------------------------------------
# TestScopeOutcomesJoins — LEFT JOIN behavior on missing rows
# ---------------------------------------------------------------------------


class TestScopeOutcomesJoins:
    def test_missing_scope_and_outcomes_still_returns_match(self, tmp_path, monkeypatch):
        """LEFT JOIN on both tables: absent rows do not suppress the match."""
        db = _seeded_db_no_scope_no_outcomes(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter minimal test",
            }
        )
        assert result["verdict"] == "suggestive"

    def test_missing_scope_sets_repo_area_empty_string(self, tmp_path, monkeypatch):
        """No decision_scope row → repo_area in match is '' (None coerced by 'or \"\"')."""
        db = _seeded_db_no_scope_no_outcomes(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter minimal test",
            }
        )
        assert result["matches"][0]["repo_area"] == ""

    def test_missing_outcomes_defaults_promote_to_pattern_false(self, tmp_path, monkeypatch):
        """No decision_outcomes row → promote_to_pattern=False → verdict stays suggestive."""
        db = _seeded_db_no_scope_no_outcomes(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract adapter minimal test",
            }
        )
        assert result["matches"][0]["promote_to_pattern"] is False

    def test_scope_and_outcomes_fields_present_in_full_join(self, tmp_path, monkeypatch):
        """When both rows exist, repo_area and tests_passed are visible in the match."""
        db = _seeded_db_path(tmp_path, promoted=False)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "extract execution adapter",
            }
        )
        assert result["verdict"] in ("suggestive", "strong")
        match = result["matches"][0]
        assert match["repo_area"] == "agentic_core/L2_execution"
        assert match["tests_passed"] is True


# ---------------------------------------------------------------------------
# TestFtsEdgeCases — sanitization and FTS5 error handling
# ---------------------------------------------------------------------------


class TestFtsEdgeCases:
    def test_all_special_chars_returns_none_verdict(self, tmp_path, monkeypatch):
        """normalized_intent of only special chars → sanitized to '' → 'none' with reason."""
        db = _seeded_db_path(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "!@#$%^&*()+[]{}",
            }
        )
        assert result["verdict"] == "none"
        assert "reason" in result

    def test_hyphen_only_query_handled_gracefully(self, tmp_path, monkeypatch):
        """Hyphen-only sanitizes to empty string — must return none with a reason,
        not raise an FTS5 OperationalError."""
        db = _seeded_db_path(tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", db)
        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "--- --- ---",
            }
        )
        assert result["verdict"] == "none"
        assert "reason" in result

    def test_hyphenated_intent_surfaces_precedent(self, tmp_path, monkeypatch):
        """Regression: hyphenated intents like ``meta-learning enrichment`` must
        return precedent when the ledger contains a matching row. Before the fix,
        FTS5 treated ``meta-learning`` as a column-filter and raised
        ``OperationalError: no such column: learning`` which the except-clause
        swallowed, hiding real precedent from Author-Gate scoring."""
        db = tmp_path / "ledger_hyphen.sqlite"
        conn = sqlite3.connect(str(db))
        conn.executescript(_SEED_DDL)
        conn.execute(
            """INSERT INTO decisions
                   (decision_id, created_at, decision_type, request_summary,
                    normalized_intent, recommended_option_id, status)
               VALUES ('dec_meta00000001', '2026-04-23T23:00:00+00:00',
                       'refactor_scope',
                       'W1+W2+W3 meta-learning enrichment',
                       'meta-learning fidelity enrichment scope',
                       'W1+W2+W3 meta-learning enrichment', 'resolved')"""
        )
        conn.execute(
            """INSERT INTO decision_outcomes
                   (decision_id, tests_passed, regression_found,
                    rollback_required, promote_to_pattern)
               VALUES ('dec_meta00000001', 1, 0, 0, 0)"""
        )
        conn.execute(
            """INSERT INTO decisions_fts
                   (decision_id, normalized_intent, request_summary,
                    user_goal, selection_rationale)
               VALUES ('dec_meta00000001',
                       'meta-learning fidelity enrichment scope',
                       'W1+W2+W3 meta-learning enrichment', '', '')"""
        )
        conn.commit()
        conn.close()
        monkeypatch.setattr(_m, "DB_PATH", db)

        result = lookup(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "meta-learning enrichment",
            }
        )
        assert result["verdict"] in ("suggestive", "strong"), (
            f"Expected precedent to surface for hyphenated intent, got {result!r}"
        )
        assert any(m["decision_id"] == "dec_meta00000001" for m in result["matches"])
