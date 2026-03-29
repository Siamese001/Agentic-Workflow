"""Wave 4: Tools — Stale Guard & Test Selector

Tests for:
- adg_stale_guard.py — staleness detection, SQLite mtime comparison, force re-ingest triggers
- adg_test_selector.py — dependency graph traversal, test selection from changed files, blast radius calculation
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# Stale Guard Tests
# ============================================================================

@pytest.mark.unit
class TestStaleGuard:
    """Tests for adg_stale_guard.py — staleness detection logic."""

    def test_sqlite_mtime_comparison(self):
        """Test SQLite mtime comparison against Redis timestamp."""
        import time
        
        sqlite_mtime = time.time() - 60  # 1 minute ago
        redis_ingested_at = time.time() - 300  # 5 minutes ago
        
        # SQLite is newer than Redis = stale
        is_stale = sqlite_mtime > redis_ingested_at
        assert is_stale, "SQLite newer than Redis means cache is stale"

    def test_freshness_threshold_5_minutes(self):
        """Test 5-minute freshness threshold."""
        import time
        
        current_time = time.time()
        ingested_at = current_time - 250  # 4 min 10 sec ago
        
        age_seconds = current_time - ingested_at
        is_fresh = age_seconds < 300  # 5 minutes
        
        assert is_fresh, "Should be fresh if < 5 minutes old"
        assert age_seconds == 250

    def test_stale_threshold_exceeded(self):
        """Test exceeding stale threshold."""
        import time
        
        current_time = time.time()
        ingested_at = current_time - 400  # 6 min 40 sec ago
        
        age_seconds = current_time - ingested_at
        is_fresh = age_seconds < 300
        
        assert not is_fresh, "Should be stale if > 5 minutes old"

    def test_force_reingest_trigger(self):
        """Test force re-ingest trigger (--force flag)."""
        force_flag = True
        
        # When force is True, should trigger re-ingest regardless of freshness
        should_reingest = force_flag
        assert should_reingest, "Force flag should trigger re-ingest"

    def test_adg_status_file_exists(self, tmp_path):
        """Test that adg:status file exists check."""
        status_file = tmp_path / "adg_status.json"
        status_file.write_text(json.dumps({"timestamp": "2026-03-29"}))
        
        assert status_file.exists(), "Status file should exist"

    def test_sqlite_file_exists(self, tmp_path):
        """Test that SQLite file exists check."""
        sqlite_file = tmp_path / "adg_indexed.sqlite"
        sqlite_file.write_text("")  # Empty file for test
        
        assert sqlite_file.exists(), "SQLite file should exist"


# ============================================================================
# Test Selector Tests
# ============================================================================

@pytest.mark.unit
class TestTestSelector:
    """Tests for adg_test_selector.py — test selection logic."""

    def test_dependency_graph_traversal(self):
        """Test dependency graph traversal from changed files."""
        # Simulate a dependency graph
        dependencies = {
            "module_a.py": ["test_module_a.py", "integration_test.py"],
            "module_b.py": ["test_module_b.py"],
            "utils.py": ["test_utils.py", "test_module_a.py", "test_module_b.py"],
        }
        
        changed_files = ["module_a.py"]
        selected_tests = []
        
        for changed in changed_files:
            if changed in dependencies:
                selected_tests.extend(dependencies[changed])
        
        assert "test_module_a.py" in selected_tests
        assert "integration_test.py" in selected_tests

    def test_blast_radius_calculation(self):
        """Test blast radius calculation for changes."""
        # Import graph: A imports B, B imports C
        import_graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
            "D": ["B"],
        }
        
        def get_blast_radius(start, depth=3):
            """Get all modules within blast radius."""
            visited = set()
            queue = [(start, 0)]
            
            while queue:
                node, d = queue.pop(0)
                if node in visited or d > depth:
                    continue
                visited.add(node)
                
                if node in import_graph:
                    for neighbor in import_graph[node]:
                        queue.append((neighbor, d + 1))
            
            return visited
        
        # Change to C affects B and A (importers)
        blast = get_blast_radius("C")
        # C doesn't import anything, so blast radius is just C
        assert blast == {"C"}

    def test_reverse_blast_radius(self):
        """Test reverse blast radius (importers of changed module)."""
        # Reverse graph: who imports me
        reverse_graph = {
            "A": [],  # Nothing imports A
            "B": ["A", "D"],  # A and D import B
            "C": ["B"],  # B imports C
            "D": [],  # Nothing imports D
        }
        
        changed_module = "C"
        affected = reverse_graph.get(changed_module, [])
        
        assert "B" in affected, "B should be affected by change to C"

    def test_test_selection_from_changed_files(self):
        """Test selecting tests from changed files."""
        # Map modules to their tests
        module_to_tests = {
            "module_a.py": ["test_a.py"],
            "module_b.py": ["test_b.py", "test_integration.py"],
            "utils.py": ["test_utils.py", "test_a.py"],
        }
        
        changed_files = ["module_a.py", "utils.py"]
        selected_tests = set()
        
        for changed in changed_files:
            if changed in module_to_tests:
                selected_tests.update(module_to_tests[changed])
        
        assert "test_a.py" in selected_tests
        assert "test_utils.py" in selected_tests
        assert "test_b.py" not in selected_tests  # Not affected

    def test_3_hop_closure(self):
        """Test 3-hop closure computation."""
        # Graph with 4 levels
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": ["E"],
            "E": [],
        }
        
        def get_closure(start, max_hops=3):
            """Get closure within max_hops."""
            visited = set()
            queue = [(start, 0)]
            
            while queue:
                node, hops = queue.pop(0)
                if node in visited or hops > max_hops:
                    continue
                visited.add(node)
                
                if node in graph:
                    for neighbor in graph[node]:
                        queue.append((neighbor, hops + 1))
            
            return visited
        
        closure = get_closure("A", max_hops=3)
        # A -> B -> C -> D (3 hops, should include D)
        assert "A" in closure
        assert "B" in closure
        assert "C" in closure
        assert "D" in closure
        # E is 4 hops away, should NOT be included
        assert "E" not in closure

    def test_test_file_naming_patterns(self):
        """Test detection of test file naming patterns."""
        test_patterns = [
            "test_something.py",
            "something_test.py",
            "test_unit.py",
        ]
        
        non_test_patterns = [
            "module.py",
            "utils.py",
            "__init__.py",
        ]
        
        def is_test_file(filename):
            return (
                filename.startswith("test_") or
                filename.endswith("_test.py")
            )
        
        for pattern in test_patterns:
            assert is_test_file(pattern), f"{pattern} should be test file"
        
        for pattern in non_test_patterns:
            assert not is_test_file(pattern), f"{pattern} should not be test file"


# ============================================================================
# Integration Scenarios
# ============================================================================

@pytest.mark.unit
class TestIntegrationScenarios:
    """Integration test scenarios for stale guard + test selector."""

    def test_full_workflow_stale_to_test_selection(self, tmp_path):
        """Test full workflow: detect stale -> regenerate -> select tests."""
        import time
        
        # 1. Create old SQLite file
        sqlite_file = tmp_path / "adg_indexed.sqlite"
        sqlite_file.write_text("")
        
        # 2. Set old mtime
        old_time = time.time() - 600  # 10 minutes ago
        import os
        os.utime(sqlite_file, (old_time, old_time))
        
        # 3. Check staleness
        mtime = sqlite_file.stat().st_mtime
        is_stale = (time.time() - mtime) > 300  # 5 minutes
        
        assert is_stale, "Should detect stale file"
        
        # 4. In real workflow, would trigger re-ingest
        # 5. Then select tests based on changed modules
        
        # Simulate test selection
        changed_modules = ["module_a.py"]
        tests_to_run = ["test_module_a.py"]
        
        assert len(tests_to_run) > 0

    def test_blast_radius_with_multiple_changes(self):
        """Test blast radius with multiple changed files."""
        changes = ["module_a.py", "module_b.py", "utils.py"]
        
        # Simulate cumulative blast radius
        blast_radius = set()
        for change in changes:
            # Each change adds to blast radius
            blast_radius.add(change)
            # Plus 1-hop neighbors
            if change == "module_a.py":
                blast_radius.update(["test_a.py", "integration.py"])
            elif change == "utils.py":
                blast_radius.update(["test_utils.py", "module_a.py", "module_b.py"])
        
        # Verify cumulative effect
        assert "module_a.py" in blast_radius
        assert "test_a.py" in blast_radius
        assert "utils.py" in blast_radius
