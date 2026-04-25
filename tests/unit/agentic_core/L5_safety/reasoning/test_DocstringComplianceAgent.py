"""Smoke tests for DocstringComplianceAgent — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.DocstringComplianceAgent")


def test_module_imports_clean():
    assert mod is not None


def test_DocstringComplianceAgent_class_present():
    assert hasattr(mod, "DocstringComplianceAgent")
    assert isinstance(mod.DocstringComplianceAgent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
