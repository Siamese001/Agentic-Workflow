"""Smoke tests for DuplicateCodeDetectorAgent — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.DuplicateCodeDetectorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_DuplicateFile_class_present():
    assert hasattr(mod, "DuplicateFile")
    assert isinstance(mod.DuplicateFile, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_module_has_mixin_classes():
    assert hasattr(mod, "AtomicExecutionMixin") or hasattr(mod, "SubatomicTestingMixin")
