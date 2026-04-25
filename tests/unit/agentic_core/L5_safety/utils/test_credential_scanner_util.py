"""Smoke tests for credential_scanner_util — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.credential_scanner_util")


def test_module_imports_clean():
    assert mod is not None


def test_CredentialMatch_class_present():
    assert hasattr(mod, "CredentialMatch")
    assert isinstance(mod.CredentialMatch, type)


def test_scan_for_credentials_callable():
    assert callable(mod.scan_for_credentials)
