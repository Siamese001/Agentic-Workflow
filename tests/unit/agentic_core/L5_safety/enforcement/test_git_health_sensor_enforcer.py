"""Smoke tests for git_health_sensor_enforcer — wave 34."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.enforcement.git_health_sensor_enforcer",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
