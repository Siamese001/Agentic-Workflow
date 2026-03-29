"""ADG-driven tests for apps_lic/reasoning/MessageComplianceAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module MessageComplianceAgent must be importable."""
    import apps_lic.reasoning.MessageComplianceAgent  # noqa: F401

    assert apps_lic.reasoning.MessageComplianceAgent is not None