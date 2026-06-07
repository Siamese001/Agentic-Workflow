"""Regression tests for agentic_core.adg.processing.phase2_disposition_processor.

Covers two historical bugs discovered during Wave-1 tech-debt cleanup
(plan docs/archive/windsurf/legacy-tree/plans/repo-tech-debt-wave1-b3c8d1.md):

1. SQL template rendering bug — plain-string line in a concatenated f-string +
   str.format() template used `{{disposition_filter}}` (double braces) while
   sibling f-string lines used `{{X}}` that pre-resolved to `{X}`. The plain
   string preserved `{{...}}` literally; after `.format()` the double braces
   became literal `{X}` in the SQL, causing SQLite to reject with
   `unrecognized token: "{"`. Entire phase2 pipeline was silently inert —
   every guardian-annotated antipattern across the repo stayed `untriaged`.

2. Ambiguous column name — unqualified `line_no` and `evidence` identifiers
   in the SELECT / ORDER BY clauses matched both `violations.line_no` and
   `edges.line_no` under `violations v LEFT JOIN edges e`, producing
   `ambiguous column name: line_no`.

Both bugs reproduce with a minimal in-memory ADG-like SQLite database.
"""

from __future__ import annotations

import sqlite3
import textwrap
from pathlib import Path

import pytest

from agentic_core.adg.processing.phase2_disposition_processor import (
    run_phase2_disposition_processing,
)


def _build_minimal_adg(db_path: Path, source_file: Path, line_no: int) -> None:
    """Create a minimal ADG-schema SQLite with one antipattern violation
    whose edge has an exception-handler edge_kind matching a guardian
    comment at the given source line.
    """
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            semantic_type TEXT
        );
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY,
            edge_id INTEGER,
            category TEXT,
            evidence TEXT,
            file_path TEXT,
            line_no INTEGER,
            disposition TEXT DEFAULT 'untriaged',
            disposition_source TEXT,
            disposition_date TEXT,
            severity TEXT,
            violation_class TEXT
        );
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            resolved_path TEXT,
            span_line INTEGER,
            span_end_line INTEGER
        );
        """
    )
    conn.execute(
        "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, "
        "source_file, line_no, symbol, semantic_type) VALUES "
        "(1, 100, 200, 'antipattern', 'silent_exception_swallow', ?, ?, "
        "'OSError', 'antipattern_silent_swallow')",
        (str(source_file).replace("\\", "/"), line_no),
    )
    conn.execute(
        "INSERT INTO violations (id, edge_id, category, evidence, file_path, "
        "line_no, disposition, severity, violation_class) VALUES "
        "(1, 1, 'antipattern', 'OSError', ?, ?, 'untriaged', 'HIGH', 'hygiene')",
        (str(source_file).replace("\\", "/"), line_no),
    )
    conn.commit()
    conn.close()


@pytest.fixture
def adg_with_guardian_violation(tmp_path: Path) -> tuple[Path, Path]:
    """Return (db_path, source_file_path) for a guardian-annotated violation."""
    source_file = tmp_path / "sample_module.py"
    source_file.write_text(
        textwrap.dedent(
            """\
            def do_work():
                try:
                    open('missing')
                except OSError:  # guardian: allow-silent-swallow -- regression-test sample guardian annotation
                    pass
            """
        ),
        encoding="utf-8",
    )
    # Guardian line is line 3 (1-indexed): the `except` header
    db_path = tmp_path / "adg.sqlite"
    _build_minimal_adg(db_path, source_file, line_no=3)
    return db_path, source_file


@pytest.fixture
def adg_with_w5_variant_tokens(tmp_path: Path) -> Path:
    """Seed a DB with violations whose guardian comments use W5.1 variant tokens.

    Validates that `allow-import-fail`, `allow-rollback-failure`,
    `allow-broad-except`, etc. now match after the Wave-5.1 vocabulary expansion.
    """
    # Three distinct source files, each with a different variant token
    sources = {
        "import_fail_site.py": (
            "def f():\n"
            "    try:\n"
            "        import foo\n"
            "    except ImportError:  # guardian: allow-import-fail -- optional dependency\n"
            "        pass\n",
            4,  # line_no of except
            "silent_exception_swallow",
        ),
        "broad_except_site.py": (
            "def g():\n"
            "    try:\n"
            "        work()\n"
            "    except Exception as exc:  # guardian: allow-broad-except -- outer safety net\n"
            "        raise\n",
            4,
            "broad_exception_catch",
        ),
        "rollback_site.py": (
            "def h(conn):\n"
            "    try:\n"
            "        conn.rollback()\n"
            "    except Exception:  # guardian: allow-rollback-failure -- best-effort cleanup\n"
            "        pass\n",
            4,
            "silent_exception_swallow",
        ),
    }
    db_path = tmp_path / "adg.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INTEGER, dst_id INTEGER,
            relation_type TEXT, edge_kind TEXT, source_file TEXT, line_no INTEGER,
            symbol TEXT, semantic_type TEXT);
        CREATE TABLE violations (id INTEGER PRIMARY KEY, edge_id INTEGER,
            category TEXT, evidence TEXT, file_path TEXT, line_no INTEGER,
            disposition TEXT DEFAULT 'untriaged', disposition_source TEXT,
            disposition_date TEXT, severity TEXT, violation_class TEXT);
        CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT,
            resolved_path TEXT, span_line INTEGER, span_end_line INTEGER);
        """
    )
    for idx, (fname, (body, ln, edge_kind)) in enumerate(sources.items(), 1):
        src = tmp_path / fname
        src.write_text(body, encoding="utf-8")
        src_posix = str(src).replace("\\", "/")
        conn.execute(
            "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, "
            "source_file, line_no, symbol, semantic_type) VALUES "
            "(?, ?, ?, 'antipattern', ?, ?, ?, 'Exc', ?)",
            (idx, idx * 10, idx * 20, edge_kind, src_posix, ln, f"antipattern_{edge_kind}"),
        )
        conn.execute(
            "INSERT INTO violations (id, edge_id, category, evidence, file_path, "
            "line_no, disposition, severity, violation_class) VALUES "
            "(?, ?, 'antipattern', 'SampleExc', ?, ?, 'untriaged', 'HIGH', 'hygiene')",
            (idx, idx, src_posix, ln),
        )
    conn.commit()
    conn.close()
    return db_path


class TestW5VariantTokenRecognition:
    """Regression coverage for Wave-5.1 expanded guardian vocabulary."""

    def test_all_three_variant_tokens_recognized(
        self,
        adg_with_w5_variant_tokens: Path,
    ) -> None:
        """`allow-import-fail`, `allow-broad-except`, `allow-rollback-failure`
        must all auto-disposition to `approved` after Wave-5.1 expansion.
        """
        result = run_phase2_disposition_processing(adg_with_w5_variant_tokens)
        assert result["approved"] == 3, f"Expected all 3 variant-token sites approved, got {result}"

    def test_log_and_swallow_aliases_return_none_swallow(
        self,
        tmp_path: Path,
    ) -> None:
        """Scanner misclassification: `except X: Logger.debug(...)` with an
        enclosing `return None` gets edge_kind=return_none_swallow, but authors
        annotate it as allow-log-and-swallow. W5.1 accepts that alias.
        """
        src = tmp_path / "return_none_logged.py"
        src.write_text(
            "def compute():\n"
            "    try:\n"
            "        return do_work()\n"
            "    except ValueError as exc:  # guardian: allow-log-and-swallow -- non-fatal, caller handles None\n"
            "        import logging; logging.getLogger(__name__).debug('failed: %s', exc)\n"
            "    return None\n",
            encoding="utf-8",
        )
        db_path = tmp_path / "adg.sqlite"
        conn = sqlite3.connect(str(db_path))
        conn.executescript(
            """
            CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INTEGER, dst_id INTEGER,
                relation_type TEXT, edge_kind TEXT, source_file TEXT, line_no INTEGER,
                symbol TEXT, semantic_type TEXT);
            CREATE TABLE violations (id INTEGER PRIMARY KEY, edge_id INTEGER,
                category TEXT, evidence TEXT, file_path TEXT, line_no INTEGER,
                disposition TEXT DEFAULT 'untriaged', disposition_source TEXT,
                disposition_date TEXT, severity TEXT, violation_class TEXT);
            CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT,
                resolved_path TEXT, span_line INTEGER, span_end_line INTEGER);
            """
        )
        sp = str(src).replace("\\", "/")
        conn.execute(
            "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, "
            "source_file, line_no, symbol, semantic_type) VALUES "
            "(1, 1, 2, 'antipattern', 'return_none_swallow', ?, 4, 'ValueError', "
            "'antipattern_return_none')",
            (sp,),
        )
        conn.execute(
            "INSERT INTO violations (id, edge_id, category, evidence, file_path, "
            "line_no, disposition, severity, violation_class) VALUES "
            "(1, 1, 'antipattern', 'ValueError', ?, 4, 'untriaged', 'HIGH', 'hygiene')",
            (sp,),
        )
        conn.commit()
        conn.close()
        result = run_phase2_disposition_processing(db_path)
        assert result["approved"] == 1, (
            f"log-and-swallow alias for return_none_swallow should approve; got {result}"
        )


class TestPhase2DispositionProcessor:
    """Regression coverage for phase2 SQL template + column-qualification bugs."""

    def test_sql_template_renders_without_operational_error(
        self,
        adg_with_guardian_violation: tuple[Path, Path],
    ) -> None:
        """Bug 1 regression: `{{disposition_filter}}` on plain-string line
        used to survive `.format()` as literal `{disposition_filter}` and
        SQLite would raise `unrecognized token: "{"`. Bug 2 regression:
        unqualified `line_no` used to raise `ambiguous column name: line_no`.

        Passing assertion: phase2 completes without raising sqlite3.OperationalError.
        """
        db_path, _ = adg_with_guardian_violation
        # Must not raise sqlite3.OperationalError
        result = run_phase2_disposition_processing(db_path)
        assert isinstance(result, dict)
        assert "approved" in result
        assert "tested" in result
        assert "remaining" in result

    def test_guardian_annotated_violation_auto_approved(
        self,
        adg_with_guardian_violation: tuple[Path, Path],
    ) -> None:
        """End-to-end: a guardian-annotated `except OSError` with a matching
        canonical token should be auto-dispositioned to 'approved'.
        """
        db_path, _ = adg_with_guardian_violation
        result = run_phase2_disposition_processing(db_path)
        assert result["approved"] == 1, f"Expected exactly 1 guardian-approved violation, got {result}"

        # Verify the DB row directly
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT disposition, disposition_source FROM violations WHERE id = 1"
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        disposition, source = row
        assert disposition == "approved", f"Expected disposition='approved', got {disposition!r}"
        assert source and "guardian" in source.lower()
