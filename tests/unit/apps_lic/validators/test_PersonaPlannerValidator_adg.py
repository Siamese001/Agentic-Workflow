"""ADG-driven tests for apps_lic/validators/PersonaPlannerValidator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module PersonaPlannerValidator must be importable."""
    import apps_lic.validators.PersonaPlannerValidator  # noqa: F401

    assert apps_lic.validators.PersonaPlannerValidator is not None