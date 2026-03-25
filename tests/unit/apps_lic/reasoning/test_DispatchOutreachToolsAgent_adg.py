"""ADG-driven tests for apps_lic/reasoning/DispatchOutreachToolsAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.DispatchOutreachToolsAgent  # noqa: F401


def test_module_importable():
    """Module DispatchOutreachToolsAgent must be importable."""
    assert apps_lic.reasoning.DispatchOutreachToolsAgent is not None
