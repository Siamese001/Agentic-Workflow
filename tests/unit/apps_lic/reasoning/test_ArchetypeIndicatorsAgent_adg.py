"""ADG-driven tests for apps_lic/reasoning/ArchetypeIndicatorsAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.ArchetypeIndicatorsAgent  # noqa: F401


def test_module_importable():
    """Module ArchetypeIndicatorsAgent must be importable."""
    assert apps_lic.reasoning.ArchetypeIndicatorsAgent is not None
