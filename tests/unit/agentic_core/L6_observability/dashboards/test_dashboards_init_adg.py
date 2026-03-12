"""ADG-driven tests for L6_observability/dashboards/__init__.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L6_observability.dashboards
    assert agentic_core.L6_observability.dashboards is not None


def test_is_package():
    import agentic_core.L6_observability.dashboards
    assert hasattr(agentic_core.L6_observability.dashboards, "__path__")
