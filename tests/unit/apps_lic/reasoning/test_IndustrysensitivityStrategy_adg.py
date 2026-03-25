"""ADG-driven tests for apps_lic/reasoning/IndustrysensitivityStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.IndustrysensitivityStrategy  # noqa: F401


def test_module_importable():
    """Module IndustrysensitivityStrategy must be importable."""
    assert apps_lic.reasoning.IndustrysensitivityStrategy is not None
