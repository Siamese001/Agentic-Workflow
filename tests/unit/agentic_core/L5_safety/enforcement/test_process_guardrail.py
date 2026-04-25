"""Smoke tests for process_guardrail — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.process_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_ProcessGuard_class_present():
    assert hasattr(mod, "ProcessGuard")
    assert isinstance(mod.ProcessGuard, type)


def test_SecurityViolation_is_exception():
    assert issubclass(mod.SecurityViolation, Exception)


def test_BLOCKED_COMMANDS_is_collection():
    assert hasattr(mod, "BLOCKED_COMMANDS")
    assert len(mod.BLOCKED_COMMANDS) > 0
