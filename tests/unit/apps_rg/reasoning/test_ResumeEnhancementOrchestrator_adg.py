"""ADG-driven tests for apps_rg/reasoning/ResumeEnhancementOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.reasoning.ResumeEnhancementOrchestrator  # noqa: F401


def test_module_importable():
    """Module ResumeEnhancementOrchestrator must be importable."""
    assert apps_rg.reasoning.ResumeEnhancementOrchestrator is not None
