"""ADG-driven tests for apps_lic/reasoning/HOP3SenderGroundingAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.HOP3SenderGroundingAgent  # noqa: F401


def test_module_importable():
    """Module HOP3SenderGroundingAgent must be importable."""
    assert apps_lic.reasoning.HOP3SenderGroundingAgent is not None
