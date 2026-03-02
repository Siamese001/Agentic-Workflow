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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[4]
EXECUTE_SSOT_PATH = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
ENTRYPOINT_PATH = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot_entrypoint.py"


def _load_module():
    """Import execute_ssot module; skip on ImportError."""
    try:
        return importlib.import_module(
            "agentic_core.L0_routing.scripts.execute_ssot",
        )
    except ImportError as exc:
        pytest.skip(f"Cannot import execute_ssot: {exc}")


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
        mod = _load_module()
        plan = mod.get_execution_plan()
        assert isinstance(plan, list)
        assert len(plan) >= 5, "Plan must have at least 5 phases"

        # Phase order is deterministic
        phase_ids = [p["phase"] for p in plan]
        assert phase_ids == sorted(
            phase_ids,
            key=lambda x: float(x),
        ), "Phases must be in ascending numeric order"

    def test_execution_plan_all_phases_have_agents(self):
        mod = _load_module()
        plan = mod.get_execution_plan()
        for phase in plan:
            assert "agents" in phase, f"Phase {phase['phase']} missing agents key"
            assert len(phase["agents"]) >= 1, f"Phase {phase['phase']} has no agents"

    def test_execution_plan_agent_keys_in_canonical_set(self):
        mod = _load_module()
        plan = mod.get_execution_plan()
        canonical = mod.CANONICAL_ROSTER_KEYS
        for phase in plan:
            for agent in phase["agents"]:
                key = agent["key"]
                if key == "*":
                    continue  # wildcard for aggregation phase
                assert key in canonical, (
                    f"Phase {phase['phase']} references unknown agent key '{key}'. Valid: {sorted(canonical)}"
                )

    def test_print_execution_plan_no_side_effects(self, capsys):
        mod = _load_module()
        mod.print_execution_plan()
        captured = capsys.readouterr()
        assert "PHASE 1:" in captured.out
        assert "PHASE 5:" in captured.out
        # Must contain agent.method format
        assert "reconciler.detect_root_drift" in captured.out

    def test_plan_flag_stable_output(self, capsys):
        """Two consecutive calls produce identical output."""
        mod = _load_module()
        mod.print_execution_plan()
        first = capsys.readouterr().out
        mod.print_execution_plan()
        second = capsys.readouterr().out
        assert first == second, "Plan output must be stable across calls"


# ===================================================================
# PHASE 2 — RootHygieneAgent Wiring
# ===================================================================


class TestRootHygieneAgentWiring:
    """Phase 4.5 must not crash on missing root_hygiene roster key."""

    def test_root_hygiene_in_canonical_roster(self):
        mod = _load_module()
        assert "root_hygiene" in mod.CANONICAL_ROSTER_KEYS

    def test_root_hygiene_key_referenced_in_source(self):
        """AST scan: agents['root_hygiene'] must appear in _legacy_main."""
        tree = _parse_ast(EXECUTE_SSOT_PATH)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant) and node.slice.value == "root_hygiene":
                    found = True
                    break
        assert found, "agents['root_hygiene'] not found in execute_ssot.py"

    def test_removing_root_hygiene_from_canonical_would_break_plan(self):
        """If root_hygiene were removed from CANONICAL_ROSTER_KEYS,
        the plan integrity check would fail."""
        mod = _load_module()
        plan = mod.get_execution_plan()
        plan_keys = set()
        for phase in plan:
            for agent in phase["agents"]:
                if agent["key"] != "*":
                    plan_keys.add(agent["key"])
        assert "root_hygiene" in plan_keys, "root_hygiene must be referenced in EXECUTION_PLAN"

    def test_phase_4_5_guarded_invocation(self):
        """Phase 4.5 RootHygieneAgent block is wrapped in try/except."""
        source = EXECUTE_SSOT_PATH.read_text(encoding="utf-8")
        # Verify that agents["root_hygiene"] is inside a try block
        lines = source.splitlines()
        for i, line in enumerate(lines):
            if 'agents["root_hygiene"]' in line:
                # Walk backwards to find enclosing try
                for j in range(i - 1, max(i - 20, 0), -1):
                    if lines[j].strip().startswith("try:"):
                        return  # PASS
        pytest.fail(
            'agents["root_hygiene"] is not inside a try block in Phase 4.5',
        )


# ===================================================================
# PHASE 3 — FileClassificationAgent Detect + Heal Contract
# ===================================================================


class TestFileClassificationAgentContract:
    """FCA must be used deterministically in detect (Phase 1) and heal (Phase 2.5)."""

    def test_fca_in_phase1_discovery(self):
        """Phase 1 must invoke file_classification with validate_only=True, dry_run=True."""
        mod = _load_module()
        plan = mod.get_execution_plan()
        phase1 = [p for p in plan if p["phase"] == "1"][0]
        fca_agents = [a for a in phase1["agents"] if a["key"] == "file_classification"]
        assert len(fca_agents) == 1, "FCA must be in Phase 1"
        assert "validate_only=True" in fca_agents[0].get("kwargs", "")
        assert "dry_run=True" in fca_agents[0].get("kwargs", "")

    def test_fca_in_phase2_5_sovereignty(self):
        """Phase 2.5 must invoke file_classification.heal_repository."""
        mod = _load_module()
        plan = mod.get_execution_plan()
        phase25 = [p for p in plan if p["phase"] == "2.5"][0]
        fca_agents = [a for a in phase25["agents"] if a["key"] == "file_classification"]
        assert len(fca_agents) == 1, "FCA must be in Phase 2.5"
        assert fca_agents[0]["method"] == "heal_repository"

    def test_validate_forces_dry_run(self):
        """--validate must force dry_run=True (centralized mapping)."""
        source = EXECUTE_SSOT_PATH.read_text(encoding="utf-8")
        # The centralized mapping: if args.validate: args.dry_run = True
        assert "if args.validate:" in source
        assert "args.dry_run = True" in source

    def test_fca_heal_only_when_not_dry_run(self):
        """heal_repository is only invoked when pascal_proceed and not dry_run."""
        source = EXECUTE_SSOT_PATH.read_text(encoding="utf-8")
        # Find the sovereignty purge block
        idx = source.find("pascal_proceed and not dry_run")
        assert idx != -1, "Sovereignty purge must be gated by 'pascal_proceed and not dry_run'"
        # heal_repository must appear after the gate
        heal_idx = source.find("heal_repository", idx)
        assert heal_idx != -1, "heal_repository must be invoked inside the gate block"


# ===================================================================
# PHASE 4 — Agent Execution Contract (AST Guards)
# ===================================================================


class TestAgentExecutionContract:
    """AST-based guards preventing roster/key drift and entrypoint bypass."""

    def test_all_agents_subscript_keys_in_canonical_set(self):
        """Every agents['key'] reference in _legacy_main must exist
        in CANONICAL_ROSTER_KEYS."""
        mod = _load_module()
        canonical = mod.CANONICAL_ROSTER_KEYS
        tree = _parse_ast(EXECUTE_SSOT_PATH)

        # Find _legacy_main function node
        legacy_main_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
                legacy_main_node = node
                break
        assert legacy_main_node is not None, "_legacy_main not found"

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
        """The agents = {{...}} dict in _legacy_main must have exactly
        the keys in CANONICAL_ROSTER_KEYS."""
        mod = _load_module()
        canonical = mod.CANONICAL_ROSTER_KEYS
        tree = _parse_ast(EXECUTE_SSOT_PATH)

        # Find agents = {...} assignment inside _legacy_main
        legacy_main_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
                legacy_main_node = node
                break
        assert legacy_main_node is not None

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
        """EXECUTION_PLAN phase order must be strictly ascending."""
        mod = _load_module()
        plan = mod.get_execution_plan()
        phase_nums = [float(p["phase"]) for p in plan]
        for i in range(1, len(phase_nums)):
            assert phase_nums[i] > phase_nums[i - 1], (
                f"Phase order is not strictly ascending: {phase_nums[i - 1]} >= {phase_nums[i]}"
            )

    def test_execution_plan_is_immutable_list(self):
        """EXECUTION_PLAN must be a module-level list (not dynamically built)."""
        tree = _parse_ast(EXECUTE_SSOT_PATH)
        found = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "EXECUTION_PLAN":
                        assert isinstance(node.value, ast.List), "EXECUTION_PLAN must be a list literal"
                        found = True
        assert found, "EXECUTION_PLAN not found as module-level assignment"


# ===================================================================
# PHASE 5 — Strict Agent Selection Semantics
# ===================================================================


class TestAgentSelectionSemantics:
    """--agents A,B must resolve subset + dependencies deterministically."""

    def test_unknown_agent_raises(self):
        mod = _load_module()
        with pytest.raises(ValueError, match="Unknown agent key"):
            mod.resolve_agent_subset(["nonexistent_agent"])

    def test_known_agent_returns_with_dependencies(self):
        mod = _load_module()
        result = mod.resolve_agent_subset(["hierarchy"])
        assert "hierarchy" in result
        # hierarchy depends on reconciler and location
        assert "reconciler" in result
        assert "location" in result

    def test_subset_is_sorted(self):
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
        """Two calls produce identical results."""
        mod = _load_module()
        r1 = mod.resolve_agent_subset(["arch_governor", "root_hygiene"])
        r2 = mod.resolve_agent_subset(["arch_governor", "root_hygiene"])
        assert r1 == r2

    def test_all_canonical_keys_have_dependency_entry(self):
        """Every key in CANONICAL_ROSTER_KEYS must appear in AGENT_DEPENDENCIES."""
        mod = _load_module()
        for key in mod.CANONICAL_ROSTER_KEYS:
            assert key in mod.AGENT_DEPENDENCIES, f"Agent key '{key}' missing from AGENT_DEPENDENCIES"


# ===================================================================
# PHASE 6 — Entrypoint Boundary Lock
# ===================================================================


class TestEntrypointBoundaryLock:
    """Only execute_ssot_entrypoint.py is the public CLI."""

    def test_execute_ssot_direct_invocation_blocked(self):
        """Running execute_ssot.py directly must exit with code 2."""
        env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
        result = subprocess.run(
            [sys.executable, str(EXECUTE_SSOT_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
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
            timeout=30,
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
            timeout=30,
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
            timeout=30,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert "--plan" in result.stdout

    def test_execute_ssot_if_name_main_blocks(self):
        """AST check: if __name__ == '__main__' must raise SystemExit(2)."""
        tree = _parse_ast(EXECUTE_SSOT_PATH)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.If):
                # Check for if __name__ == "__main__"
                test = node.test
                if (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                ):
                    # Must contain SystemExit(2)
                    source_segment = ast.get_source_segment(
                        EXECUTE_SSOT_PATH.read_text(encoding="utf-8"),
                        node,
                    )
                    if source_segment and "SystemExit(2)" in source_segment:
                        return  # PASS
        pytest.fail(
            "execute_ssot.py __name__ == '__main__' block must raise SystemExit(2)",
        )
