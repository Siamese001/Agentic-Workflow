"""Smoke tests for anthropic_stub judge backend — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.eval_spine.judge_backends.anthropic_stub")


def test_module_imports_clean():
    assert mod is not None


def test_AnthropicBackend_in_all():
    assert "AnthropicBackend" in mod.__all__


def test_AnthropicBackend_class_present():
    assert hasattr(mod, "AnthropicBackend")
    assert isinstance(mod.AnthropicBackend, type)


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"
