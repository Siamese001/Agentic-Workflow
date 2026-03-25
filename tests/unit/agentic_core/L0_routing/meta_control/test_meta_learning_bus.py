"""Foundational behavioral tests for agentic_core/L0_routing/meta_control/meta_learning_bus.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.meta_control.meta_learning_bus  # noqa: F401


def test_module_importable():
    """Module meta_learning_bus must be importable."""
    assert agentic_core.L0_routing.meta_control.meta_learning_bus is not None
