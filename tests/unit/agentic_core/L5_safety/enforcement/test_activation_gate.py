"""Smoke tests for activation_gate — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.activation_gate")


def test_module_imports_clean():
    assert mod is not None


def test_assert_activation_allowed_callable():
    assert callable(mod.assert_activation_allowed)
