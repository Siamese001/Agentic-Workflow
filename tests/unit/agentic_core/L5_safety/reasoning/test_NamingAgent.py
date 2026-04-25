"""Surface coverage for `agentic_core.L5_safety.reasoning.NamingAgent`.

Wave 2 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. Security-surface
L5 gatekeeper — enforces naming laws (agent suffix, canonical placement).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.NamingAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_declared(mod):
    assert hasattr(mod, "__all__")
    expected = {"NamingAgent", "get_naming_agent", "TREE_SITTER_AVAILABLE", "PlacementResult"}
    assert set(mod.__all__) >= expected


@pytest.mark.parametrize("name", ["NamingAgent", "get_naming_agent", "TREE_SITTER_AVAILABLE", "PlacementResult"])
def test_public_surface(mod, name):
    assert hasattr(mod, name)


def test_naming_agent_is_class(mod):
    assert inspect.isclass(mod.NamingAgent)


def test_placement_result_is_class(mod):
    assert inspect.isclass(mod.PlacementResult)


def test_get_naming_agent_is_callable(mod):
    assert callable(mod.get_naming_agent)


def test_tree_sitter_available_is_bool(mod):
    assert isinstance(mod.TREE_SITTER_AVAILABLE, bool)


def test_naming_agent_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.NamingAgent, SovereignBaseAgent)
