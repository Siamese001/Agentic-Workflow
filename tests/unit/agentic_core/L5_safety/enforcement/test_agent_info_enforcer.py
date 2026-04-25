"""Smoke tests for agent_info_enforcer — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.agent_info_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_AgentInfo_present():
    assert hasattr(mod, "AgentInfo")
    assert isinstance(mod.AgentInfo, type)


def test_extract_layer_callable():
    assert callable(mod.extract_layer)
