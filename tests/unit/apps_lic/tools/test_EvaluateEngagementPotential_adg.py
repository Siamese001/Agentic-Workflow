"""ADG-driven tests for apps_lic/tools/EvaluateEngagementPotential.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module EvaluateEngagementPotential must be importable."""
    import apps_lic.tools.EvaluateEngagementPotential  # noqa: F401

    assert apps_lic.tools.EvaluateEngagementPotential is not None
