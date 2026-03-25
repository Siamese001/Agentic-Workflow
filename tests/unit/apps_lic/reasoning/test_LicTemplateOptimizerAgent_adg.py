"""ADG-driven tests for apps_lic/reasoning/LicTemplateOptimizerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.LicTemplateOptimizerAgent  # noqa: F401


def test_module_importable():
    """Module LicTemplateOptimizerAgent must be importable."""
    assert apps_lic.reasoning.LicTemplateOptimizerAgent is not None
