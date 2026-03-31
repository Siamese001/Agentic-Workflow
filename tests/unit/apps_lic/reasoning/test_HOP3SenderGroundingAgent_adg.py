"""ADG-driven tests for apps_lic/reasoning/HOP3SenderGroundingAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module HOP3SenderGroundingAgent must be importable."""
    import apps_lic.reasoning.HOP3SenderGroundingAgent  # noqa: F401

    assert apps_lic.reasoning.HOP3SenderGroundingAgent is not None
