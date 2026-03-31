"""ADG-driven tests for apps_rg/validators/validation_gate_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module validation_gate_validator must be importable."""
    import apps_rg.validators.validation_gate_validator  # noqa: F401

    assert apps_rg.validators.validation_gate_validator is not None
