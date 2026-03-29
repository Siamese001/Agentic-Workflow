"""ADG-driven tests for apps_lic/validators/safety_validate_ethical_standards_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module safety_validate_ethical_standards_validator must be importable."""
    import apps_lic.validators.safety_validate_ethical_standards_validator  # noqa: F401

    assert apps_lic.validators.safety_validate_ethical_standards_validator is not None