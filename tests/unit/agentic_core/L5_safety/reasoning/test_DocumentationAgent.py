"""Smoke tests for DocumentationAgent — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.DocumentationAgent")


def test_module_imports_clean():
    assert mod is not None


def test_DocumentationAgent_class_present():
    assert hasattr(mod, "DocumentationAgent")
    assert isinstance(mod.DocumentationAgent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
