"""Smoke tests for PascalSovereigntyAgent — wave 29."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.validators.PascalSovereigntyAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_PascalSovereigntyAgent_class_present():
    assert hasattr(mod, "PascalSovereigntyAgent")
    assert isinstance(mod.PascalSovereigntyAgent, type)


def test_main_callable():
    assert callable(mod.main)
