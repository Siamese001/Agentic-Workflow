"""ADG-driven tests for apps_lic/reasoning/MessageComplianceAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.MessageComplianceAgent  # noqa: F401


def test_module_importable():
    """Module MessageComplianceAgent must be importable."""
    assert apps_lic.reasoning.MessageComplianceAgent is not None
