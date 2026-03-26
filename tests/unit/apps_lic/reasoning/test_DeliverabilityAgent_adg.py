"""ADG-driven tests for apps_lic/reasoning/DeliverabilityAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module DeliverabilityAgent must be importable."""
    import apps_lic.reasoning.DeliverabilityAgent  # noqa: F401

    assert apps_lic.reasoning.DeliverabilityAgent is not None
