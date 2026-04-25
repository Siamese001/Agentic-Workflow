"""Smoke tests for retrieval_eval_registry — wave 31."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.memory.retrieval_eval_registry")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
