"""Smoke tests for null judge backend — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.eval_spine.judge_backends.null")


def test_module_imports_clean():
    assert mod is not None


def test_NullBackend_in_all():
    assert "NullBackend" in mod.__all__


def test_NullBackend_class_present():
    assert hasattr(mod, "NullBackend")
    assert isinstance(mod.NullBackend, type)


def test_NullBackend_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"
