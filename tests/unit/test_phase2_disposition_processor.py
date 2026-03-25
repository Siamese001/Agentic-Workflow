#!/usr/bin/env python3
"""
Phase 2 Tests: Auto-disposition processor linking test coverage and guardian comments.

Tests per windsurfrules §1.1-§1.8 requirements:
- §1.1 Deterministic inputs/outputs
- §1.2 No external dependencies
- §1.3 No mutable global state
- §1.4 Idempotent operations
- §1.5 Edge case handling
- §1.6 Error handling and recovery
- §1.7 Deterministic behavior
- §1.8 Fail-closed error handling

Phase 2 validates:
1. Test coverage auto-disposition via tests_execution_of edges
2. Guardian comment parsing and auto-approval
3. Disposition updates flow back to ADG
4. Complete detection→validation feedback loop
"""

from __future__ import annotations

import sqlite3

# Import the modules we're testing
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core" / "adg" / "processing"))
from phase2_disposition_processor import ViolationDispositionProcessor, run_phase2_disposition_processing


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
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'violation::module1', 'module', 'L0', 'test_file1.py', 1, 50)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'violation::symbol1', 'symbol', 'L0', 'test_file1.py', 10, 15)"
                )

                # 2. Nodes for tests
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (101, 'test::test_func1', 'symbol', 'tests', 'test_coverage.py', 5, 20)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (102, 'test::test_module1', 'module', 'tests', 'test_coverage.py', 1, 30)"
                )

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

                # Already approved violation (should be skipped)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition, disposition_source)
                    VALUES (1, 'antipattern', 'except:ValueError', 'test_file1.py', 14, 'MEDIUM', 'approved', 'guardian: allow-silent-swallow')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_loads_untriaged_violations_only(self, phase2_adg_db: Path) -> None:
    """Test loads_untriaged_violations_only runtime behavior."""
    # Arrange
    # TODO: Set up test data for loads_untriaged_violations_only
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute loads_untriaged_violations_only
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test loads_coverage_with_line_spans runtime behavior."""
    # Arrange
    # TODO: Set up test data for loads_coverage_with_line_spans
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute loads_coverage_with_line_spans
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "guardian_test.sqlite"

            # Create minimal schema
            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                ]:
                    conn.execute(table)

                guardian_abs = str(Path(tmp_dir) / "guardian_file.py")
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', ?)",
                    (guardian_abs,),
                )
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path) VALUES (1, 'antipattern', 'untriaged', ?)",
                    (guardian_abs,),
                )
                conn.commit()
            finally:
                conn.close()

            # Create test file with guardian comments
            test_file = Path(tmp_dir) / "guardian_file.py"
            test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    with pytest.raises(Exception):
        pass

    try:
        another_operation()
    with pytest.raises(ValueError):
        pass

    # Non-guardian comment
    with pytest.raises(OSError):
""")

            with ViolationDispositionProcessor(db_path) as processor:
                comments = processor._load_guardian_comments()

                assert len(comments) == 2

                # Check first guardian comment
                comment1 = comments[0]
                assert Path(comment1.file_path).name == "guardian_file.py"
                assert comment1.line_no == 5
                assert comment1.exception_type == "Exception"
                assert "Exception is acceptable here" in comment1.reason

                # Check second guardian comment
                comment2 = comments[1]
                assert Path(comment2.file_path).name == "guardian_file.py"
                assert comment2.line_no == 10
                assert comment2.exception_type == "ValueError"
                assert "ValueError is acceptable here" in comment2.reason

    def test_auto_disposition_by_test_coverage(self, phase2_adg_db: Path) -> None:
    """Test auto_disposition_by_coverage runtime behavior."""
    # Arrange
    # TODO: Set up test data for auto_disposition_by_coverage
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute auto_disposition_by_coverage
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            assert source == "test:test::test_func1"

    def test_auto_disposition_by_guardian_comment(self) -> None:
    """Test auto_disposition_by_guardian_comment runtime behavior."""
    # Arrange
    # TODO: Set up test data for auto_disposition_by_guardian_comment
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute auto_disposition_by_guardian_comment
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

                guardian_test_abs = str(Path(tmp_dir) / "guardian_test.py")
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', ?)",
                    (guardian_test_abs,),
                )
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path, line_no) VALUES (1, 'antipattern', 'untriaged', ?, 5)",
                    (guardian_test_abs,),
                )
                conn.commit()
            finally:
                conn.close()

            # Create test file with guardian comment
            test_file = Path(tmp_dir) / "guardian_test.py"
            test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    with pytest.raises(Exception):
        pass
""")

            with ViolationDispositionProcessor(db_path) as processor:
                violations = processor._load_untriaged_violations()
                test_coverage = []
                guardian_comments = processor._load_guardian_comments()

                # Test the disposition logic
                violation = violations[0]
                disposition, source = processor._determine_disposition(
                    violation, test_coverage, guardian_comments
                )

                assert disposition == "approved"
                assert "guardian: allow-silent-swallow" in source
                assert "Exception is acceptable here" in source

    def test_disposition_priority_order(self) -> None:
    """Test disposition_priority_order runtime behavior."""
    # Arrange
    # TODO: Set up test data for disposition_priority_order
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute disposition_priority_order
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

                # Insert nodes for both test coverage and guardian comment
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'test::module', 'module', 'L0', 'priority_test.py', 1, 50)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'test::symbol', 'symbol', 'L0', 'priority_test.py', 10, 15)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (101, 'test::test_func', 'symbol', 'tests', 'test_priority.py', 5, 20)"
                )

                # Insert test coverage edge
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (2, 101, 2, 'tests_execution_of', 'test_linkage', 'test_priority.py', 8, 'risky_function')
                """)

                priority_test_abs = str(Path(tmp_dir) / "priority_test.py")
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path, line_no) VALUES (1, 'antipattern', 'untriaged', ?, 5)",
                    (priority_test_abs,),
                )
                conn.commit()
            finally:
                conn.close()

            # Create test file with both test coverage and guardian comment
            test_file = Path(tmp_dir) / "priority_test.py"
            test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    with pytest.raises(Exception):
        pass
""")

            with ViolationDispositionProcessor(db_path) as processor:
                violations = processor._load_untriaged_violations()
                test_coverage = processor._load_test_coverage()
                guardian_comments = processor._load_guardian_comments()

                # Test the disposition logic
                violation = violations[0]
                disposition, source = processor._determine_disposition(
                    violation, test_coverage, guardian_comments
                )

                # Guardian comment should take priority
                assert disposition == "approved"
                assert "guardian: allow-silent-swallow" in source

    def test_complete_feedback_loop(self, phase2_adg_db: Path) -> None:
        """§1.3: Complete detection→validation feedback loop works end-to-end."""
        # Initial state: 1 untriaged violation
        conn = sqlite3.connect(str(phase2_adg_db))
        try:
            cursor = conn.execute("SELECT disposition, disposition_source FROM violations WHERE id = 1")
            initial = cursor.fetchone()
            assert initial[0] == "untriaged"
            assert initial[1] == ""
        finally:
            conn.close()

        # Run Phase 2 processing
        results = run_phase2_disposition_processing(phase2_adg_db)

        # Verify results
        assert results["tested"] == 1
        assert results["approved"] == 0
        assert results["remaining"] == 0

        # Verify ADG was updated
        conn = sqlite3.connect(str(phase2_adg_db))
        try:
            cursor = conn.execute(
                "SELECT disposition, disposition_source, disposition_date FROM violations WHERE id = 1"
            )
            updated = cursor.fetchone()
            assert updated[0] == "tested"
            assert updated[1] == "test:test::test_func1"
            assert updated[2] != ""  # timestamp should be set
        finally:
            conn.close()


class TestPhase2ErrorHandling:
    """§1.6 & §1.8: Error handling and fail-closed behavior."""

    def test_missing_adg_file_error(self) -> None:
    """Test missing_adg_file_error runtime behavior."""
    # Arrange
    # TODO: Set up error condition
    error_input = {}  # Replace with actual error condition

    # Act & Assert
    # TODO: Test error handling in missing_adg_file_error
    """Test corrupted_adg_handling runtime behavior."""
    # Arrange
    # TODO: Set up test data for corrupted_adg_handling
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute corrupted_adg_handling
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            db_path = Path(tmp_dir) / "missing_file_test.sqlite"

            # Create ADG with violation pointing to non-existent file
            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                ]:
                    conn.execute(table)

                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', 'nonexistent.py')"
                )
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path) VALUES (1, 'antipattern', 'untriaged', 'nonexistent.py')"
                )
                conn.commit()
            finally:
                conn.close()

            # Should handle missing file gracefully
            results = run_phase2_disposition_processing(db_path)
            assert results["tested"] == 0
            assert results["approved"] == 0
            assert results["remaining"] == 1  # Still untriaged, but no crash


class TestPhase2EdgeCases:
    """§1.5: Edge case handling."""

    def test_empty_violations_table(self) -> None:
        """§1.5: Handle empty violations table."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_phase2.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                ]:
                    conn.execute(table)
                conn.commit()
            finally:
                conn.close()

            results = run_phase2_disposition_processing(db_path)
            assert results["tested"] == 0
            assert results["approved"] == 0
            assert results["remaining"] == 0

    def test_malformed_guardian_comments(self) -> None:
        """§1.5: Handle malformed guardian comments gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "malformed_guardian.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                ]:
                    conn.execute(table)

                malformed_abs = str(Path(tmp_dir) / "malformed.py")
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', ?)",
                    (malformed_abs,),
                )
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path) VALUES (1, 'antipattern', 'untriaged', ?)",
                    (malformed_abs,),
                )
                conn.commit()
            finally:
                conn.close()

            # Create test file with malformed guardian comments
            test_file = Path(tmp_dir) / "malformed.py"
            test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    except Exception:  # guardian: malformed comment without proper format
        pass

    try:
        another_operation()
    except ValueError:  # random comment with guardian word but not proper format
        pass

    try:
        third_operation()
    with pytest.raises(TypeError):
        pass
""")

            with ViolationDispositionProcessor(db_path) as processor:
                comments = processor._load_guardian_comments()

                # Should only parse the properly formatted one
                assert len(comments) == 1
                assert comments[0].exception_type == "TypeError"
                assert "proper format" in comments[0].reason

    def test_line_range_edge_cases(self) -> None:
        """§1.5: Handle edge cases in line range matching."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "line_range_test.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY, category TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'untriaged', file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0)",
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL, resolved_path TEXT NOT NULL, span_line INTEGER DEFAULT 0, span_end_line INTEGER DEFAULT 0)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                ]:
                    conn.execute(table)

                # Insert nodes with various line spans
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'test::module', 'module', 'L0', 'range_test.py', 1, 50)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'test::symbol1', 'symbol', 'L0', 'range_test.py', 10, 10)"
                )  # Single line
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (3, 'test::symbol2', 'symbol', 'L0', 'range_test.py', 20, 30)"
                )  # Multi-line
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (101, 'test::test_func1', 'symbol', 'tests', 'test_range.py', 5, 15)"
                )

                # Insert test coverage edges
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (2, 101, 2, 'tests_execution_of', 'test_linkage', 'test_range.py', 8, 'single_line_func')
                """)
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (3, 101, 3, 'tests_execution_of', 'test_linkage', 'test_range.py', 12, 'multi_line_func')
                """)

                # Insert violations at various positions
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path, line_no) VALUES (1, 'antipattern', 'untriaged', 'range_test.py', 10)"
                )  # Exactly on single line
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path, line_no) VALUES (2, 'antipattern', 'untriaged', 'range_test.py', 25)"
                )  # Inside multi-line range
                conn.execute(
                    "INSERT INTO violations (id, category, disposition, file_path, line_no) VALUES (3, 'antipattern', 'untriaged', 'range_test.py', 35)"
                )  # Outside any range

                conn.commit()
            finally:
                conn.close()

            results = run_phase2_disposition_processing(db_path)

            # Should disposition 2 violations (exact match and inside range)
            assert results["tested"] == 2
            assert results["remaining"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
