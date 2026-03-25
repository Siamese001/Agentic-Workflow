"""ADG-driven tests for apps_shared/utils/assessment_level_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.assessment_level_util  # noqa: F401


def test_module_importable():
    """Module assessment_level_util must be importable."""
    assert apps_shared.utils.assessment_level_util is not None
