"""ADG-driven tests for L0_routing/types/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
        import agentic_core.L0_routing.types
        import agentic_core.L0_routing.types
        import agentic_core.L0_routing.types
    #  # MOVED: import agentic_core.L0_routing.types
        assert agentic_core.L0_routing.types is not None

    assert agentic_core.L0_routing.types is not None


def test_is_package():
#  # MOVED: import agentic_core.L0_routing.types
    assert hasattr(agentic_core.L0_routing.types, "__path__")
