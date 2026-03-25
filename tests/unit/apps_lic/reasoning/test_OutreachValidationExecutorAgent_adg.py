"""ADG-driven tests for apps_lic/reasoning/OutreachValidationExecutorAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.OutreachValidationExecutorAgent  # noqa: F401


def test_module_importable():
    """Module OutreachValidationExecutorAgent must be importable."""
    assert apps_lic.reasoning.OutreachValidationExecutorAgent is not None
