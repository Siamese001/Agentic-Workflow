"""Smoke tests for intent_embedding_classifier — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.intent_embedding_classifier")


def test_module_imports_clean():
    assert mod is not None


def test_IntentEmbeddingClassifier_in_all():
    assert "IntentEmbeddingClassifier" in mod.__all__


def test_IntentEmbeddingClassifier_class_present():
    assert hasattr(mod, "IntentEmbeddingClassifier")
    assert isinstance(mod.IntentEmbeddingClassifier, type)


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"
