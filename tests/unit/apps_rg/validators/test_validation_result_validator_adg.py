"""ADG-driven tests for apps_rg/validators/validation_result_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module validation_result_validator must be importable."""
    import apps_rg.validators.validation_result_validator  # noqa: F401

    assert apps_rg.validators.validation_result_validator is not None