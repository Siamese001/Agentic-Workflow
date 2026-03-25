"""ADG-driven tests for apps_lic/utils/PIISanitizerSpecialistAgent_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.utils.PIISanitizerSpecialistAgent_util  # noqa: F401


def test_module_importable():
    """Module PIISanitizerSpecialistAgent_util must be importable."""
    assert apps_lic.utils.PIISanitizerSpecialistAgent_util is not None
