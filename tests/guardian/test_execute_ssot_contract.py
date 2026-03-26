"""
Guardian contract tests for execute_ssot.py (Phase 3 Wave 3.1C).

Proves:
1. Deterministic repo-root resolution (never os.getcwd())
2. Default outputs land in gitignored location
3. V15_ENFORCEMENT=1 fail-closed behaviour
4. CLI contract stable (--help exits 0, known flags accepted)
5. No tracked artifacts produced by a dry-run invocation
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTE_SSOT = REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
EXECUTE_SSOT_ENTRYPOINT = REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot_entrypoint.py"
GITIGNORE = REPO_ROOT / ".gitignore"


# ============================================================================
# 1. Deterministic repo-root
# ============================================================================


class TestDeterministicRepoRoot:
    """execute_ssot.py must never depend on os.getcwd() / Path.cwd() at runtime."""

    def test_no_cwd_calls_in_source(self):
        from agentic_core.L0_routing.config.path_constants import (
    """Test no_cwd_calls_in_source runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute no_cwd_calls_in_source
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                and isinstance(func.value, ast.Name)
                and func.value.id == "os"
            ):
                violations.append(f"os.getcwd() at line {node.lineno}")
            # Path.cwd()
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "cwd"
                and isinstance(func.value, ast.Name)
                and func.value.id == "Path"
            ):
                violations.append(f"Path.cwd() at line {node.lineno}")

        assert not violations, f"cwd-dependent calls found: {violations}"

    def test_resolve_repo_root_defined(self):
    """Test resolve_repo_root_defined runtime behavior."""
    # Arrange
    # TODO: Set up test data for resolve_repo_root_defined
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute resolve_repo_root_defined
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test repo_root_accessible runtime behavior."""
    # Arrange
    # TODO: Set up test data for repo_root_accessible
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute repo_root_accessible
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

# ============================================================================
# 2. Default outputs gitignored
# ============================================================================


class TestDefaultOutputsGitignored:
    """Default output directory must be covered by .gitignore."""

    def test_logs_dir_gitignored(self):
        """agentic_core/L0_routing/logs/ should be gitignored or its contents should be."""
        result = subprocess.run(
            ["git", "check-ignore", "-q", "agentic_core/L0_routing/logs/test_artifact.json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # exit 0 = ignored, exit 1 = tracked
        # If the specific path isn't ignored, check if guardian_report.json pattern covers it
        if result.returncode != 0:
            # Check the broader pattern
            result2 = subprocess.run(
                ["git", "check-ignore", "-q", "agentic_core/L0_routing/logs/guardian_report.json"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            assert result2.returncode == 0, (
                "Default output location (agentic_core/L0_routing/logs/) "
                "is not gitignored — tracked artifacts risk"
            )

    def test_evidence_json_gitignored(self):
        """v15_d_evidence_p2.json must be gitignored."""
        result = subprocess.run(
            ["git", "check-ignore", "-q", "v15_d_evidence_p2.json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "v15_d_evidence_p2.json is not gitignored"


# ============================================================================
# 3. V15_ENFORCEMENT=1 fail-closed
# ============================================================================


class TestV15FailClosed:
    """When V15_ENFORCEMENT=1, unguarded paths must raise."""

    def test_v15_enforcement_flag_helper_exists(self):
    """Test v15_enforcement_flag_helper_exists runtime behavior."""
    # Arrange
    # TODO: Set up test data for v15_enforcement_flag_helper_exists
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute v15_enforcement_flag_helper_exists
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test optional_guard_wrapper_exists runtime behavior."""
    # Arrange
    # TODO: Set up test data for optional_guard_wrapper_exists
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute optional_guard_wrapper_exists
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test main_and_with_retry_have_guard_decorators runtime behavior."""
    # Arrange
    # TODO: Set up test data for main_and_with_retry_have_guard_decorators
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute main_and_with_retry_have_guard_decorators
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
                if isinstance(func, ast.Call):
                    inner = func.func
                    if isinstance(inner, ast.Name) and inner.id == "_optional_runtime_guard":
                        guarded_functions.add(node.name)
                # Shape: @runtime_guard("ID")
                elif isinstance(func, ast.Name) and func.id == "runtime_guard":
                    guarded_functions.add(node.name)

        assert "main" in guarded_functions or "with_retry" in guarded_functions, (
            f"Expected main/with_retry to have v15 guard decorators, found: {guarded_functions}"
        )


# ============================================================================
# 4. CLI contract stable
# ============================================================================


class TestCLIContract:
    """CLI interface must be stable and parseable."""

    def test_help_exits_zero(self):
        """--help must exit 0."""
        result = subprocess.run(
            [sys.executable, str(EXECUTE_SSOT_ENTRYPOINT), "--help"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            env={**os.environ, "V15_ENFORCEMENT": "0", "PYTHONPATH": str(REPO_ROOT)},
        )
        assert result.returncode == 0, f"--help failed: {result.stderr[:500]}"

    def test_help_contains_expected_flags(self):
    """Test help_contains_expected_flags runtime behavior."""
    # Arrange
    # TODO: Set up test data for help_contains_expected_flags
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute help_contains_expected_flags
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

# ============================================================================
# 5. No tracked artifacts produced
# ============================================================================


class TestNoTrackedArtifacts:
    """A --dry-run invocation must not produce git-tracked files."""

    def test_dry_run_no_tracked_changes(self):
    """Test dry_run_no_tracked_changes runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute dry_run_no_tracked_changes
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                sys.executable,
                str(EXECUTE_SSOT_ENTRYPOINT),
                "--legacy",
                "--v15-enforcement",
                "0",
                "--dry-run",
                "--territory",
                AGENTIC_CORE_DIR,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            env={**os.environ, "V15_ENFORCEMENT": "0"},
        )

        # Check status after
        after = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        after_lines = set(after.stdout.strip().splitlines())

        new_tracked = after_lines - before_lines
        # Filter to only truly new untracked files (lines starting with "??")
        # that are NOT gitignored
        new_artifacts = []
        for line in new_tracked:
            if line.startswith("??"):
                fpath = line[3:].strip().strip('"')
                check = subprocess.run(
                    ["git", "check-ignore", "-q", fpath],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                )
                if check.returncode != 0:  # NOT ignored = would be tracked
                    new_artifacts.append(fpath)

        assert not new_artifacts, f"Dry-run produced tracked artifacts: {new_artifacts}"
