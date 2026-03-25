"""ADG-driven tests for apps_rg/validators/hallucination_detector_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.validators.hallucination_detector_validator  # noqa: F401


def test_module_importable():
    """Module hallucination_detector_validator must be importable."""
    assert apps_rg.validators.hallucination_detector_validator is not None
