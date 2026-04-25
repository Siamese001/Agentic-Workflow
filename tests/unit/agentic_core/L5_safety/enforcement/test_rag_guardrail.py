"""Smoke tests for rag_guardrail — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.rag_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_ExternalKnowledgeAccessViolation_present():
    assert hasattr(mod, "ExternalKnowledgeAccessViolation")
    assert isinstance(mod.ExternalKnowledgeAccessViolation, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
