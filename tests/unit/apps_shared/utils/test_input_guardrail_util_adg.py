"""ADG-driven tests for apps_shared/utils/input_guardrail_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.input_guardrail_util  # noqa: F401


def test_module_importable():
    """Module input_guardrail_util must be importable."""
    assert apps_shared.utils.input_guardrail_util is not None
