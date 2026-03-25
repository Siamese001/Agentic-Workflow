"""ADG-driven tests for agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.ConstitutionalReviewerAgent  # noqa: F401


def test_module_importable():
    """Module ConstitutionalReviewerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.ConstitutionalReviewerAgent is not None
