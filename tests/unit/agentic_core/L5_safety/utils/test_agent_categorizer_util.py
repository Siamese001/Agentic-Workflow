"""Smoke tests for agent_categorizer_util — wave 28."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.agent_categorizer_util")


def test_module_imports_clean():
    assert mod is not None


def test_AgentCategorizer_class_present():
    assert hasattr(mod, "AgentCategorizer")
    assert isinstance(mod.AgentCategorizer, type)


def test_categorize_agents_for_dashboard_callable():
    assert callable(mod.categorize_agents_for_dashboard)
