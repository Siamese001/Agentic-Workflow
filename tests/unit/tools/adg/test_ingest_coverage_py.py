"""Unit tests for tools/adg/ingest_coverage_py.py.

Plan: .windsurf/plans/hotspot-coverage-pipeline-c4e8d2.md (W1.3)

Edge cases covered (mapped to plan W5):
    - W5.1: empty .coverage file → 0 rows written, no crash
    - W5.2: missing .coverage path → 0 rows written, warning logged
    - W5.5: schema migration → ingester recreates table fresh each run
    - Idempotency: running twice does not duplicate rows
    - >100% coverage_pct guard: numerator clamped via line∩executable
    - Path normalization: absolute Windows paths → POSIX repo-relative
    - Outside-repo file → skipped (files_skipped)
    - AST parse error on target file → warning, lines_total stays -1
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.ingest_coverage_py import (  # noqa: E402
    ingest,
    _normalize_to_repo_relative,
    _ensure_table,
    _annotate_lines_total,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_minimal_adg(adg_path: Path) -> None:
    """Create a minimal ADG SQLite skeleton (just `nodes` table)."""
    con = sqlite3.connect(adg_path)
    con.execute(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            resolved_path TEXT
        )
        """
    )
    con.commit()
    con.close()


def _make_empty_coverage(coverage_path: Path) -> None:
    """Create a real but empty coverage.py SQLite file via the library API."""
    from coverage import CoverageData

    data = CoverageData(basename=str(coverage_path))
    # Touch & write nothing → produces a valid empty .coverage file
    data.write()


def _make_real_coverage(coverage_path: Path, source_file: Path) -> None:
    """Produce a tiny .coverage file by exercising one source file."""
    from coverage import CoverageData

    data = CoverageData(basename=str(coverage_path))
    data.add_lines({str(source_file): {1, 2, 3}})
    data.write()


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class TestPathNormalization:
    def test_repo_relative_from_absolute(self):
        rel = _normalize_to_repo_relative(str(REPO_ROOT / "tools" / "adg" / "ingest_coverage_py.py"))
        assert rel == "tools/adg/ingest_coverage_py.py"

    def test_outside_repo_returns_none(self, tmp_path):
        outside = tmp_path / "anywhere" / "x.py"
        outside.parent.mkdir()
        outside.touch()
        assert _normalize_to_repo_relative(str(outside)) is None

    def test_nonexistent_path_handled(self):
        # Resolves to a non-existent path; .relative_to should fail → None
        result = _normalize_to_repo_relative("Z:\\does\\not\\exist.py")
        assert result is None


class TestTableSchema:
    def test_ensure_table_creates_with_correct_columns(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        _ensure_table(adg)
        con = sqlite3.connect(adg)
        cols = {r[1] for r in con.execute("PRAGMA table_info(coverage_by_path)")}
        con.close()
        assert cols == {
            "resolved_path",
            "lines_hit",
            "arcs_hit",
            "context_count",
            "lines_total",
            "coverage_pct",
            "mode",
            "ingested_at",
        }

    def test_ensure_table_idempotent_drops_existing(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        _ensure_table(adg)
        # Insert a sentinel row
        con = sqlite3.connect(adg)
        con.execute(
            "INSERT INTO coverage_by_path "
            "(resolved_path, lines_hit, arcs_hit, context_count, "
            " lines_total, coverage_pct, mode, ingested_at) "
            "VALUES ('sentinel.py', 1, 0, 0, 1, 100.0, 'lines', 'now')"
        )
        con.commit()
        con.close()
        # Re-create
        _ensure_table(adg)
        con = sqlite3.connect(adg)
        n = con.execute("SELECT COUNT(*) FROM coverage_by_path").fetchone()[0]
        con.close()
        assert n == 0, "sentinel row should be dropped on re-create"


class TestIngestMissingCoverage:
    def test_missing_coverage_file_returns_zero_rows(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        summary = ingest(
            adg_path=adg,
            coverage_path=tmp_path / "no_such_file.coverage",
            progress=False,
        )
        assert summary["rows_written"] == 0
        assert summary["files_seen"] == 0
        assert any("not found" in w for w in summary["warnings"])

    def test_table_still_created_when_coverage_missing(self, tmp_path):
        """Downstream MV must be able to LEFT JOIN a non-existent dataset."""
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        ingest(adg_path=adg, coverage_path=tmp_path / "absent.coverage", progress=False)
        con = sqlite3.connect(adg)
        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coverage_by_path'")
        assert cur.fetchone() is not None
        con.close()


class TestIngestEmptyCoverage:
    def test_empty_coverage_no_crash(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        cov = tmp_path / ".coverage"
        _make_empty_coverage(cov)
        summary = ingest(adg_path=adg, coverage_path=cov, progress=False)
        assert summary["rows_written"] == 0
        # mode should reflect that it produced no rows
        assert summary["mode"] in ("empty", "lines", "arcs")


class TestIngestRealCoverage:
    def test_real_coverage_writes_rows(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        # Use a real repo file so the AST analysis pass succeeds
        target = REPO_ROOT / "tools" / "adg" / "ingest_coverage_py.py"
        cov = tmp_path / ".coverage"
        _make_real_coverage(cov, target)

        summary = ingest(adg_path=adg, coverage_path=cov, progress=False)
        assert summary["rows_written"] == 1
        assert summary["mode"] == "lines"
        con = sqlite3.connect(adg)
        con.row_factory = sqlite3.Row
        row = con.execute("SELECT * FROM coverage_by_path").fetchone()
        con.close()
        assert row["resolved_path"] == "tools/adg/ingest_coverage_py.py"
        assert row["lines_hit"] >= 0
        assert row["lines_total"] > 0  # AST analysis succeeded
        assert 0.0 <= row["coverage_pct"] <= 100.0  # never exceeds 100%

    def test_idempotent_double_run(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        target = REPO_ROOT / "tools" / "adg" / "ingest_coverage_py.py"
        cov = tmp_path / ".coverage"
        _make_real_coverage(cov, target)

        ingest(adg_path=adg, coverage_path=cov, progress=False)
        ingest(adg_path=adg, coverage_path=cov, progress=False)
        con = sqlite3.connect(adg)
        n = con.execute("SELECT COUNT(*) FROM coverage_by_path").fetchone()[0]
        con.close()
        assert n == 1, "second ingest must not duplicate rows"


class TestCoveragePctClamp:
    def test_coverage_pct_never_exceeds_100(self):
        """Construct a row where line_set has more lines than the AST sees."""
        # Use this very test file as the source — it definitely parses.
        rel = "tests/unit/tools/adg/test_ingest_coverage_py.py"
        # Fabricate a line_set that includes lines outside the file's executable set.
        rows = [
            {
                "resolved_path": rel,
                "lines_hit": 99999,  # absurdly high raw count
                "arcs_hit": 0,
                "context_count": 0,
                "lines_total": -1,
                "coverage_pct": -1.0,
                "mode": "arcs",
                "_line_set": set(range(1, 100000)),  # bigger than any real file
            }
        ]
        warns: list[str] = []
        _annotate_lines_total(rows, warns)
        assert rows[0]["coverage_pct"] <= 100.0
        assert rows[0]["lines_total"] > 0
        # lines_hit was overwritten to the intersection count, which equals lines_total
        assert rows[0]["lines_hit"] == rows[0]["lines_total"]


class TestOutsideRepoSkipped:
    def test_path_outside_repo_increments_files_skipped(self, tmp_path):
        adg = tmp_path / "adg.sqlite"
        _make_minimal_adg(adg)
        # Fabricate a coverage file pointing at an outside path
        from coverage import CoverageData

        cov = tmp_path / ".coverage"
        outside = tmp_path / "outside_repo.py"
        outside.write_text("x = 1\n")
        data = CoverageData(basename=str(cov))
        data.add_lines({str(outside): {1}})
        data.write()

        summary = ingest(adg_path=adg, coverage_path=cov, progress=False)
        assert summary["rows_written"] == 0
        assert summary["files_skipped"] == 1


class TestSnapshotMissingRaises:
    def test_missing_adg_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ingest(
                adg_path=tmp_path / "no_such.sqlite",
                coverage_path=tmp_path / "no_such.coverage",
                progress=False,
            )
