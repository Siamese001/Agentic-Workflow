"""Surface coverage for `agentic_core.L5_safety.reasoning.hierarchy_healer`.

Wave 3 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L5 write-surface
orchestrator — heals file hierarchy violations. Fan-out=12.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.hierarchy_healer"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_hierarchy_healer_class_present(mod):
    assert hasattr(mod, "HierarchyHealerAgent")
    assert inspect.isclass(mod.HierarchyHealerAgent)


def test_get_hierarchy_agent_callable(mod):
    assert hasattr(mod, "get_hierarchy_agent")
    assert callable(mod.get_hierarchy_agent)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.HierarchyHealerAgent, SovereignBaseAgent)


def test_get_hierarchy_agent_signature_accepts_project_root(mod):
    sig = inspect.signature(mod.get_hierarchy_agent)
    assert "project_root" in sig.parameters
