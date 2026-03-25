"""ADG-driven tests for apps_lic/validators/MessageDiversityValidator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.validators.MessageDiversityValidator  # noqa: F401


def test_module_importable():
    """Module MessageDiversityValidator must be importable."""
    assert apps_lic.validators.MessageDiversityValidator is not None
