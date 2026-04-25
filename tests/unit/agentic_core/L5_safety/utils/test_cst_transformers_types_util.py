"""Smoke tests for cst_transformers_types_util — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.utils.cst_transformers_types_util",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_BareExceptTarget_class_present():
    assert hasattr(mod, "BareExceptTarget")
    assert isinstance(mod.BareExceptTarget, type)


def test_create_bare_except_fixer_callable():
    assert callable(mod.create_bare_except_fixer)
