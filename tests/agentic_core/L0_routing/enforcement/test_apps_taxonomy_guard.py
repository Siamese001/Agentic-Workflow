"""Tests for apps_taxonomy_guard.py module."""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.apps_taxonomy_guard import AppsTaxonomyGuard


class TestAppsTaxonomyGuard:
    """Tests for AppsTaxonomyGuard class."""

    def test_allowed_imports_constant(self):
        """Test that ALLOWED_IMPORTS constant exists and has expected values."""
        assert isinstance(AppsTaxonomyGuard.ALLOWED_IMPORTS, set)
        assert "agentic_core.interfaces" in AppsTaxonomyGuard.ALLOWED_IMPORTS
        assert "agentic_core.prompt_governance.contracts" in AppsTaxonomyGuard.ALLOWED_IMPORTS

    def test_is_allowed_import_exact_match(self):
        """Test that exact allowed imports return True."""
        guard = AppsTaxonomyGuard()
        assert guard._is_allowed_import("agentic_core.interfaces")
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts")

    def test_is_allowed_import_submodule(self):
        """Test that submodules of allowed imports return True."""
        guard = AppsTaxonomyGuard()
        assert guard._is_allowed_import("agentic_core.interfaces.some_module")
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts.some_submodule")

    def test_is_allowed_import_prohibited(self):
        """Test that prohibited imports return False."""
        guard = AppsTaxonomyGuard()
        assert not guard._is_allowed_import("agentic_core.L0_routing")
        assert not guard._is_allowed_import("agentic_core.L1_cognition")
        assert not guard._is_allowed_import("agentic_core.runtime")

    def test_is_allowed_import_partial_match(self):
        """Test that partial matches return False."""
        guard = AppsTaxonomyGuard()
        # Should not match just because it starts with similar prefix
        assert not guard._is_allowed_import("agentic_core_interfaces")  # Missing dot
        assert not guard._is_allowed_import("agentic_core.prompt_governance")  # Not full path


class TestCheckImportNode:
    """Tests for _check_import_node method."""

    def test_check_import_node_prohibited(self):
        """Test that prohibited import nodes are detected."""
        guard = AppsTaxonomyGuard()
        node = ast.Import(names=[ast.alias(name="agentic_core.L0_routing", asname=None)])
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        with patch.object(guard, "_is_allowed_import", return_value=False):
            violations = guard._check_import_node(node, file_path, repo_root)

        assert len(violations) == 1
        assert "apps_test/test.py" in violations[0]
        assert "import agentic_core.L0_routing" in violations[0]

    def test_check_import_node_allowed(self):
        """Test that allowed import nodes are not violations."""
        guard = AppsTaxonomyGuard()
        node = ast.Import(names=[ast.alias(name="agentic_core.interfaces", asname=None)])
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        with patch.object(guard, "_is_allowed_import", return_value=True):
            violations = guard._check_import_node(node, file_path, repo_root)

        assert len(violations) == 0

    def test_check_import_node_non_agentic_core(self):
        """Test that non-agentic_core imports are not violations."""
        guard = AppsTaxonomyGuard()
        node = ast.Import(names=[ast.alias(name="some_other_module", asname=None)])
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        violations = guard._check_import_node(node, file_path, repo_root)

        assert len(violations) == 0


class TestCheckImportFromNode:
    """Tests for _check_import_from_node method."""

    def test_check_import_from_node_prohibited(self):
        """Test that prohibited import-from nodes are detected."""
        guard = AppsTaxonomyGuard()
        node = ast.ImportFrom(
            module="agentic_core.L0_routing",
            names=[ast.alias(name="some_function", asname=None)],
            level=0,
        )
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        with patch.object(guard, "_is_allowed_import", return_value=False):
            violations = guard._check_import_from_node(node, file_path, repo_root)

        assert len(violations) == 1
        assert "apps_test/test.py" in violations[0]
        assert "from agentic_core.L0_routing import" in violations[0]

    def test_check_import_from_node_allowed(self):
        """Test that allowed import-from nodes are not violations."""
        guard = AppsTaxonomyGuard()
        node = ast.ImportFrom(
            module="agentic_core.interfaces",
            names=[ast.alias(name="some_protocol", asname=None)],
            level=0,
        )
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        with patch.object(guard, "_is_allowed_import", return_value=True):
            violations = guard._check_import_from_node(node, file_path, repo_root)

        assert len(violations) == 0

    def test_check_import_from_node_non_agentic_core(self):
        """Test that non-agentic_core imports are not violations."""
        guard = AppsTaxonomyGuard()
        node = ast.ImportFrom(
            module="some_other_module",
            names=[ast.alias(name="some_function", asname=None)],
            level=0,
        )
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        violations = guard._check_import_from_node(node, file_path, repo_root)

        assert len(violations) == 0

    def test_check_import_from_node_none_module(self):
        """Test that None module is handled gracefully."""
        guard = AppsTaxonomyGuard()
        node = ast.ImportFrom(
            module=None,
            names=[ast.alias(name="local_module", asname=None)],
            level=1,
        )
        file_path = Path("apps_test/test.py")
        repo_root = Path("/repo")

        violations = guard._check_import_from_node(node, file_path, repo_root)

        assert len(violations) == 0


class TestScanFile:
    """Tests for _scan_file method."""

    def test_scan_file_with_violations(self):
        """Test that file with violations is detected."""
        guard = AppsTaxonomyGuard()
        code = """
import agentic_core.L0_routing
from agentic_core.L1_cognition import something
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            file_path = Path(f.name)

        try:
            repo_root = Path("/repo")
            violations = guard._scan_file(file_path, repo_root)

            assert len(violations) == 2
            assert any("agentic_core.L0_routing" in v for v in violations)
            assert any("agentic_core.L1_cognition" in v for v in violations)
        finally:
            file_path.unlink()

    def test_scan_file_with_allowed_imports(self):
        """Test that file with allowed imports has no violations."""
        guard = AppsTaxonomyGuard()
        code = """
import agentic_core.interfaces
from agentic_core.prompt_governance.contracts import something
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            file_path = Path(f.name)

        try:
            repo_root = Path("/repo")
            violations = guard._scan_file(file_path, repo_root)

            assert len(violations) == 0
        finally:
            file_path.unlink()

    def test_scan_file_with_syntax_error(self):
        """Test that file with syntax error is handled gracefully."""
        guard = AppsTaxonomyGuard()
        code = """
import agentic_core.L0_routing
this is invalid syntax
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            file_path = Path(f.name)

        try:
            repo_root = Path("/repo")
            violations = guard._scan_file(file_path, repo_root)

            # Should return empty list on syntax error
            assert isinstance(violations, list)
        finally:
            file_path.unlink()

    def test_scan_file_with_no_violations(self):
        """Test that file without violations returns empty list."""
        guard = AppsTaxonomyGuard()
        code = """
import os
import sys
from typing import Optional
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            file_path = Path(f.name)

        try:
            repo_root = Path("/repo")
            violations = guard._scan_file(file_path, repo_root)

            assert len(violations) == 0
        finally:
            file_path.unlink()


class TestScanAppsDirectory:
    """Tests for _scan_apps_directory method."""

    def test_scan_apps_directory_with_violations(self):
        """Test scanning directory with violations."""
        guard = AppsTaxonomyGuard()
        code = """
import agentic_core.L0_routing
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            apps_dir = Path(tmpdir) / "apps_test"
            apps_dir.mkdir()
            test_file = apps_dir / "test.py"
            test_file.write_text(code)

            repo_root = Path(tmpdir)
            violations = guard._scan_apps_directory(apps_dir, repo_root)

            assert len(violations) == 1
            assert "agentic_core.L0_routing" in violations[0]

    def test_scan_apps_directory_no_violations(self):
        """Test scanning directory without violations."""
        guard = AppsTaxonomyGuard()
        code = """
import os
import sys
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            apps_dir = Path(tmpdir) / "apps_test"
            apps_dir.mkdir()
            test_file = apps_dir / "test.py"
            test_file.write_text(code)

            repo_root = Path(tmpdir)
            violations = guard._scan_apps_directory(apps_dir, repo_root)

            assert len(violations) == 0


class TestScan:
    """Tests for scan method."""

    def test_scan_with_mock_trace_emissions(self):
        """Test scan method with mocked trace emissions."""
        guard = AppsTaxonomyGuard()
        code = """
import agentic_core.L0_routing
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            apps_dir = Path(tmpdir) / "apps_test"
            apps_dir.mkdir()
            test_file = apps_dir / "test.py"
            test_file.write_text(code)

            with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard._emit_records_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_replay_key"):
                    with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_determinism_digest"):
                        violations = guard.scan(repo_root=tmpdir)

                        assert isinstance(violations, tuple)
                        assert len(violations) == 1

    def test_scan_no_apps_directories(self):
        """Test scan when no apps_* directories exist."""
        guard = AppsTaxonomyGuard()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard._emit_records_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_replay_key"):
                    with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_determinism_digest"):
                        violations = guard.scan(repo_root=tmpdir)

                        assert violations == ()

    def test_scan_returns_sorted_tuple(self):
        """Test that scan returns a sorted tuple of violations."""
        guard = AppsTaxonomyGuard()
        with tempfile.TemporaryDirectory() as tmpdir:
            apps_dir = Path(tmpdir) / "apps_test"
            apps_dir.mkdir()
            
            # Create multiple files with violations
            test1 = apps_dir / "z_test.py"
            test1.write_text("import agentic_core.L0_routing")
            
            test2 = apps_dir / "a_test.py"
            test2.write_text("import agentic_core.L1_cognition")

            with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard._emit_records_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_replay_key"):
                    with patch("agentic_core.L0_routing.enforcement.apps_taxonomy_guard.emit_determinism_digest"):
                        violations = guard.scan(repo_root=tmpdir)

                        assert isinstance(violations, tuple)
                        # Should be sorted alphabetically
                        assert violations[0] < violations[1]
