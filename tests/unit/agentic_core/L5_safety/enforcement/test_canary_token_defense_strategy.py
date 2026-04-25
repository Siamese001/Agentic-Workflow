"""Smoke tests for canary_token_defense_strategy — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.canary_token_defense_strategy")


def test_module_imports_clean():
    assert mod is not None


def test_CanaryToken_present():
    assert hasattr(mod, "CanaryToken")
    assert isinstance(mod.CanaryToken, type)


def test_scan_untrusted_text_callable():
    assert callable(mod.scan_untrusted_text)
