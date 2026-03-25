"""ADG-driven tests for agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.hardened_anti_pattern_visitor  # noqa: F401


def test_module_importable():
    """Module hardened_anti_pattern_visitor must be importable."""
    assert agentic_core.L0_routing.scripts.hardened_anti_pattern_visitor is not None
