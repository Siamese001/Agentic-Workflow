"""Smoke tests for L5_safety __init__ — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety")


def test_module_imports_clean():
    assert mod is not None


def test_emit_guardrail_audit_callable():
    assert callable(mod.emit_guardrail_audit)


def test_DecisionContext_present():
    assert hasattr(mod, "DecisionContext")
