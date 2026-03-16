"""
Unit tests for L0 Routing Apps Taxonomy Guard - deterministic import-graph checks.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L0_routing.enforcement.apps_taxonomy_guard import AppsTaxonomyGuard
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_apps_taxonomy_guard")
_emit_applies_guardrail("p0", "test_apps_taxonomy_guard", "p0_governance")
_emit_reads_policy_state("p0", "test_apps_taxonomy_guard", "policy_binding")
_emit_snapshots_state("p0", "test_apps_taxonomy_guard", "state_snapshot")
emit_replay_key("p0", "test_apps_taxonomy_guard")
emit_determinism_digest("p0", "test_apps_taxonomy_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit
class TestAppsTaxonomyGuard:
    """Test AppsTaxonomyGuard AST-based import scanning."""

    def test_guard_initialization(self):
        """Test guard initializes with correct allowlist."""
        guard = AppsTaxonomyGuard()

        expected_allowed = {
            "agentic_core.interfaces",
            "agentic_core.prompt_governance.contracts",
        }
        assert guard.ALLOWED_IMPORTS == expected_allowed

    def test_scan_empty_repository(self):
        """Test scan on repository with no apps_* directories."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            violations = guard.scan(repo_root=temp_dir)

            assert violations == ()

    def test_scan_apps_directory_with_allowed_imports(self):
        """Test scan detects no violations for allowed imports."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory with allowed imports
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create Python file with allowed imports
            py_file = apps_dir / "main.py"
            py_file.write_text("""
# Allowed imports
from agentic_core.interfaces import SomeInterface
from agentic_core.prompt_governance.contracts import Contract
import agentic_core.interfaces.submodule
""")

            violations = guard.scan(repo_root=temp_dir)

            # Should have no violations
            assert violations == ()

    def test_scan_apps_directory_with_prohibited_imports(self):
        """Test scan detects violations for prohibited imports."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create Python file with prohibited imports
            py_file = apps_dir / "main.py"
            py_file.write_text("""
# Prohibited imports
from agentic_core.L0_routing import PathRouter
import agentic_core.L4_state
from agentic_core.L2_execution import CIDRegistry
""")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violations
            assert len(violations) == 3

            # Check specific violations (sorted)
            assert "apps_demo/main.py:3 from agentic_core.L0_routing import PathRouter" in violations
            assert "apps_demo/main.py:4 import agentic_core.L4_state" in violations
            assert "apps_demo/main.py:5 from agentic_core.L2_execution import CIDRegistry" in violations

    def test_scan_multiple_apps_directories(self):
        """Test scan handles multiple apps_* directories."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two apps directories
            apps1_dir = Path(temp_dir) / "apps_first"
            apps1_dir.mkdir()

            apps2_dir = Path(temp_dir) / "apps_second"
            apps2_dir.mkdir()

            # Create files with violations in both
            py_file1 = apps1_dir / "file1.py"
            py_file1.write_text("from agentic_core.L5_safety import RiskGate\n")

            py_file2 = apps2_dir / "file2.py"
            py_file2.write_text("import agentic_core.L6_observability\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violations from both directories
            assert len(violations) == 2

            # Violations should be sorted by path and content
            expected_violations = [
                "apps_first/file1.py:1 from agentic_core.L5_safety import RiskGate",
                "apps_second/file2.py:1 import agentic_core.L6_observability",
            ]
            assert violations == tuple(expected_violations)

    def test_scan_nested_python_files(self):
        """Test scan finds violations in nested Python files."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            nested_dir = apps_dir / "submodule"
            nested_dir.mkdir()

            # Create file in nested directory
            py_file = nested_dir / "deep.py"
            py_file.write_text("from agentic_core.L0_routing.meta_control import MetaLearningBus\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violation with correct path
            assert len(violations) == 1
            assert (
                "submodule/deep.py:1 from agentic_core.L0_routing.meta_control import MetaLearningBus"
                in violations[0]
            )

    def test_scan_ignores_non_python_files(self):
        """Test scan ignores non-Python files."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create non-Python files with agentic_core content
            txt_file = apps_dir / "config.txt"
            txt_file.write_text("import agentic_core.L0_routing\n")

            md_file = apps_dir / "readme.md"
            md_file.write_text("from agentic_core.L4_state import Something\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should have no violations (non-Python files ignored)
            assert violations == ()

    def test_scan_handles_syntax_errors_gracefully(self):
        """Test scan skips files with syntax errors."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create file with syntax error
            bad_file = apps_dir / "bad.py"
            bad_file.write_text("from agentic_core.L0_routing import  # incomplete\n")

            # Create valid file with violation
            good_file = apps_dir / "good.py"
            good_file.write_text("from agentic_core.L4_state import State\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should only detect violation from valid file
            assert len(violations) == 1
            assert "good.py:1 from agentic_core.L4_state import State" in violations[0]

    def test_deterministic_ordering_violations(self):
        """Test violations are returned in deterministic sorted order."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create multiple files with violations
            files_and_imports = [
                ("z_file.py", "import agentic_core.L4_state"),
                ("a_file.py", "from agentic_core.L0_routing import Path"),
                ("m_file.py", "import agentic_core.L2_execution"),
            ]

            for filename, import_stmt in files_and_imports:
                py_file = apps_dir / filename
                py_file.write_text(f"{import_stmt}\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should be sorted by filename and content
            expected_violations = [
                "apps_demo/a_file.py:1 from agentic_core.L0_routing import Path",
                "apps_demo/m_file.py:1 import agentic_core.L2_execution",
                "apps_demo/z_file.py:1 import agentic_core.L4_state",
            ]
            assert violations == tuple(expected_violations)

    def test_is_allowed_import_exact_match(self):
        """Test _is_allowed_import with exact matches."""
        guard = AppsTaxonomyGuard()

        # Allowed exact matches
        assert guard._is_allowed_import("agentic_core.interfaces") is True
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts") is True

        # Prohibited imports
        assert guard._is_allowed_import("agentic_core.L0_routing") is False
        assert guard._is_allowed_import("agentic_core.L4_state") is False

    def test_is_allowed_import_submodule_match(self):
        """Test _is_allowed_import with submodule matches."""
        guard = AppsTaxonomyGuard()

        # Allowed submodule imports
        assert guard._is_allowed_import("agentic_core.interfaces.api") is True
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts.v2") is True

        # Prohibited submodule imports
        assert guard._is_allowed_import("agentic_core.L0_routing.engines") is False
        assert guard._is_allowed_import("agentic_core.L4_state.storage") is False

    def test_scan_with_multiple_imports_per_line(self):
        """Test scan handles multiple imports on same line."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create file with multiple imports
            py_file = apps_dir / "multi.py"
            py_file.write_text("from agentic_core.L0_routing import PathRouter, MetaLearningBus\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect one violation with all imported names
            assert len(violations) == 1
            assert (
                "multi.py:1 from agentic_core.L0_routing import PathRouter, MetaLearningBus" in violations[0]
            )
