"""ADG-driven tests for L0_routing/reasoning/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
        import agentic_core.L0_routing.reasoning
        import agentic_core.L0_routing.reasoning
        import agentic_core.L0_routing.reasoning
    #  # MOVED: import agentic_core.L0_routing.reasoning
        assert agentic_core.L0_routing.reasoning is not None

    assert agentic_core.L0_routing.reasoning is not None


def test_is_package():
#  # MOVED: import agentic_core.L0_routing.reasoning
    assert hasattr(agentic_core.L0_routing.reasoning, "__path__")
