"""Smoke tests for tool_safety_gate — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.gates.tool_safety_gate")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_ToolRiskLevel_enum_present():
    assert hasattr(mod, "ToolRiskLevel")
    import enum

    assert issubclass(mod.ToolRiskLevel, enum.Enum)


def test_ToolSafetyGate_class_present():
    assert hasattr(mod, "ToolSafetyGate")
    assert isinstance(mod.ToolSafetyGate, type)


def test_ToolNotSandboxedError_is_exception():
    assert issubclass(mod.ToolNotSandboxedError, Exception)


def test_get_tool_safety_gate_callable():
    assert callable(mod.get_tool_safety_gate)


def test_reset_tool_safety_gate_callable():
    assert callable(mod.reset_tool_safety_gate)


def test_ToolInvocationRecord_present():
    assert hasattr(mod, "ToolInvocationRecord")


def test_singleton_reset_pattern():
    mod.reset_tool_safety_gate()
    gate = mod.get_tool_safety_gate()
    assert gate is not None
    gate2 = mod.get_tool_safety_gate()
    assert gate is gate2  # singleton
