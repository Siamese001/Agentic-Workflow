"""Smoke tests for bootstrap_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.bootstrap_util")


def test_module_imports_clean():
    assert mod is not None


def test_BootstrapResult_present():
    assert hasattr(mod, "BootstrapResult")
    assert isinstance(mod.BootstrapResult, type)


def test_verify_redis_connection_callable():
    assert callable(mod.verify_redis_connection)
