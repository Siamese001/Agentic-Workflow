"""Smoke tests for CredentialScannerAgent — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.CredentialScannerAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_CredentialScannerAgent_class_present():
    assert hasattr(mod, "CredentialScannerAgent")
    assert isinstance(mod.CredentialScannerAgent, type)
