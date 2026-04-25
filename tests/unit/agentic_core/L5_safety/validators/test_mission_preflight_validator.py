"""Smoke tests for mission_preflight_validator — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.mission_preflight_validator")


def test_module_imports_clean():
    assert mod is not None


def test_MissionPreflight_class_present():
    assert hasattr(mod, "MissionPreflight")
    assert isinstance(mod.MissionPreflight, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
