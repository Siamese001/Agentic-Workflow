"""Smoke tests for vigilance_routing — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.vigilance_routing")


def test_module_imports_clean():
    assert mod is not None


def test_route_vigilance_event_callable():
    assert callable(mod.route_vigilance_event)


def test_get_vigilance_severity_callable():
    assert callable(mod.get_vigilance_severity)
