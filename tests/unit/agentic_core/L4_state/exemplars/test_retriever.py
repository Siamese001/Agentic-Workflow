"""Smoke tests for exemplars retriever — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.exemplars.retriever")


def test_module_imports_clean():
    assert mod is not None


def test_ExemplarBank_present():
    assert hasattr(mod, "ExemplarBank")
    assert isinstance(mod.ExemplarBank, type)


def test_select_top_k_callable():
    assert callable(mod.select_top_k)
