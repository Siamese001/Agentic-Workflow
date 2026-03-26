"""ADG-driven tests for L0_routing/meta_control/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L0_routing.meta_control
    import agentic_core.L0_routing.meta_control
#  # MOVED: import agentic_core.L0_routing.meta_control
    assert agentic_core.L0_routing.meta_control is not None


def test_is_package():
#  # MOVED: import agentic_core.L0_routing.meta_control
    assert hasattr(agentic_core.L0_routing.meta_control, "__path__")
