"""Smoke tests for the canonical code janitor utility."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_janitor_util")


def test_module_imports_clean():
    assert mod is not None


def test_code_janitor_class_present():
    assert hasattr(mod, "CodeJanitor")
    assert isinstance(mod.CodeJanitor, type)


def test_code_janitor_exposes_validate_all():
    assert callable(getattr(mod.CodeJanitor, "validate_all", None))


def test_module_has_heal_repository_compatibility_entrypoint():
    assert callable(getattr(mod, "heal_repository", None))
