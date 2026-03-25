"""ADG-driven tests for apps_rg/validators/regeneration_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.validators.regeneration_validator  # noqa: F401


def test_module_importable():
    """Module regeneration_validator must be importable."""
    assert apps_rg.validators.regeneration_validator is not None
