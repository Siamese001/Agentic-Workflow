#!/usr/bin/env python3
"""
Phase 2 Tests: Auto-disposition processor linking test coverage and guardian comments.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core" / "adg" / "processing"))
from phase2_disposition_processor import (
    ViolationDispositionProcessor,
    ViolationInfo,
    TestCoverage,
    GuardianComment,
    run_phase2_disposition_processing
)


class TestPhase2DispositionProcessor:
    """§1.5 Edge case: Phase 2 processor handles all scenarios correctly."""

    @pytest.fixture
    def phase2_adg_db(self) -> Generator[Path, None, None]:
        """Create a comprehensive ADG SQLite with Phase 2 test data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "phase2_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Basic schema
                conn.execute("""
                    CREATE TABLE nodes (
                        id INTEGER PRIMARY KEY,
                        adg_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        layer TEXT NOT NULL,
                        resolved_path TEXT NOT NULL,
                        span_line INTEGER DEFAULT 0,
                        span_end_line INTEGER DEFAULT 0
                    )
                """)

                conn.execute("""
                    CREATE TABLE edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src_id INTEGER NOT NULL REFERENCES nodes(id),
                        dst_id INTEGER NOT NULL REFERENCES nodes(id),
                        relation_type TEXT NOT NULL,
                        edge_kind TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        line_no INTEGER NOT NULL,
                        symbol TEXT NOT NULL DEFAULT ''
                    )
                """)

                # Phase 1: Extended violations schema
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        edge_id INTEGER NOT NULL REFERENCES edges(id),
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        disposition_source TEXT DEFAULT '',
                        disposition_date TEXT DEFAULT '',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert comprehensive test data

                # 1. Nodes for violations
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'violation::module1', 'module', 'L0', 'test_file1.py', 1, 50)")
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'violation::symbol1', 'symbol', 'L0', 'test_file1.py', 10, 15)")

                # 2. Nodes for tests
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (101, 'test::test_func1', 'symbol', 'tests', 'test_coverage.py', 5, 20)")

                # 3. Violation edges
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 2, 'antipattern', 'silent_exception_swallow', 'test_file1.py', 12, 'except:Exception')
                """)

                # 4. Test coverage edges (tests_execution_of)
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (2, 101, 2, 'tests_execution_of', 'test_linkage', 'test_coverage.py', 8, 'risky_function')
                """)

                # 5. Violations with different dispositions
                # Untriaged violation (should be auto-dispositioned)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'test_file1.py', 12, 'MEDIUM', 'untriaged')
                """)

                # Already tested violation (should be skipped)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition, disposition_source)
                    VALUES (1, 'antipattern', 'except:Exception', 'test_file1.py', 13, 'MEDIUM', 'tested', 'test:existing_test')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_loads_untriaged_violations_only(self, phase2_adg_db: Path) -> None:
        """§1.4: Only untriaged violations are loaded for processing."""
        with ViolationDispositionProcessor(phase2_adg_db) as processor:
            violations = processor._load_untriaged_violations()

            # Should only load the untriaged violation
            assert len(violations) == 1
            assert violations[0].disposition == 'untriaged'
            assert violations[0].line_no == 12
            assert violations[0].file_path == 'test_file1.py'

    def test_loads_test_coverage_with_line_spans(self, phase2_adg_db: Path) -> None:
        """§1.1: Test coverage includes line span information."""
        with ViolationDispositionProcessor(phase2_adg_db) as processor:
            coverage = processor._load_test_coverage()

            assert len(coverage) == 1
            tc = coverage[0]
            assert tc.test_name == 'test::test_func1'
            assert tc.target_file == 'test_file1.py'
            assert tc.target_line_start == 10
            assert tc.target_line_end == 15

    def test_auto_disposition_by_test_coverage(self, phase2_adg_db: Path) -> None:
        """§1.3: Violations covered by tests are auto-marked as 'tested'."""
        with ViolationDispositionProcessor(phase2_adg_db) as processor:
            violations = processor._load_untriaged_violations()
            test_coverage = processor._load_test_coverage()
            guardian_comments = []

            # Test the disposition logic
            violation = violations[0]
            disposition, source = processor._determine_disposition(violation, test_coverage, guardian_comments)

            assert disposition == 'tested'
            assert source == 'test:test::test_func1'

    def test_complete_feedback_loop(self, phase2_adg_db: Path) -> None:
        """§1.3: Complete detection→validation feedback loop works end-to-end."""
        # Initial state: 1 untriaged violation
        conn = sqlite3.connect(str(phase2_adg_db))
        try:
            cursor = conn.execute("SELECT disposition, disposition_source FROM violations WHERE id = 1")
            initial = cursor.fetchone()
            assert initial[0] == 'untriaged'
            assert initial[1] == ''
        finally:
            conn.close()

        # Run Phase 2 processing
        results = run_phase2_disposition_processing(phase2_adg_db)

        # Verify results
        assert results['tested'] == 1
        assert results['approved'] == 0
        assert results['remaining'] == 0

        # Verify ADG was updated
        conn = sqlite3.connect(str(phase2_adg_db))
        try:
            cursor = conn.execute("SELECT disposition, disposition_source, disposition_date FROM violations WHERE id = 1")
            updated = cursor.fetchone()
            assert updated[0] == 'tested'
            assert updated[1] == 'test:test::test_func1'
            assert updated[2] != ''  # timestamp should be set
        finally:
            conn.close()


class TestPhase2ErrorHandling:
    """§1.6 & §1.8: Error handling and fail-closed behavior."""

    def test_missing_adg_file_error(self) -> None:
        """§1.8: Missing ADG file fails with clear error."""
        with pytest.raises(FileNotFoundError):
            run_phase2_disposition_processing(Path("nonexistent.sqlite"))

    def test_empty_violations_table(self) -> None:
        """§1.5: Handle empty violations table."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_phase2.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')"
                ]:
                    conn.execute(table)
                conn.commit()
            finally:
                conn.close()

            results = run_phase2_disposition_processing(db_path)
            assert results['tested'] == 0
            assert results['approved'] == 0
            assert results['remaining'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
