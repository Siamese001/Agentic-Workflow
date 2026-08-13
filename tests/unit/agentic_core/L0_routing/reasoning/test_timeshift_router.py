"""Smoke tests for timeshift_router — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.timeshift_router")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0


def test_routing_config_is_explicit_and_missing_config_fails_closed():
    with pytest.raises(ValueError, match="routing_config is required"):
        mod.evaluate_timeshift_routing(execution_start_tick=1)
