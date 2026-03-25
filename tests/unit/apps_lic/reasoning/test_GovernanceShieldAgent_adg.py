"""ADG-driven tests for apps_lic/reasoning/GovernanceShieldAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.GovernanceShieldAgent  # noqa: F401


def test_module_importable():
    """Module GovernanceShieldAgent must be importable."""
    assert apps_lic.reasoning.GovernanceShieldAgent is not None
