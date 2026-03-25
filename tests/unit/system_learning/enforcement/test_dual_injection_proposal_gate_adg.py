"""ADG-driven tests for system_learning/enforcement/dual_injection_proposal_gate.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.enforcement.dual_injection_proposal_gate  # noqa: F401


def test_module_importable():
    """Module dual_injection_proposal_gate must be importable."""
    assert system_learning.enforcement.dual_injection_proposal_gate is not None
