"""ADG-driven tests for apps_lic/reasoning/HOP8QAReportAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module HOP8QAReportAgent must be importable."""
    import apps_lic.reasoning.HOP8QAReportAgent  # noqa: F401

    assert apps_lic.reasoning.HOP8QAReportAgent is not None
