"""ADG-driven tests for apps_shared/validators/check_depth_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.validators.check_depth_validator  # noqa: F401


def test_module_importable():
    """Module check_depth_validator must be importable."""
    assert apps_shared.validators.check_depth_validator is not None
