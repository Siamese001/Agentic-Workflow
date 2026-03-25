"""ADG-driven tests for agentic_core/L5_safety/validators/ddd_alignment_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.validators.ddd_alignment_validator  # noqa: F401


def test_module_importable():
    """Module ddd_alignment_validator must be importable."""
    assert agentic_core.L5_safety.validators.ddd_alignment_validator is not None
