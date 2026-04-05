"""Integration tests for infrastructure monitoring CLI tools.

Tests adg_health, adg_violations, and adg_drift CLI tools.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from infrastructure.utils.adg_drift import compute_drift, format_json, format_table, load_snapshot
from infrastructure.utils.adg_health import (
    find_latest_adg,
    parse_adg_timestamp,
    query_health_metrics,
)
from infrastructure.utils.adg_health import (
    format_json as health_format_json,
)
from infrastructure.utils.adg_health import (
    format_markdown as health_format_markdown,
)
from infrastructure.utils.adg_health import (
    format_table as health_format_table,
)
from infrastructure.utils.adg_violations import (
    analyze_violations,
    format_csv,
    query_violations,
)


class TestAdgHealth:
    """Tests for adg_health CLI tool."""

    def test_parse_adg_timestamp_valid(self):
        """Test timestamp parsing from valid ADG filename."""
        path = Path("adg_indexed_04032026_2045.sqlite")
        result = parse_adg_timestamp(path)
        assert result == "2026-04-03 20:45"

    def test_parse_adg_timestamp_invalid(self):
        """Test timestamp parsing from invalid filename."""
        path = Path("some_other_file.sqlite")
        result = parse_adg_timestamp(path)
        assert result == "unknown"

    def test_parse_adg_timestamp_edge_cases(self):
        """Test timestamp parsing edge cases."""
        # Empty string
        result = parse_adg_timestamp(Path(""))
        assert result == "unknown"

        # Missing time component defaults to 00:00
        result = parse_adg_timestamp(Path("adg_indexed_04032026.sqlite"))
        assert result == "2026-04-03 00:00"  # Time defaults to 0000

        # Invalid date format
        result = parse_adg_timestamp(Path("adg_indexed_2026_0403_2045.sqlite"))
        assert result == "unknown"

        # None-like (should not crash)
        result = parse_adg_timestamp(Path(".sqlite"))
        assert result == "unknown"

    def test_find_latest_adg_no_adg_dir(self, tmp_path):
        """Test finding ADG when directory doesn't exist."""
        result = find_latest_adg(tmp_path)
        assert result is None

    def test_query_health_metrics(self):
        """Test querying health metrics from ADG."""
        # Create a mock ADG SQLite database
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = Path(f.name)

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Create tables
            cursor.execute(
                """CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY,
                    resolved_path TEXT,
                    entity_type TEXT,
                    layer TEXT
                )"""
            )
            cursor.execute(
                """CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id INTEGER,
                    relation_type TEXT,
                    symbol TEXT
                )"""
            )

            # Insert test data
            cursor.executemany(
                "INSERT INTO nodes (resolved_path, entity_type, layer) VALUES (?, ?, ?)",
                [
                    ("module1.py", "module", "L0"),
                    ("module2.py", "module", "L1"),
                    ("symbol1", "symbol", "L0"),
                    ("symbol2", "symbol", "L1"),
                ],
            )
            cursor.executemany(
                "INSERT INTO edges (src_id, relation_type, symbol) VALUES (?, ?, ?)",
                [
                    (1, "violates", "L0->L1"),
                    (2, "imports", "L1->L0"),
                ],
            )
            conn.commit()
            conn.close()

            # Query metrics
            conn = sqlite3.connect(str(db_path))
            metrics = query_health_metrics(conn, db_path)
            conn.close()

            assert metrics.total_nodes == 4
            assert metrics.total_edges == 2
            assert metrics.module_count == 2  # Only modules, not symbols
            assert metrics.symbol_count == 2
            assert metrics.violation_count == 1
            # Layer distribution only counts modules (entity_type='module')
            assert metrics.layer_distribution["L0"] == 1  # Only module1.py, not symbol1
            assert metrics.layer_distribution["L1"] == 1  # Only module2.py, not symbol2

        except sqlite3.OperationalError as e:
            pytest.fail(f"SQLite operational error: {e}")
        finally:
            db_path.unlink(missing_ok=True)

    def test_query_health_metrics_missing_tables(self):
        """Test error handling when ADG tables don't exist."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = Path(f.name)

        try:
            # Create empty DB without tables
            conn = sqlite3.connect(str(db_path))
            conn.close()

            # Should raise OperationalError when querying non-existent tables
            conn = sqlite3.connect(str(db_path))
            with pytest.raises(sqlite3.OperationalError):
                query_health_metrics(conn, db_path)
            conn.close()

        finally:
            db_path.unlink(missing_ok=True)

    def test_format_table(self):
        """Test table formatting."""
        from infrastructure.utils.adg_health import HealthMetrics

        metrics = HealthMetrics(
            adg_path="/test/adg.sqlite",
            timestamp="2026-04-04 06:14",
            total_nodes=100,
            total_edges=200,
            module_count=50,
            symbol_count=50,
            layer_distribution={"L0": 30, "L1": 20},
            violation_count=5,
            violation_by_type={"L0->L1": 3, "L1->L2": 2},
        )

        result = health_format_table(metrics)
        assert "ADG HEALTH REPORT" in result
        assert "100" in result
        assert "200" in result
        assert "L0" in result
        assert "L0->L1" in result

    def test_format_json(self):
        """Test JSON formatting."""
        from infrastructure.utils.adg_health import HealthMetrics

        metrics = HealthMetrics(
            adg_path="/test/adg.sqlite",
            timestamp="2026-04-04 06:14",
            total_nodes=100,
            total_edges=200,
            module_count=50,
            symbol_count=50,
            layer_distribution={"L0": 30},
            violation_count=5,
            violation_by_type={"L0->L1": 3},
        )

        result = health_format_json(metrics)
        data = json.loads(result)
        assert data["total_nodes"] == 100
        assert data["layer_distribution"]["L0"] == 30

    def test_format_markdown(self):
        """Test Markdown formatting."""
        from infrastructure.utils.adg_health import HealthMetrics

        metrics = HealthMetrics(
            adg_path="/test/adg.sqlite",
            timestamp="2026-04-04 06:14",
            total_nodes=100,
            total_edges=200,
            module_count=50,
            symbol_count=50,
            layer_distribution={"L0": 30},
            violation_count=5,
            violation_by_type={},
        )

        result = health_format_markdown(metrics)
        assert "# ADG Health Report" in result
        assert "| Metric | Count |" in result


class TestAdgViolations:
    """Tests for adg_violations CLI tool."""

    def test_query_violations_basic(self):
        """Test basic violation querying."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = Path(f.name)

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Create tables
            cursor.execute(
                """CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY,
                    resolved_path TEXT,
                    entity_type TEXT,
                    layer TEXT
                )"""
            )
            cursor.execute(
                """CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id INTEGER,
                    relation_type TEXT,
                    symbol TEXT,
                    line_no INTEGER
                )"""
            )

            # Insert test data
            cursor.executemany(
                "INSERT INTO nodes (resolved_path, entity_type, layer) VALUES (?, ?, ?)",
                [
                    ("agentic_core/L0/file.py", "module", "L0"),
                    ("tools/util.py", "module", "L_TOOLS"),
                ],
            )
            cursor.executemany(
                "INSERT INTO edges (src_id, relation_type, symbol, line_no) VALUES (?, ?, ?, ?)",
                [
                    (1, "violates", "L0->L4", 42),
                    (2, "violates", "L_TOOLS->L_APP", 10),
                    (1, "imports", "L0->L1", 5),  # Not a violation
                ],
            )
            conn.commit()

            # Query all violations
            violations = query_violations(conn)
            assert len(violations) == 2

            # Query filtered by layer
            violations = query_violations(conn, layers=["L0"])
            assert len(violations) == 1
            assert violations[0].symbol == "L0->L4"

            # Query filtered by file
            violations = query_violations(conn, file_pattern="tools/*")
            assert len(violations) == 1
            assert violations[0].source_file == "tools/util.py"

            conn.close()

        finally:
            db_path.unlink(missing_ok=True)

    def test_analyze_violations(self):
        """Test violation analysis."""
        from infrastructure.utils.adg_violations import Violation

        violations = [
            Violation(id=1, source_file="file1.py", relation_type="violates", symbol="L0->L4", line_no=10),
            Violation(id=2, source_file="file1.py", relation_type="violates", symbol="L0->L4", line_no=20),
            Violation(id=3, source_file="file2.py", relation_type="violates", symbol="L1->L5", line_no=5),
        ]

        report = analyze_violations(violations)
        assert report.total_violations == 3
        assert report.by_type["L0->L4"] == 2
        assert report.by_type["L1->L5"] == 1
        assert report.by_file["file1.py"] == 2
        assert report.by_file["file2.py"] == 1

    def test_format_csv(self):
        """Test CSV formatting with file output."""
        import tempfile

        from infrastructure.utils.adg_violations import Violation, ViolationReport

        report = ViolationReport(
            adg_path="/test/adg.sqlite",
            timestamp="2026-04-04 06:14",
            total_violations=2,
            violations=[
                Violation(
                    id=1,
                    source_file="file1.py",
                    relation_type="violates",
                    symbol="L0->L4",
                    line_no=10,
                    layer_from="L0",
                    layer_to="L4",
                ),
                Violation(
                    id=2,
                    source_file="file2.py",
                    relation_type="violates",
                    symbol="L1->L5",
                    line_no=20,
                    layer_from="L1",
                    layer_to="L5",
                ),
            ],
            by_type={"L0->L4": 1, "L1->L5": 1},
            by_layer={"L0": 1, "L1": 1},
            by_file={"file1.py": 1, "file2.py": 1},
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = Path(f.name)

        try:
            # Test file write
            result = format_csv(report, output_path=output_path)
            assert result == ""  # Should return empty string when writing to file
            assert output_path.exists()

            # Verify file contents
            content = output_path.read_text()
            assert "id,source_file,line_no,violation_type,layer_from,layer_to" in content
            assert "file1.py" in content
            assert "L0->L4" in content

        finally:
            output_path.unlink(missing_ok=True)

    def test_format_csv_string(self):
        """Test CSV formatting returning string."""
        from infrastructure.utils.adg_violations import Violation, ViolationReport

        report = ViolationReport(
            adg_path="/test/adg.sqlite",
            timestamp="2026-04-04 06:14",
            total_violations=1,
            violations=[
                Violation(
                    id=1,
                    source_file="file.py",
                    relation_type="violates",
                    symbol="L0->L4",
                    line_no=42,
                    layer_from="L0",
                    layer_to="L4",
                ),
            ],
            by_type={"L0->L4": 1},
            by_layer={"L0": 1},
            by_file={"file.py": 1},
        )

        result = format_csv(report, output_path=None)
        assert "id,source_file,line_no,violation_type,layer_from,layer_to" in result
        assert "file.py" in result
        assert "L0->L4" in result


class TestAdgDrift:
    """Tests for adg_drift CLI tool."""

    def test_load_snapshot(self):
        """Test loading ADG snapshot."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = Path(f.name)

        conn = None
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Create tables with full schema (including line_no)
            cursor.execute(
                """CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY,
                    resolved_path TEXT,
                    entity_type TEXT,
                    layer TEXT
                )"""
            )
            cursor.execute(
                """CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id INTEGER,
                    relation_type TEXT,
                    symbol TEXT,
                    line_no INTEGER
                )"""
            )

            # Insert test data
            cursor.executemany(
                "INSERT INTO nodes (resolved_path, entity_type, layer) VALUES (?, ?, ?)",
                [
                    ("module1.py", "module", "L0"),
                    ("module2.py", "module", "L1"),
                ],
            )
            cursor.execute(
                "INSERT INTO edges (src_id, relation_type, symbol, line_no) VALUES (?, ?, ?, ?)",
                (1, "violates", "L0->L1", 42),
            )
            conn.commit()
            conn.close()
            conn = None  # Mark as closed

            snapshot = load_snapshot(db_path)
            assert len(snapshot.nodes) == 2
            assert "module1.py" in snapshot.nodes
            assert "module2.py" in snapshot.nodes
            assert len(snapshot.violations) == 1

        finally:
            if conn:
                conn.close()
            db_path.unlink(missing_ok=True)

    def test_compute_drift(self):
        """Test drift computation."""
        from infrastructure.utils.adg_drift import Snapshot

        baseline = Snapshot(
            path=Path("baseline.sqlite"),
            timestamp="2026-04-03",
            nodes={
                "mod1.py": {"path": "mod1.py", "layer": "L0"},
                "mod2.py": {"path": "mod2.py", "layer": "L1"},
            },
            violations=[{"id": 1}],
        )

        current = Snapshot(
            path=Path("current.sqlite"),
            timestamp="2026-04-04",
            nodes={
                "mod1.py": {"path": "mod1.py", "layer": "L0"},
                "mod3.py": {"path": "mod3.py", "layer": "L2"},
            },
            violations=[{"id": 1}, {"id": 2}],
        )

        drift = compute_drift(baseline, current)
        assert "mod3.py" in drift.added_modules
        assert "mod2.py" in drift.deleted_modules
        assert drift.violation_delta == 1
        assert drift.modules_by_layer_delta["L2"] == 1
        assert drift.modules_by_layer_delta["L1"] == -1

    def test_format_table(self):
        """Test table formatting for drift."""
        from infrastructure.utils.adg_drift import DriftReport, Snapshot

        baseline = Snapshot(path=Path("b.sqlite"), timestamp="2026-04-03", nodes={}, violations=[])
        current = Snapshot(path=Path("c.sqlite"), timestamp="2026-04-04", nodes={}, violations=[])

        report = DriftReport(
            baseline=baseline,
            current=current,
            added_modules=["new1.py", "new2.py"],
            deleted_modules=["old1.py"],
            violation_delta=2,
            modules_by_layer_delta={"L0": 1, "L1": -1},
        )

        result = format_table(report, show_modules=True)
        assert "ADG DRIFT REPORT" in result
        assert "new1.py" in result
        assert "old1.py" in result
        assert "+2" in result or "Violation Delta: 2" in result

    def test_format_json(self):
        """Test JSON formatting for drift."""
        from infrastructure.utils.adg_drift import DriftReport, Snapshot

        baseline = Snapshot(path=Path("b.sqlite"), timestamp="2026-04-03", nodes={}, violations=[])
        current = Snapshot(path=Path("c.sqlite"), timestamp="2026-04-04", nodes={}, violations=[])

        report = DriftReport(
            baseline=baseline,
            current=current,
            added_modules=["new.py"],
            deleted_modules=[],
            violation_delta=0,
            modules_by_layer_delta={},
        )

        result = format_json(report)
        data = json.loads(result)
        assert data["drift"]["added_modules"] == ["new.py"]
        assert data["baseline"]["module_count"] == 0


class TestCliIntegration:
    """Integration tests for CLI entry points."""

    def test_health_self_test(self, caplog):
        """Test health monitor self-test."""
        import logging

        from infrastructure.utils.adg_health import self_test

        with caplog.at_level(logging.INFO):
            result = self_test()

        # Verify return type
        assert isinstance(result, bool)
        # Verify actual functionality - should find ADG or log appropriate message
        assert result is True  # self_test should return True even if no ADG
        # Verify expected log messages
        assert "Running self-test" in caplog.text
        assert "Self-test complete" in caplog.text

    def test_violations_self_test(self, caplog):
        """Test violations tracker self-test."""
        import logging

        from infrastructure.utils.adg_violations import self_test

        with caplog.at_level(logging.INFO):
            result = self_test()

        assert isinstance(result, bool)
        assert result is True
        assert "Running self-test" in caplog.text
        assert "Self-test complete" in caplog.text

    def test_drift_self_test(self, caplog):
        """Test drift detector self-test."""
        import logging

        from infrastructure.utils.adg_drift import self_test

        with caplog.at_level(logging.INFO):
            result = self_test()

        assert isinstance(result, bool)
        assert result is True
        assert "Running self-test" in caplog.text
        assert "Self-test complete" in caplog.text
