"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/location_validator.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.location_validator  # noqa: F401


def test_module_importable():
    """Module location_validator must be importable."""
    assert agentic_core.L5_safety.reasoning.location_validator is not None
