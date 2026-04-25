"""Smoke tests for learning_seam — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.utils.learning_seam")


def test_module_imports_clean():
    assert mod is not None


def test_LearningArtifactIntent_present():
    assert hasattr(mod, "LearningArtifactIntent")
    assert isinstance(mod.LearningArtifactIntent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
