"""Foundational behavioral tests for agentic_core/L2_execution/healers/healing_tier_config.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.healers.healing_tier_config  # noqa: F401


def test_module_importable():
    """Module healing_tier_config must be importable."""
    assert agentic_core.L2_execution.healers.healing_tier_config is not None
