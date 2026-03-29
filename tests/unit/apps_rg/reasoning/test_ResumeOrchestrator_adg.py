"""ADG-driven tests for apps_rg/reasoning/ResumeOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module ResumeOrchestrator must be importable."""
    import apps_rg.reasoning.ResumeOrchestrator  # noqa: F401

    assert apps_rg.reasoning.ResumeOrchestrator is not None