"""ADG-driven tests for apps_lic/reasoning/HOP5GenerationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.HOP5GenerationAgent  # noqa: F401


def test_module_importable():
    """Module HOP5GenerationAgent must be importable."""
    assert apps_lic.reasoning.HOP5GenerationAgent is not None
