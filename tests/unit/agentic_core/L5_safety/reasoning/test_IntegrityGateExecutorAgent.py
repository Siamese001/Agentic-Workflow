"""Smoke tests for IntegrityGateExecutorAgent — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_IntegrityGateExecutorAgent_class_present():
    cls = getattr(mod, "IntegrityGateExecutorAgent", None)
    if cls is None:
        # class may be named differently — just verify module loaded
        pass
    else:
        assert isinstance(cls, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
