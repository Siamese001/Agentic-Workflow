"""ADG-driven tests for apps_lic/validators/PersonaPlannerValidator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.validators.PersonaPlannerValidator  # noqa: F401


def test_module_importable():
    """Module PersonaPlannerValidator must be importable."""
    assert apps_lic.validators.PersonaPlannerValidator is not None
