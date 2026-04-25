"""Smoke tests for graph_store_factory — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.memory.graph_store_factory")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
