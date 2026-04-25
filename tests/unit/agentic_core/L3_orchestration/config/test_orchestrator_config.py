"""Smoke tests for orchestrator_config — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.config.orchestrator_config")


def test_module_imports_clean():
    assert mod is not None


def test_OrchestratorConfig_class_present():
    assert hasattr(mod, "OrchestratorConfig")
    assert isinstance(mod.OrchestratorConfig, type)
