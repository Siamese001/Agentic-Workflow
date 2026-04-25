"""Smoke tests for shadow_routing_wiring — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.shadow_routing_wiring")


def test_module_imports_clean():
    assert mod is not None


def test_ShadowRouterClassifier_present():
    assert hasattr(mod, "ShadowRouterClassifier")
    assert isinstance(mod.ShadowRouterClassifier, type)


def test_get_shadow_wiring_callable():
    assert callable(mod.get_shadow_wiring)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
