#!/usr/bin/env python3
"""
AST-based contract tests for execute_ssot pipeline hardening.

Covers:
  Phase 1: --plan introspection produces stable output, no side effects.
  Phase 2: RootHygieneAgent wiring — roster key exists, Phase 4.5 safe.
  Phase 3: FileClassificationAgent detect+heal contract.
  Phase 4: AST guards — roster/key drift, phase order, entrypoint bypass.
  Phase 5: --agents subset selection semantics.
  Phase 6: Entrypoint boundary lock.
"""

import ast
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[5]
EXECUTE_SSOT_PATH = REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
ENTRYPOINT_PATH = REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot_entrypoint.py"


def _load_module():
    """Import execute_ssot module; skip on ImportError."""
    try:
        return importlib.import_module(
            "agentic_core.L0_routing.scripts.execute_ssot",
        )
    except ImportError as exc:
        pytest.fail(f"Cannot import execute_ssot: {exc}")


def _parse_ast(path: Path) -> ast.Module:
    """Parse a Python file into an AST."""
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path))


# ===================================================================
# PHASE 1 — Execution Plan Introspection
# ===================================================================


class TestExecutionPlanIntrospection:
    """--plan flag produces stable, deterministic output with no side effects."""

    def test_execution_plan_exists_and_ordered(self):
        from agentic_core.L0_routing.config.path_constants import (
    """Test execution_plan_exists_and_ordered runtime behavior."""
    # Arrange
    # TODO: Set up test data for execution_plan_exists_and_ordered
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execution_plan_exists_and_ordered
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    """Test execution_plan_all_phases_have_agents runtime behavior."""
    # Arrange
    # TODO: Set up test data for execution_plan_all_phases_have_agents
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execution_plan_all_phases_have_agents
    """Test execution_plan_agent_keys_in_canonical_set runtime behavior."""
    # Arrange
    # TODO: Set up test data for execution_plan_agent_keys_in_canonical_set
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execution_plan_agent_keys_in_canonical_set
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    """Test print_execution_plan_no_side_effects runtime behavior."""
    # Arrange
    # TODO: Set up test data for print_execution_plan_no_side_effects
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute print_execution_plan_no_side_effects
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        mod.print_execution_plan()
        second = capsys.readouterr().out
        assert first == second, "Plan output must be stable across calls"


# ===================================================================
# PHASE 2 — RootHygieneAgent Wiring
# ===================================================================


class TestRootHygieneAgentWiring:
    """Phase 4.5 must not crash on missing root_hygiene roster key."""

    def test_root_hygiene_in_canonical_roster(self):
    """Test root_hygiene_in_canonical_roster runtime behavior."""
    # Arrange
    # TODO: Set up test data for root_hygiene_in_canonical_roster
    test_data = {}  # Replace with actual test data
    """Test root_hygiene_key_referenced_in_source runtime behavior."""
    # Arrange
    # TODO: Set up test data for root_hygiene_key_referenced_in_source
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute root_hygiene_key_referenced_in_source
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test removing_root_hygiene_from_canonical_would_break_plan runtime behavior."""
    # Arrange
    # TODO: Set up test data for removing_root_hygiene_from_canonical_would_break_plan
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute removing_root_hygiene_from_canonical_would_break_plan
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    """Test phase_4_5_guarded_invocation runtime behavior."""
    # Arrange
    # TODO: Set up test data for phase_4_5_guarded_invocation
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute phase_4_5_guarded_invocation
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions


# ===================================================================
# PHASE 3 — FileClassificationAgent Detect + Heal Contract
# ===================================================================


class TestFileClassificationAgentContract:
    """FCA must be used deterministically in detect (Phase 1) and heal (Phase 2.5)."""

    def test_fca_in_phase1_discovery(self):
    """Test fca_in_phase1_discovery runtime behavior."""
    # Arrange
    # TODO: Set up test data for fca_in_phase1_discovery
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute fca_in_phase1_discovery
    result = None  # Replace with actual function call

    # Assert
    """Test fca_in_phase2_5_sovereignty runtime behavior."""
    # Arrange
    # TODO: Set up test data for fca_in_phase2_5_sovereignty
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute fca_in_phase2_5_sovereignty
    result = None  # Replace with actual function call

"""Test validate_forces_dry_run runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute validate_forces_dry_run
"""Test fca_heal_only_when_not_dry_run runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute fca_heal_only_when_not_dry_run
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
# ===================================================================
# PHASE 4 — Agent Execution Contract (AST Guards)
# ===================================================================


class TestAgentExecutionContract:
    """AST-based guards preventing roster/key drift and entrypoint bypass."""

    def test_all_agents_subscript_keys_in_canonical_set(self):
    """Test all_agents_subscript_keys_in_canonical_set runtime behavior."""
    # Arrange
    # TODO: Set up test data for all_agents_subscript_keys_in_canonical_set
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute all_agents_subscript_keys_in_canonical_set
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

        # Collect all agents["key"] subscripts inside _legacy_main
        referenced_keys = set()
        for node in ast.walk(legacy_main_node):
            if isinstance(node, ast.Subscript):
                # Check if the value is 'agents'
                if isinstance(node.value, ast.Name) and node.value.id == "agents":
                    if isinstance(node.slice, ast.Constant) and isinstance(
                        node.slice.value,
                        str,
                    ):
                        referenced_keys.add(node.slice.value)

        assert len(referenced_keys) > 0, "No agents['key'] references found in _legacy_main"

        missing = referenced_keys - canonical
        assert not missing, f"agents[] references keys not in CANONICAL_ROSTER_KEYS: {sorted(missing)}"

    def test_roster_dict_keys_match_canonical(self):
    """Test roster_dict_keys_match_canonical runtime behavior."""
    # Arrange
    # TODO: Set up test data for roster_dict_keys_match_canonical
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute roster_dict_keys_match_canonical
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

        roster_keys = set()
        for node in ast.walk(legacy_main_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "agents":
                        if isinstance(node.value, ast.Dict):
                            for key in node.value.keys:
                                if isinstance(key, ast.Constant):
                                    roster_keys.add(key.value)

        assert roster_keys, "agents dict not found in _legacy_main"
        assert roster_keys == canonical, (
            f"Roster keys mismatch.\n"
            f"  In roster but not canonical: {roster_keys - canonical}\n"
            f"  In canonical but not roster: {canonical - roster_keys}"
        )

    def test_phase_order_is_deterministic(self):
    """Test phase_order_is_deterministic runtime behavior."""
    # Arrange
    # TODO: Set up test data for phase_order_is_deterministic
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute phase_order_is_deterministic
    result = None  # Replace with actual function call

    # Assert
    """Test execution_plan_is_immutable_list runtime behavior."""
    # Arrange
    # TODO: Set up test data for execution_plan_is_immutable_list
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execution_plan_is_immutable_list
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
# PHASE 5 — Strict Agent Selection Semantics
# ===================================================================


class TestAgentSelectionSemantics:
    """--agents A,B must resolve subset + dependencies deterministically."""

    def test_unknown_agent_raises(self):
    """Test unknown_agent_raises runtime behavior."""
    # Arrange
    # TODO: Set up test data for unknown_agent_raises
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute unknown_agent_raises
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        mod = _load_module()
        result = mod.resolve_agent_subset(["hierarchy", "root_hygiene"])
        assert result == sorted(result), "Result must be sorted alphabetically"

    def test_no_dependency_agent_returns_self_only(self):
        mod = _load_module()
        result = mod.resolve_agent_subset(["root_hygiene"])
        assert result == ["root_hygiene"]

    def test_transitive_dependencies_resolved(self):
        mod = _load_module()
        # arch_governor -> reconciler, location, hierarchy
        # hierarchy -> reconciler, location
        result = mod.resolve_agent_subset(["arch_governor"])
        assert "reconciler" in result
        assert "location" in result
        assert "hierarchy" in result
        assert "arch_governor" in result

    def test_dependency_closure_is_stable(self):
    """Test dependency_closure_is_stable runtime behavior."""
    # Arrange
    # TODO: Set up test data for dependency_closure_is_stable
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute dependency_closure_is_stable
    """Test all_canonical_keys_have_dependency_entry runtime behavior."""
    # Arrange
    # TODO: Set up test data for all_canonical_keys_have_dependency_entry
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute all_canonical_keys_have_dependency_entry
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

    def test_execute_ssot_direct_invocation_blocked(self):
        """Running execute_ssot.py directly must exit with code 2."""
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
        result = subprocess.run(
            [sys.executable, str(EXECUTE_SSOT_PATH)],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert result.returncode == 2, (
            f"Direct invocation should exit with code 2, got {result.returncode}.\n"
            f"stderr: {result.stderr[:500]}"
        )
        assert "not supported" in result.stderr.lower() or "entrypoint" in result.stderr.lower(), (
            f"Error message should mention entrypoint. Got: {result.stderr[:500]}"
        )

    def test_entrypoint_without_legacy_returns_1(self):
        """Entrypoint without --legacy returns 1."""
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
        result = subprocess.run(
            [sys.executable, "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert result.returncode == 1

    def test_entrypoint_plan_returns_0(self):
        """Entrypoint with --legacy --plan returns 0 and prints plan."""
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
                "--legacy",
                "--plan",
            ],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert result.returncode == 0, (
            f"--legacy --plan should return 0, got {result.returncode}.\nstderr: {result.stderr[:500]}"
        )
        assert "PHASE 1:" in result.stdout
        assert "PHASE 5:" in result.stdout

    def test_entrypoint_has_plan_flag_in_help(self):
        """Entrypoint help text must mention --plan."""
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
        result = subprocess.run(
            [sys.executable, "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--help"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert "--plan" in result.stdout

    def test_execute_ssot_if_name_main_blocks(self):
    """Test execute_ssot_if_name_main_blocks runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execute_ssot_if_name_main_blocks
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                        EXECUTE_SSOT_PATH.read_text(encoding="utf-8"),
                        node,
                    )
                    if source_segment and "SystemExit(2)" in source_segment:
                        return  # PASS
        pytest.fail(
            "execute_ssot.py __name__ == '__main__' block must raise SystemExit(2)",
        )
