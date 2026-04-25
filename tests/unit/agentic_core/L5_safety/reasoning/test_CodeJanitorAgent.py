"""Smoke tests for CodeJanitorAgent — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.CodeJanitorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_CodeJanitorAgent_class_present():
    assert hasattr(mod, "CodeJanitorAgent")
    assert isinstance(mod.CodeJanitorAgent, type)


def test_CodeJanitorAgent_has_heal_repository():
    assert callable(getattr(mod.CodeJanitorAgent, "heal_repository", None))
