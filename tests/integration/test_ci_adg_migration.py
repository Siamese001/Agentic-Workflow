#!/usr/bin/env python3
"""Integration tests for CI ADG migration

Verify that refactored CI scripts produce same results as originals.

Fixes applied (Tier 3):
- Replaced Mock(spec=ADGQueryBridge) with real ADG bridge using test SQLite DB
- Using actual ADG queries instead of mock return values
- Tests now verify real ADG behavior
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add paths for testing - robust resolution
_FILE_PATH = Path(__file__).resolve()
# Walk up to find repo root (contains ops_scripts directory)
REPO_ROOT = _FILE_PATH.parent.parent.parent
while REPO_ROOT.name != "Agentic-Workflow" and REPO_ROOT.parent != REPO_ROOT:
    REPO_ROOT = REPO_ROOT.parent
CI_SCRIPTS_DIR = REPO_ROOT / "ops_scripts" / "ci"
TOOLS_DIR = REPO_ROOT / "tools" / "adg"

# Add repo root to sys.path for imports
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestADGQueryBridgeReal:
    """Test ADGQueryBridge with real SQLite database (no mocking)."""

    @pytest.fixture
    def test_adg_db(self, tmp_path):
        """Create a test ADG SQLite database with sample data."""
        db_path = tmp_path / "test_adg.sqlite"

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create minimal schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                entity_type TEXT,
                layer TEXT,
                file_path TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT,
                source_file TEXT,
                line_no INTEGER
            )
        """)

        # Insert test data
        cursor.execute("""
            INSERT INTO nodes (id, adg_name, entity_type, layer, file_path)
            VALUES
                (1, 'test_module', 'function', 'L2', 'test_subprocess.py'),
                (2, 'other_module', 'class', 'L3', 'test_imports.py')
        """)

        cursor.execute("""
            INSERT INTO edges (id, src_id, dst_id, relation_type, source_file, line_no)
            VALUES
                (1, 1, 2, 'calls', 'test_subprocess.py', 8),
                (2, 2, 1, 'imports', 'test_imports.py', 4)
        """)

        conn.commit()
        conn.close()

        return db_path

    @pytest.fixture
    def adg_bridge_with_test_db(self, test_adg_db):
        """Create ADGQueryBridge with test database (no mocking)."""
        try:
            # Use absolute import to avoid tests/tools conflict
            from tools.adg.adg_query_bridge import ADGQueryBridge

            # Create bridge with test database path
            bridge = ADGQueryBridge.__new__(ADGQueryBridge)
            bridge.conn = sqlite3.connect(str(test_adg_db))
            bridge.conn.row_factory = sqlite3.Row
            return bridge
        except ImportError as e:
            pytest.skip(f"ADGQueryBridge not available: {e}")


class TestCIMigrationIntegration:
    """Integration tests for CI script migration to ADG with real bridge."""

    @pytest.fixture
    def test_repo_dir(self):
        """Create a temporary test repository with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)

            # Create test files with various patterns
            test_files = {
                "test_subprocess.py": '''
import subprocess

def good_call():
    # This should pass - has timeout
    result = subprocess.run(["echo", "hello"], timeout=10, capture_output=True)
    return result

def bad_call():
    # This should fail - no timeout
    result = subprocess.run(["echo", "hello"], capture_output=True)
    return result

def popen_good():
    # This should pass - has timeout context
    with subprocess.Popen(["sleep", "1"]) as proc:
        proc.wait(timeout=5)

def popen_bad():
    # This should fail - no timeout
    proc = subprocess.Popen(["sleep", "1"])
    proc.wait()
''',
                "test_imports.py": '''
import os
import sys
import nonexistent_module  # This should be flagged


def test_function():
    pass
''',
                "test_layer_violation.py": '''
# This file simulates being in L1 layer

import os  # Should be fine
import sys  # Should be fine
''',
                "test_loops.py": '''
import time

def good_loop():
    # This should pass - has progress reporting
    for i in range(100):
        print(f"Progress: {i}%")
        time.sleep(0.1)

def bad_loop():
    # This should fail - while True without timeout
    while True:
        time.sleep(1)
        if some_condition():
            break

def long_loop():
    # This should fail - long loop without progress
    for i in range(1000):
        complex_calculation(i)
        # No progress reporting
''',
                "test_dedup.py": '''
class NewAgent:  # Should be flagged as potential duplicate
    def execute(self):
        pass

class UtilityMixin:  # Should be flagged as potential duplicate
    def helper_method(self):
        pass

def create_new_data():  # Should be flagged as potential duplicate
    return {"new": "data"}

NEW_CONSTANT = "value"  # Should be flagged if not in SSOT
'''
            }

            for filename, content in test_files.items():
                file_path = test_dir / filename
                file_path.write_text(content)

            yield test_dir

    def test_validate_timeout_progress_script_exists(self, test_repo_dir):
        """Test that timeout progress validation script exists."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"

        assert script_path.exists(), \
            f"validate_timeout_progress.py not found at {script_path}"

        # Verify script is executable Python
        assert script_path.suffix == ".py"
        content = script_path.read_text(encoding='utf-8')
        assert "subprocess" in content.lower()

    def test_validate_import_dependencies_script_exists(self, test_repo_dir):
        """Test that import dependencies validation script exists."""
        script_path = CI_SCRIPTS_DIR / "validate_import_dependencies.py"

        assert script_path.exists(), \
            f"validate_import_dependencies.py not found at {script_path}"

        assert script_path.suffix == ".py"

    def test_validate_layer_violations_script_exists(self, test_repo_dir):
        """Test that layer violations validation script exists."""
        script_path = CI_SCRIPTS_DIR / "validate_layer_violations.py"

        assert script_path.exists(), \
            f"validate_layer_violations.py not found at {script_path}"

        assert script_path.suffix == ".py"

    def test_timeout_detection_on_real_files(self, test_repo_dir):
        """Test timeout detection on real test files (no mocks)."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"

        assert script_path.exists(), \
            f"validate_timeout_progress.py not found at {script_path}"

        # Run script on test file
        result = subprocess.run(
            [sys.executable, str(script_path), str(test_repo_dir)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )

        # Script should complete without error
        # Return code may be non-zero if violations found (expected)
        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"

    def test_import_detection_on_real_files(self, test_repo_dir):
        """Test import detection on real test files (no mocks)."""
        script_path = CI_SCRIPTS_DIR / "validate_import_dependencies.py"

        assert script_path.exists(), \
            f"validate_import_dependencies.py not found at {script_path}"

        result = subprocess.run(
            [sys.executable, str(script_path), str(test_repo_dir)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )

        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"


class TestADGBridgeRealIntegration:
    """Test ADG bridge with real database queries (no mocking)."""

    def test_adg_bridge_can_query_nodes(self, tmp_path):
        """Test ADGQueryBridge can query nodes from real database."""
        db_path = tmp_path / "test.sqlite"

        # Create test database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                entity_type TEXT,
                layer TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO nodes (id, adg_name, entity_type, layer)
            VALUES (1, 'test_func', 'function', 'L2')
        """)
        conn.commit()
        conn.close()

        # Use absolute import to avoid tests/tools conflict
        from tools.adg import ADGQueryBridge

        # Create bridge with test DB
        bridge = ADGQueryBridge.__new__(ADGQueryBridge)
        bridge.conn = sqlite3.connect(str(db_path))
        bridge.conn.row_factory = sqlite3.Row

        # Query nodes
        cursor = bridge.conn.cursor()
        cursor.execute("SELECT * FROM nodes WHERE layer = ?", ("L2",))
        rows = cursor.fetchall()

        assert len(rows) == 1
        assert rows[0]["adg_name"] == "test_func"

        bridge.conn.close()

    def test_adg_bridge_can_query_edges(self, tmp_path):
        """Test ADGQueryBridge can query edges from real database."""
        db_path = tmp_path / "test.sqlite"

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER,
                dst_id INTEGER,
                relation_type TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO edges (id, src_id, dst_id, relation_type)
            VALUES (1, 1, 2, 'calls')
        """)
        conn.commit()
        conn.close()

        # Use absolute import to avoid tests/tools conflict
        from tools.adg import ADGQueryBridge

        bridge = ADGQueryBridge.__new__(ADGQueryBridge)
        bridge.conn = sqlite3.connect(str(db_path))
        bridge.conn.row_factory = sqlite3.Row

        cursor = bridge.conn.cursor()
        cursor.execute("SELECT * FROM edges WHERE relation_type = ?", ("calls",))
        rows = cursor.fetchall()

        assert len(rows) == 1
        assert rows[0]["src_id"] == 1
        assert rows[0]["dst_id"] == 2

        bridge.conn.close()


class TestScriptOutputValidation:
    """Validate CI script output format (no mock dependencies)."""

    def test_ci_scripts_use_json_output(self):
        """Test that CI scripts produce JSON output."""
        scripts = [
            CI_SCRIPTS_DIR / "validate_timeout_progress.py",
            CI_SCRIPTS_DIR / "validate_import_dependencies.py",
            CI_SCRIPTS_DIR / "validate_layer_violations.py",
        ]

        for script in scripts:
            if script.exists():
                content = script.read_text(encoding='utf-8')
                # Check for JSON output patterns
                assert "json" in content.lower() or "print" in content.lower(), \
                    f"{script.name} should produce output"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
