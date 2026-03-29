"""ADG-driven tests for apps_lic/reasoning/OutreachMessageAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module OutreachMessageAgent must be importable."""
    import apps_lic.reasoning.OutreachMessageAgent  # noqa: F401

    assert apps_lic.reasoning.OutreachMessageAgent is not None