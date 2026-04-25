"""Smoke tests for code_deduplication_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.code_deduplication_util")


def test_module_imports_clean():
    assert mod is not None


def test_DuplicateGroup_present():
    assert hasattr(mod, "DuplicateGroup")
    assert isinstance(mod.DuplicateGroup, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
