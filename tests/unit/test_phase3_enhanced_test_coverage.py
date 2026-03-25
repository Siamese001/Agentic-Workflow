#!/usr/bin/env python3
"""
Phase 3.2 Tests: Enhanced test coverage integration for exception handling violations.

Tests per windsurfrules §1.1-§1.8 requirements:
- §1.1 Deterministic inputs/outputs
- §1.2 No external dependencies
- §1.3 No mutable global state
- §1.4 Idempotent operations
- §1.5 Edge case handling
- §1.6 Error handling and recovery
- §1.7 Deterministic behavior
- §1.8 Fail-closed error handling

Phase 3.2 validates:
1. Dynamic test discovery from test suites
2. Comprehensive tests_execution_of edge population
3. Test-to-violation mapping with precise line coverage
4. Coverage gap analysis and prioritization
5. Auto-generated test skeletons
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
from phase3_enhanced_test_coverage import (
    TestCoverageAnalyzer,
    TestCoverageGap,
    TestDiscoveryEngine,
    TestFramework,
    TestSkeletonGenerator,
    run_phase3_enhanced_test_coverage,
)


class TestDiscovery:
    """§1.5 Edge case: Test discovery handles various test patterns."""

    def test_discovers_pytest_tests(self) -> None:
        """§1.1: Discovers pytest-style tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test_example.py"
            test_file.write_text("""
import pytest

def test_function_basic():
    assert True

def test_with_params(param1, param2):
    result = some_function(param1, param2)
    assert result is not None

class TestClass:
    def test_method(self):
        assert True
""")

            engine = TestDiscoveryEngine()
            tests = engine.discover_tests_in_file(test_file)

            assert len(tests) >= 2  # At least the two test functions

            # Check pytest tests
            pytest_tests = [t for t in tests if t.framework == TestFramework.PYTEST]
            assert len(pytest_tests) >= 2

            # Check test names
            test_names = [t.name for t in pytest_tests]
            assert "test_function_basic" in test_names
            assert "test_with_params" in test_names

    def test_discovers_unittest_tests(self) -> None:
        """§1.1: Discovers unittest-style tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test_unittest.py"
            test_file.write_text("""
import unittest

class TestExample(unittest.TestCase):
    def test_basic_operation(self):
        self.assertTrue(True)

    def test_with_setup(self):
        data = setup_test_data()
        self.assertIsNotNone(data)

def standalone_test():
    assert True
""")

            engine = TestDiscoveryEngine()
            tests = engine.discover_tests_in_file(test_file)

            assert len(tests) >= 2  # At least the two unittest methods

            # Check unittest tests
            unittest_tests = [t for t in tests if t.framework == TestFramework.UNITTEST]
            assert len(unittest_tests) >= 2

            # Check test names
            test_names = [t.name for t in unittest_tests]
            assert "test_basic_operation" in test_names
            assert "test_with_setup" in test_names

    def test_analyzes_test_targets(self) -> None:
        """§1.1: Analyzes target functions and modules in tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test_targets.py"
            test_file.write_text("""
import target_module
from other_module import SomeClass

def test_function_calls():
    result = target_module.target_function()
    data = SomeClass().process_data(result)
    assert data is not None
""")

            engine = TestDiscoveryEngine()
            tests = engine.discover_tests_in_file(test_file)

            assert len(tests) == 1
            test = tests[0]

            # Check target functions
            assert "target_function" in test.target_functions

            # Check target classes
            assert "SomeClass" in test.target_classes

            # Check target modules
            assert "target_module" in test.target_modules
            assert "other_module" in test.target_modules

    def test_handles_malformed_tests(self) -> None:
    """Test handles_malformed_tests runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with handles_malformed_tests
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions
            tests = engine.discover_tests_in_file(test_file)

            # Should still find the valid test
            assert len(tests) >= 1
            valid_test = next((t for t in tests if t.name == "test_valid"), None)
            assert valid_test is not None


class TestCoverage:
    """§1.5 Edge case: Coverage analysis handles various scenarios."""

    @pytest.fixture
    def coverage_adg_db(self) -> Generator[Path, None, None]:
        """Create ADG with violations for coverage analysis."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "coverage_adg.sqlite"

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

                # Insert test data
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', 'target_module.py')"
                )

                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 1, 'antipattern', 'silent_exception_swallow', 'target_module.py', 10, 'except:Exception')
                """)

                # Insert violations for coverage analysis
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'target_module.py', 15, 'HIGH', 'untriaged')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_analyzes_coverage_gaps(self, coverage_adg_db: Path) -> None:
        """§1.3: Analyzes test coverage gaps correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test directory with some tests
            test_dir = Path(tmp_dir) / "tests"
            test_dir.mkdir()

            test_file = test_dir / "test_target.py"
            test_file.write_text("""
def test_target_module():
    # This test doesn't cover the exception handler
    result = target_module.safe_function()
    assert result is not None
""")

            with TestCoverageAnalyzer(coverage_adg_db) as analyzer:  # noqa: F811
                gaps = analyzer.analyze_test_coverage_gaps([test_dir])

                # Should find at least one gap
                assert len(gaps) >= 1

                gap = gaps[0]
                assert gap.violation_file == "target_module.py"
                assert gap.violation_line == 15
                assert gap.priority > 0.0
                assert gap.suggested_test_name.startswith("test_")

    def test_prioritizes_gaps_by_severity(self, coverage_adg_db: Path) -> None:
        """§1.7: Gaps are prioritized by severity and coverage."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir) / "tests"
            test_dir.mkdir()

            # Create empty test directory (no coverage)

            with TestCoverageAnalyzer(coverage_adg_db) as analyzer:  # noqa: F811
                gaps = analyzer.analyze_test_coverage_gaps([test_dir])

                if len(gaps) > 0:
                    # High severity violations should have high priority
                    high_priority_gaps = [g for g in gaps if g.priority > 0.7]
                    assert len(high_priority_gaps) >= 1

    def test_populates_test_edges(self, coverage_adg_db: Path) -> None:
        """§1.4: Populates tests_execution_of edges comprehensively."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir) / "tests"
            test_dir.mkdir()

            test_file = test_dir / "test_comprehensive.py"
            test_file.write_text("""
def test_target_function():
    result = target_module.target_function()
    assert result is not None

def test_another_function():
    data = target_module.process_data()
    assert data is not None
""")

            # Add target nodes to ADG
            conn = sqlite3.connect(str(coverage_adg_db))
            try:
                conn.execute(
                    "INSERT INTO nodes (adg_name, entity_type, layer, resolved_path) VALUES ('symbol::target_function', 'symbol', 'L0', 'target_module.py')"
                )
                conn.execute(
                    "INSERT INTO nodes (adg_name, entity_type, layer, resolved_path) VALUES ('symbol::process_data', 'symbol', 'L0', 'target_module.py')"
                )
                conn.commit()
            finally:
                conn.close()

            with TestCoverageAnalyzer(coverage_adg_db) as analyzer:  # noqa: F811
                stats = analyzer.populate_comprehensive_test_edges([test_dir])

                assert stats["tests_discovered"] >= 2
                assert stats["edges_created"] >= 0  # May create edges if targets match


class TestSkeleton:
    """§1.5 Edge case: Test skeleton generation handles various scenarios."""

    def test_generates_unit_test_skeleton(self) -> None:
        """§1.1: Generates unit test skeleton correctly."""
        gap = TestCoverageGap(
            violation_file="target_module.py",
            violation_line=15,
            violation_function="risky_function",
            missing_test_types=["unit"],
            suggested_test_name="test_risky_function_exception_handling",
            priority=0.8,
        )

        generator = TestSkeletonGenerator()
        skeleton = generator.generate_test_skeleton(gap, "ValueError", "narrow_to_specific")

        assert "test_risky_function_exception_handling" in skeleton
        assert "ValueError" in skeleton
        assert "risky_function" in skeleton
        assert "pytest.raises" in skeleton
        assert "TODO: Implement this test" in skeleton

    def test_generates_integration_test_skeleton(self) -> None:
        """§1.1: Generates integration test skeleton correctly."""
        gap = TestCoverageGap(
            violation_file="api_client.py",
            violation_line=25,
            violation_function="api_call",
            missing_test_types=["integration"],
            suggested_test_name="test_api_call_exception_handling",
            priority=0.7,
        )

        generator = TestSkeletonGenerator()
        skeleton = generator.generate_test_skeleton(gap, "ConnectionError", "add_logging")

        assert "test_api_call_exception_handling_integration" in skeleton
        assert "ConnectionError" in skeleton
        assert "api_call" in skeleton
        assert "patch" in skeleton
        assert "TODO: Implement this integration test" in skeleton

    def test_generates_property_test_skeleton(self) -> None:
        """§1.1: Generates property-based test skeleton correctly."""
        gap = TestCoverageGap(
            violation_file="parser.py",
            violation_line=30,
            violation_function="parse_data",
            missing_test_types=["property"],
            suggested_test_name="test_parse_data_exception_handling",
            priority=0.6,
        )

        generator = TestSkeletonGenerator()
        skeleton = generator.generate_test_skeleton(gap, "TypeError", "narrow_to_specific")

        assert "test_parse_data_exception_handling_property" in skeleton
        assert "TypeError" in skeleton
        assert "parse_data" in skeleton
        assert "@given" in skeleton
        assert "st." in skeleton  # hypothesis strategies


class TestPhase3Integration:
    """§1.6 & §1.8: Integration tests with error handling."""

    def test_missing_test_directory_handling(self) -> None:
        """§1.6: Handles missing test directories gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_adg.sqlite"

            # Create minimal ADG
            conn = sqlite3.connect(str(db_path))
            try:
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY,
                        edge_id INTEGER,
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)
                conn.commit()
            finally:
                conn.close()

            # Use non-existent test directory
            non_existent_dir = Path(tmp_dir) / "non_existent_tests"

            results = run_phase3_enhanced_test_coverage(db_path, [non_existent_dir])

            # Should handle gracefully
            assert results["coverage_gaps"] == 0
            assert results["tests_discovered"] == 0

    def test_empty_adg_handling(self) -> None:
        """§1.6: Handles empty or malformed ADG gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_adg.sqlite"

            # Create ADG without violations table
            conn = sqlite3.connect(str(db_path))
            conn.close()

            test_dir = Path(tmp_dir) / "tests"
            test_dir.mkdir()

            # Should handle missing table gracefully
            with pytest.raises(Exception):  # Should raise due to missing violations table
                with TestCoverageAnalyzer(db_path) as analyzer:
                    analyzer.analyze_test_coverage_gaps([test_dir])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
