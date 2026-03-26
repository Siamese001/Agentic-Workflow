"""ADG-driven tests for system_learning/enforcement/dual_injection_proposal_gate.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module dual_injection_proposal_gate must be importable."""
    import system_learning.enforcement.dual_injection_proposal_gate  # noqa: F401

    assert system_learning.enforcement.dual_injection_proposal_gate is not None