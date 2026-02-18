"""
Guardian test: Wave 2.2 Fail-Closed Bypass Negative Tests.

Proves that under V15_ENFORCEMENT=1, direct execution at/behind an
enforcement boundary WITHOUT the runtime_guard raises
V15EnforcementError deterministically.

One representative per category A-E (minimum 5 tests) plus a coverage
assertion that every inventory entrypoint is either AST-wired or
already_v15_enforced.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.enforcement.runtime_guard import (
    _get_active_guards,
    assert_v15_guarded,
)
from agentic_core.L0_routing.types.guardian_contract import V15EnforcementError

INVENTORY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reports"
    / "plans"
    / "v15_phase2_wave2_1_runtime_entrypoints.json"
)


@pytest.fixture(autouse=True)
def _enforce_v15(monkeypatch):
    """Enable V15 enforcement for all tests in this module."""
    monkeypatch.setenv("V15_ENFORCEMENT", "1")
    yield
    # Clean up any leftover guard state
    active = _get_active_guards()
    active.clear()


class TestCategoryABypass:
    """Category A: Planner/Orchestrator — bypass must fail."""

    def test_run_mission_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for run_mission outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("A.run_mission.orchestrator_engine")

    def test_execute_orchestrator_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for execute outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("A.execute.orchestrator_engine")


class TestCategoryBBypass:
    """Category B: Executor/Tool — bypass must fail."""

    def test_agent_engine_run_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for agent_engine.run outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("B.run.agent_engine")

    def test_execute_tool_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for execute_tool outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("B.execute_tool.L2ExecutionBase")


class TestCategoryCBypass:
    """Category C: Background worker — bypass must fail."""

    def test_daemon_mode_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for run_daemon_mode outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("C.run_daemon_mode.mission_runner")


class TestCategoryDBypass:
    """Category D: Retry/Fallback — bypass must fail."""

    def test_with_retry_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for with_retry outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("D.with_retry.tool_reliability_mixin")


class TestCategoryEBypass:
    """Category E: CLI — bypass must fail."""

    def test_surgical_mode_bypass_raises(self) -> None:
        """Calling assert_v15_guarded for run_surgical_mode outside guard must raise."""
        with pytest.raises(V15EnforcementError, match="V15 bypass detected"):
            assert_v15_guarded("E.run_surgical_mode.mission_runner")


class TestGuardPassThrough:
    """Verify that assert_v15_guarded passes when guard IS active."""

    def test_guarded_call_does_not_raise(self) -> None:
        """When guard is active, assert_v15_guarded must not raise."""
        active = _get_active_guards()
        entry_id = "A.run_mission.orchestrator_engine"
        active.add(entry_id)
        try:
            assert_v15_guarded(entry_id)  # Must not raise
        finally:
            active.discard(entry_id)


class TestEnforcementDisabled:
    """Verify that under V15_ENFORCEMENT=0, assert_v15_guarded is a no-op."""

    def test_no_enforcement_no_raise(self, monkeypatch) -> None:
        """With V15_ENFORCEMENT=0, bypass check is a no-op."""
        monkeypatch.setenv("V15_ENFORCEMENT", "0")
        assert_v15_guarded("A.run_mission.orchestrator_engine")  # Must not raise


class TestInventoryCoverageAssertion:
    """Every inventory entrypoint must be WIRED or ALREADY_ENFORCED."""

    def test_all_unenforced_entrypoints_have_guard_decorator(self) -> None:
        """AST-verify that every unenforced entrypoint has runtime_guard decorator."""
        import ast

        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        repo_root = Path(__file__).resolve().parents[2]

        unwired: list[str] = []
        for ep in inventory["entrypoints"]:
            if ep.get("already_v15_enforced"):
                continue

            ep_path = repo_root / ep["path"]
            if not ep_path.exists():
                unwired.append(f"{ep['id']} (file missing: {ep['path']})")
                continue

            source = ep_path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                unwired.append(f"{ep['id']} (syntax error in {ep['path']})")
                continue

            # Check if runtime_guard with this entry_point_id appears as a decorator
            found = _ast_find_guard_decorator(tree, ep["id"])
            if not found:
                unwired.append(ep["id"])

        assert not unwired, f"Unenforced entrypoints missing runtime_guard decorator: {unwired}"


def _ast_find_guard_decorator(tree: ast.Module, entry_point_id: str) -> bool:
    """AST-search for @runtime_guard("<entry_point_id>") decorator in module.

    Also recognises the lazy-import variant @_optional_runtime_guard()("ID").
    """
    import ast

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not dec.args:
                continue
            arg = dec.args[0]
            if not (isinstance(arg, ast.Constant) and arg.value == entry_point_id):
                continue
            func = dec.func
            # Shape 1: @runtime_guard("ID")
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name == "runtime_guard":
                return True
            # Shape 2: @_optional_runtime_guard()("ID")
            if isinstance(func, ast.Call):
                inner = func.func
                inner_name = None
                if isinstance(inner, ast.Name):
                    inner_name = inner.id
                elif isinstance(inner, ast.Attribute):
                    inner_name = inner.attr
                if inner_name == "_optional_runtime_guard":
                    return True
    return False
