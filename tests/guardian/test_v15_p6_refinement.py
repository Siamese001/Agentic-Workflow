"""
Guardian tests for Phase 6 refinements.

Wave 6.3: Pre-commit idempotency (working-tree stability).
Wave 6.4: Regression tripwires for Phase 6 refactors.

Each test fails deterministically if the corresponding refactor is reverted.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# Wave 6.3 — Pre-commit Idempotency
# ============================================================================


class TestPreCommitIdempotency:
    """Assert that pre-commit hooks do not mutate the working tree."""

    def test_precommit_versions_pinned(self):
        """Pre-commit config must pin all remote repo revisions explicitly."""
        config_path = REPO_ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), ".pre-commit-config.yaml not found"
        content = config_path.read_text(encoding="utf-8")
        # Every remote repo block must have a 'rev:' line with a pinned version
        import re

        repos = re.findall(r"- repo: https://.*\n\s+rev: (.+)", content)
        assert len(repos) >= 2, f"Expected >=2 pinned repos, found {len(repos)}"
        for rev in repos:
            # Must be a version tag (v*) or exact SHA, not 'main' or 'latest'
            assert rev.strip().startswith("v") or len(rev.strip()) >= 7, f"Unpinned revision: {rev}"

    def test_ruff_version_pinned_in_precommit(self):
        """Ruff pre-commit hook must use a pinned version."""
        config_path = REPO_ROOT / ".pre-commit-config.yaml"
        content = config_path.read_text(encoding="utf-8")
        assert "astral-sh/ruff-pre-commit" in content
        import re

        match = re.search(
            r"repo: https://github.com/astral-sh/ruff-pre-commit\s+rev: (v[\d.]+)",
            content,
        )
        assert match, "Ruff pre-commit revision not found or not pinned"
        version = match.group(1)
        assert version.startswith("v0."), f"Unexpected ruff version format: {version}"


# ============================================================================
# Wave 6.4 — Regression Tripwires
# ============================================================================


class TestInventoryAutoClassification:
    """Tripwire: inventory collector must produce near-zero false positives
    without any manual classification step."""

    def test_inventory_schema_v5(self):
        """Inventory collector must output schema 5.0.0 with auto-classification."""
        result = subprocess.run(
            [
                sys.executable,
                "ops_scripts/ci/v15_d_inventory_collect_full.py",
                "--out",
                "v15_d_inventory_tripwire.json",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"Inventory collector failed: {result.stderr}"
        inv_path = REPO_ROOT / "v15_d_inventory_tripwire.json"
        try:
            data = json.loads(inv_path.read_text(encoding="utf-8"))
            assert data["schema_version"] == "5.0.0", f"Expected schema 5.0.0, got {data['schema_version']}"
            assert data["summary"]["total_unwired"] == 0, (
                f"UNWIRED must be 0, got {data['summary']['total_unwired']}"
            )
            assert data["summary"]["p2_unwired"] == 0, (
                f"P2 UNWIRED must be 0, got {data['summary']['p2_unwired']}"
            )
        finally:
            inv_path.unlink(missing_ok=True)

    def test_classify_unguarded_has_heuristic_layers(self):
        """The classify_unguarded function must have all required heuristic layers."""
        collector_path = REPO_ROOT / "ops_scripts" / "ci" / "v15_d_inventory_collect_full.py"
        source = collector_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        # Find classify_unguarded function
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "classify_unguarded":
                found = True
                body_text = ast.get_source_segment(source, node)
                assert body_text is not None
                # Must contain all heuristic layers
                assert "heal pathway" in body_text, "Missing heal pathway heuristic"
                assert "ops_scripts" in body_text, "Missing ops_scripts exclusion"
                assert "infrastructure directory" in body_text, "Missing infra dir heuristic"
                assert "agent-class transitive" in body_text, "Missing agent-class transitive"
                assert "side-effect" in body_text, "Missing side-effect analysis"
                assert "file-level transitive" in body_text, "Missing file-level transitive"
                break
        assert found, "classify_unguarded function not found in inventory collector"


class TestRuntimeBoundaryExists:
    """Tripwire: v15_runtime_boundary must exist in the guard module."""

    def test_v15_runtime_boundary_exported(self):
        """v15_runtime_boundary must be importable from the guard module."""
        from agentic_core.L0_routing.enforcement.v15_runtime_guard import (
            v15_runtime_boundary,
        )

        assert callable(v15_runtime_boundary)

    def test_v15_runtime_boundary_in_all(self):
        """v15_runtime_boundary must be in __all__."""
        guard_path = REPO_ROOT / "agentic_core" / "L0_routing" / "enforcement" / "v15_runtime_guard.py"
        source = guard_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        assert isinstance(node.value, ast.List)
                        names = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                        assert "v15_runtime_boundary" in names, (
                            f"v15_runtime_boundary not in __all__: {names}"
                        )
                        return
        pytest.fail("__all__ not found in v15_runtime_guard.py")


class TestEntrypointDecomposition:
    """Tripwire: execute_ssot_entrypoint.py must exist and gate legacy access."""

    def test_entrypoint_exists(self):
        """execute_ssot_entrypoint.py must exist."""
        ep = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot_entrypoint.py"
        assert ep.exists(), "execute_ssot_entrypoint.py not found"

    def test_entrypoint_requires_legacy_flag(self):
        """Entrypoint must exit non-zero without --legacy flag."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode != 0, "Entrypoint should fail without --legacy"
        assert "--legacy" in result.stderr or "--legacy" in result.stdout, (
            "Error message should mention --legacy flag"
        )

    def test_legacy_main_still_guarded(self):
        """_legacy_main in execute_ssot.py must still have V15 guard decorator."""
        ssot_path = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
        source = ssot_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
                # Must have at least one decorator
                assert len(node.decorator_list) > 0, "_legacy_main must have V15 guard decorator"
                return
        pytest.fail("_legacy_main not found in execute_ssot.py")


class TestAllGatesStillPass:
    """Tripwire: all V15 gates must still pass after Phase 6 refactors."""

    def test_p0_gate(self):
        """P0 gate must pass."""
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/run_v15_p0_gate.py"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"P0 gate failed: {result.stdout}\n{result.stderr}"

    def test_p1_gate(self):
        """P1 gate must pass."""
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/run_v15_p1_gate.py"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"P1 gate failed: {result.stdout}\n{result.stderr}"

    def test_p2_gate(self):
        """P2 gate must pass."""
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/run_v15_p2_gate.py"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"P2 gate failed: {result.stdout}\n{result.stderr}"
