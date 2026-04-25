"""Smoke tests for code_tool_runner_core_util — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_tool_runner_core_util")


def test_module_imports_clean():
    assert mod is not None


def test_CodeToolRunnerCapability_class_present():
    assert hasattr(mod, "CodeToolRunnerCapability")
    assert isinstance(mod.CodeToolRunnerCapability, type)


def test_CodeToolRunnerMixin_class_present():
    assert hasattr(mod, "CodeToolRunnerMixin")
    assert isinstance(mod.CodeToolRunnerMixin, type)
