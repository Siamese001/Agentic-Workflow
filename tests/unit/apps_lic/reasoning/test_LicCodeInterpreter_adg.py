"""ADG-driven tests for apps_lic/reasoning/LicCodeInterpreter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.LicCodeInterpreter  # noqa: F401


def test_module_importable():
    """Module LicCodeInterpreter must be importable."""
    assert apps_lic.reasoning.LicCodeInterpreter is not None
