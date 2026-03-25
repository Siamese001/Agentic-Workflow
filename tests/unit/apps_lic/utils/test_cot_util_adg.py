"""ADG-driven tests for apps_lic/utils/cot_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.utils.cot_util  # noqa: F401


def test_module_importable():
    """Module cot_util must be importable."""
    assert apps_lic.utils.cot_util is not None
