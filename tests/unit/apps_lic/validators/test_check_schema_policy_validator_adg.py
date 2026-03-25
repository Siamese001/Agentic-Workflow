"""ADG-driven tests for apps_lic/validators/check_schema_policy_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.validators.check_schema_policy_validator as _mod  # noqa: F401


def test_module_importable():
    """Module check_schema_policy_validator must be importable."""
    assert _mod is not None
