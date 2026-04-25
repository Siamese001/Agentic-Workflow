"""Smoke tests for pre_deploy_check_util — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.pre_deploy_check_util")


def test_module_imports_clean():
    assert mod is not None


def test_safe_execute_callable():
    assert callable(mod.safe_execute)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
