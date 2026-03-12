"""ADG-driven tests for L0_routing/engines/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L0_routing.engines
    assert agentic_core.L0_routing.engines is not None


def test_is_package():
    import agentic_core.L0_routing.engines
    assert hasattr(agentic_core.L0_routing.engines, "__path__")
