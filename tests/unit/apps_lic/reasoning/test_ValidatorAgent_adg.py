"""ADG-driven tests for apps_lic/reasoning/ValidatorAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.ValidatorAgent  # noqa: F401


def test_module_importable():
    """Module ValidatorAgent must be importable."""
    assert apps_lic.reasoning.ValidatorAgent is not None
