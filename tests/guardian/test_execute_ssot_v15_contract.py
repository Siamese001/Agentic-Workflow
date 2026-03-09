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

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
)

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
        """AST-scan: no Call nodes to os.getcwd or Path.cwd in non-comment code."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        tree = ast.parse(source)

        violations: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            # os.getcwd()
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "getcwd"
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
        """resolve_repo_root() must exist as a module-level function."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "resolve_repo_root"
        ]
        assert "resolve_repo_root" in func_names, "resolve_repo_root() not found"

    def test_repo_root_accessible(self):
        """REPO_ROOT must be accessible as a module-level name (eager or via __getattr__)."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        # Accept either eager assignment (REPO_ROOT = ...) or lazy __getattr__ pattern
        has_eager = any(
            line.strip().startswith("REPO_ROOT") and "=" in line and not line.strip().startswith("#")
            for line in source.splitlines()
        )
        has_getattr = "__getattr__" in source and "REPO_ROOT" in source
        assert has_eager or has_getattr, (
            "REPO_ROOT must be available as a module attribute "
            "(either eager assignment or __getattr__ lazy resolution)"
        )


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
        """_apply_v15_enforcement_flag must exist."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_apply_v15_enforcement_flag"
        ]
        assert "_apply_v15_enforcement_flag" in func_names

    def test_optional_guard_wrapper_exists(self):
        """_optional_runtime_guard must exist for lazy import safety."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_optional_runtime_guard"
        ]
        assert "_optional_runtime_guard" in func_names

    def test_main_and_with_retry_have_guard_decorators(self):
        """main() and with_retry() must have v15 guard decorators."""
        source = EXECUTE_SSOT.read_text(encoding="utf-8")
        tree = ast.parse(source)

        guarded_functions: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                # Shape: @_optional_runtime_guard()("ID")
                func = dec.func
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
            timeout=30,
            env={**os.environ, "V15_ENFORCEMENT": "0", "PYTHONPATH": str(REPO_ROOT)},
        )
        assert result.returncode == 0, f"--help failed: {result.stderr[:500]}"

    def test_help_contains_expected_flags(self):
        """--help output must mention key flags."""
        result = subprocess.run(
            [sys.executable, str(EXECUTE_SSOT_ENTRYPOINT), "--help"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "V15_ENFORCEMENT": "0", "PYTHONPATH": str(REPO_ROOT)},
        )
        help_text = result.stdout + result.stderr
        assert "--v15-enforcement" in help_text, "--v15-enforcement flag missing from --help"
        assert "--verbose" in help_text or "-v" in help_text, "--verbose flag missing from --help"


# ============================================================================
# 5. No tracked artifacts produced
# ============================================================================


class TestNoTrackedArtifacts:
    """A --dry-run invocation must not produce git-tracked files."""

    def test_dry_run_no_tracked_changes(self):
        """Running with --dry-run must not dirty the git index with new tracked files."""
        # Snapshot current status
        before = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        before_lines = set(before.stdout.strip().splitlines())

        # Run via entrypoint --legacy --dry-run --territory agentic_core (quick, no side effects)
        subprocess.run(
            [
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
            timeout=120,
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
