"""ADG-driven tests for apps_lic/utils/mixins_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.utils.mixins_util  # noqa: F401


def test_module_importable():
    """Module mixins_util must be importable."""
    assert apps_lic.utils.mixins_util is not None
