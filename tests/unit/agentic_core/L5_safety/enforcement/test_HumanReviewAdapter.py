"""Smoke tests for HumanReviewAdapter — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.HumanReviewAdapter")


def test_module_imports_clean():
    assert mod is not None


def test_HumanReviewAdapter_class_present():
    assert hasattr(mod, "HumanReviewAdapter")
    assert isinstance(mod.HumanReviewAdapter, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
