"""ADG-driven tests for apps_lic/reasoning/HOP7GateDecisionAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module HOP7GateDecisionAgent must be importable."""
    import apps_lic.reasoning.HOP7GateDecisionAgent  # noqa: F401

    assert apps_lic.reasoning.HOP7GateDecisionAgent is not None
