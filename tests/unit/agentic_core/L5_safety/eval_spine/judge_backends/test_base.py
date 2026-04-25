"""Smoke tests for eval_spine judge_backends base — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.eval_spine.judge_backends.base")


def test_module_imports_clean():
    assert mod is not None


def test_JudgeBackend_callable():
    assert callable(mod.JudgeBackend)


def test_DimScorer_callable():
    assert callable(mod.DimScorer)
