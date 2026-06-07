"""Surface coverage for `agentic_core.L5_safety.reasoning.GovernanceAgent`.

Wave 4 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L5 governance core.
Highest fan-out untested module (14). Drives ArchitectureGovernor enforcement.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.GovernanceAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_governance_agent_class_present(mod):
    assert hasattr(mod, "GovernanceAgent")
    assert inspect.isclass(mod.GovernanceAgent)


def test_dependency_graph_class_present(mod):
    assert hasattr(mod, "DependencyGraph")
    assert inspect.isclass(mod.DependencyGraph)


def test_heal_top_level_callable(mod):
    """Module-level heal() helper callable per signature heal(violation: dict) -> dict."""
    assert hasattr(mod, "heal")
    assert callable(mod.heal)


def test_factories_callable(mod):
    for name in ("create_architecture_governor", "get_GovernanceAgent"):
        fn = getattr(mod, name, None)
        assert callable(fn), f"{name} must be callable"


def test_get_governance_agent_signature(mod):
    sig = inspect.signature(mod.get_GovernanceAgent)
    assert "project_root" in sig.parameters
    assert "enforcement_mode" in sig.parameters


def test_governance_agent_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.GovernanceAgent, SovereignBaseAgent)


def test_heal_with_unknown_violation_returns_dict(mod):
    """Module-level heal() must return a dict for any input shape (defensive)."""
    result = mod.heal({"type": "noop"})
    assert isinstance(result, dict)
