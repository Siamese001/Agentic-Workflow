"""ADG-driven tests for L0_routing/utils/__init__.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L0_routing.utils
    assert agentic_core.L0_routing.utils is not None


def test_is_package():
    import agentic_core.L0_routing.utils
    assert hasattr(agentic_core.L0_routing.utils, "__path__")
