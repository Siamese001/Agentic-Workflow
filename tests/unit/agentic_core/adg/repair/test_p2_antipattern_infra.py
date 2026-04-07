"""W1 tests: P2 antipattern infrastructure.

Tests:
- test_p2_rule_always_block_fix: FixP2AntipatternsRule never auto-applies code changes
- test_sqlite_analyzer_p2_antipatterns: get_p2_antipatterns() detects HIGH-severity edges
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from tools.adg.repair.rules.fix_p2_antipatterns import FixP2AntipatternsRule
from tools.adg.repair.sqlite_analyzer import SQLiteAnalyzer
from tools.adg.repair.types import Deficiency, FixCategory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_deficiency(issue_type: str, file_path: str = "foo/bar.py", line_no: int = 42) -> Deficiency:
    return Deficiency(
        id=f"test_{issue_type}",
        category=FixCategory.BLOCK_FIX,
        file_path=file_path,
        line_no=line_no,
        issue_type=issue_type,
        description=f"Test {issue_type}",
        confidence=0.95,
    )


def _make_test_db(rows: list[tuple]) -> Path:
    """Create a minimal in-memory-style SQLite DB with antipattern edges."""
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    db_path = Path(tmp.name)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            src_id INTEGER,
            dst_id INTEGER
        )
        """,
    )
    conn.execute(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            label TEXT,
            layer TEXT,
            entity_type TEXT,
            resolved_path TEXT,
            metadata TEXT
        )
        """,
    )
    conn.execute(
        """
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY,
            source_file TEXT,
            relation_type TEXT,
            symbol TEXT,
            line_no INTEGER
        )
        """,
    )
    conn.execute(
        """
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """,
    )
    conn.executemany(
        "INSERT INTO edges (id, relation_type, edge_kind, source_file, line_no, symbol) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# Tests: FixP2AntipatternsRule
# ---------------------------------------------------------------------------

class TestFixP2AntipatternsRule:
    """FixP2AntipatternsRule must never apply code changes."""

    def setup_method(self):
        self.rule = FixP2AntipatternsRule()

    @pytest.mark.parametrize("issue_type", [
        "silent_exception_swallow",
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
    ])
    def test_match_all_p2_kinds(self, issue_type: str):
        deficiency = _make_deficiency(issue_type)
        assert self.rule.match(deficiency) is True

    def test_no_match_unrelated_type(self):
        deficiency = _make_deficiency("missing_governance_edges")
        assert self.rule.match(deficiency) is False

    @pytest.mark.parametrize("issue_type", [
        "silent_exception_swallow",
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
    ])
    def test_can_fix_always_false(self, issue_type: str):
        deficiency = _make_deficiency(issue_type)
        can, reason = self.rule.can_fix(deficiency)
        assert can is False
        assert "human" in reason.lower() or "classification" in reason.lower()

    @pytest.mark.parametrize("issue_type", [
        "silent_exception_swallow",
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
    ])
    def test_apply_fix_never_succeeds(self, issue_type: str):
        deficiency = _make_deficiency(issue_type)
        result = self.rule.apply_fix(deficiency)
        assert result.success is False
        assert result.deficiency_id == deficiency.id
        assert result.error_message is not None
        assert "[P2-CLASSIFY]" in result.error_message

    @pytest.mark.parametrize("issue_type", [
        "silent_exception_swallow",
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
    ])
    def test_apply_fix_contains_remediation_hint(self, issue_type: str):
        deficiency = _make_deficiency(issue_type)
        result = self.rule.apply_fix(deficiency)
        assert result.error_message is not None
        assert issue_type in result.error_message

    def test_verify_fix_always_true(self):
        deficiency = _make_deficiency("log_and_swallow")
        from tools.adg.repair.types import FixResult
        result = FixResult(success=False, deficiency_id=deficiency.id, error_message="noop")
        assert self.rule.verify_fix(deficiency, result) is True

    def test_rule_category_is_block_fix(self):
        deficiency = _make_deficiency("return_none_swallow")
        result = self.rule.apply_fix(deficiency)
        assert result.success is False

    def test_no_file_written(self, tmp_path):
        deficiency = _make_deficiency("broad_exception_catch", file_path=str(tmp_path / "target.py"))
        (tmp_path / "target.py").write_text("pass\n")
        original_content = (tmp_path / "target.py").read_text()
        self.rule.apply_fix(deficiency)
        assert (tmp_path / "target.py").read_text() == original_content


# ---------------------------------------------------------------------------
# Tests: SQLiteAnalyzer.get_p2_antipatterns()
# ---------------------------------------------------------------------------

class TestSqliteAnalyzerP2Antipatterns:
    """SQLiteAnalyzer.get_p2_antipatterns() detects all four HIGH-severity kinds."""

    def test_detects_silent_exception_swallow(self, tmp_path):
        rows = [
            (1, "antipattern", "silent_exception_swallow", "agentic_core/foo.py", 10, "exc"),
        ]
        db_path = _make_test_db(rows)
        with SQLiteAnalyzer(db_path) as analyzer:
            results = analyzer.get_p2_antipatterns()
        assert len(results) == 1
        assert results[0]["edge_kind"] == "silent_exception_swallow"
        assert results[0]["source_file"] == "agentic_core/foo.py"
        assert results[0]["line_no"] == 10
        db_path.unlink(missing_ok=True)

    def test_detects_all_four_kinds(self, tmp_path):
        rows = [
            (1, "antipattern", "silent_exception_swallow", "a.py", 1, ""),
            (2, "antipattern", "broad_exception_catch",    "b.py", 2, ""),
            (3, "antipattern", "log_and_swallow",          "c.py", 3, ""),
            (4, "antipattern", "return_none_swallow",      "d.py", 4, ""),
        ]
        db_path = _make_test_db(rows)
        with SQLiteAnalyzer(db_path) as analyzer:
            results = analyzer.get_p2_antipatterns()
        kinds = {r["edge_kind"] for r in results}
        assert kinds == {
            "silent_exception_swallow",
            "broad_exception_catch",
            "log_and_swallow",
            "return_none_swallow",
        }
        db_path.unlink(missing_ok=True)

    def test_excludes_non_high_severity(self, tmp_path):
        rows = [
            (1, "antipattern", "mutable_default_arg", "x.py", 5, ""),
            (2, "antipattern", "star_import_use",     "y.py", 6, ""),
        ]
        db_path = _make_test_db(rows)
        with SQLiteAnalyzer(db_path) as analyzer:
            results = analyzer.get_p2_antipatterns()
        assert results == []
        db_path.unlink(missing_ok=True)

    def test_no_limit_returns_all(self, tmp_path):
        rows = [
            (i, "antipattern", "broad_exception_catch", f"file_{i}.py", i, "")
            for i in range(1, 251)
        ]
        db_path = _make_test_db(rows)
        with SQLiteAnalyzer(db_path) as analyzer:
            results = analyzer.get_p2_antipatterns()
        assert len(results) == 250
        db_path.unlink(missing_ok=True)

    def test_empty_db_returns_empty_list(self, tmp_path):
        db_path = _make_test_db([])
        with SQLiteAnalyzer(db_path) as analyzer:
            results = analyzer.get_p2_antipatterns()
        assert results == []
        db_path.unlink(missing_ok=True)

    def test_result_includes_deficiencies(self, tmp_path):
        rows = [
            (7, "antipattern", "return_none_swallow", "ops_scripts/foo.py", 99, "some_sym"),
        ]
        db_path = _make_test_db(rows)
        with SQLiteAnalyzer(db_path) as analyzer:
            deficiencies = analyzer.get_deficiencies_as_dicts()
        p2 = [d for d in deficiencies if d["issue_type"] == "return_none_swallow"]
        assert len(p2) == 1
        assert p2[0]["file_path"] == "ops_scripts/foo.py"
        assert p2[0]["line_no"] == 99
        assert p2[0]["confidence"] == 0.95
        db_path.unlink(missing_ok=True)
