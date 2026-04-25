"""Smoke tests for human_review_queue — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.audit.human_review_queue")


def test_module_imports_clean():
    assert mod is not None


def test_PendingVerdict_class_present():
    assert hasattr(mod, "PendingVerdict")
    assert isinstance(mod.PendingVerdict, type)


def test_get_review_queue_callable():
    assert callable(mod.get_review_queue)
