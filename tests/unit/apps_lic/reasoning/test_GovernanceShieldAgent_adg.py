"""ADG-driven tests for apps_lic/reasoning/GovernanceShieldAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module GovernanceShieldAgent must be importable."""
    import apps_lic.reasoning.GovernanceShieldAgent  # noqa: F401

    assert apps_lic.reasoning.GovernanceShieldAgent is not None
