"""ADG-driven tests for apps_lic/validators/safety_validate_outreach_constraints_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.validators.safety_validate_outreach_constraints_validator  # noqa: F401


def test_module_importable():
    """Module safety_validate_outreach_constraints_validator must be importable."""
    assert apps_lic.validators.safety_validate_outreach_constraints_validator is not None
