"""Smoke tests for code_enforcer_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_enforcer_util")


def test_module_imports_clean():
    assert mod is not None


def test_validate_file_callable():
    assert callable(mod.validate_file)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
