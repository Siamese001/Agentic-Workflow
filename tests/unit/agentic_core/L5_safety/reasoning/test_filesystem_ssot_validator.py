"""Smoke tests for filesystem_ssot_validator — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.filesystem_ssot_validator")


def test_module_imports_clean():
    assert mod is not None


def test_FilesystemSSOTValidatorAgent_class_present():
    assert hasattr(mod, "FilesystemSSOTValidatorAgent")
    assert isinstance(mod.FilesystemSSOTValidatorAgent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
