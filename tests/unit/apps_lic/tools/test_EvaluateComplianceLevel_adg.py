"""ADG-driven tests for apps_lic/tools/EvaluateComplianceLevel.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.EvaluateComplianceLevel  # noqa: F401


def test_module_importable():
    """Module EvaluateComplianceLevel must be importable."""
    assert apps_lic.tools.EvaluateComplianceLevel is not None
