"""ADG-driven tests for apps_rg/reasoning/HardenedopenaiexecutorStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module HardenedopenaiexecutorStrategy must be importable."""
    import apps_rg.reasoning.HardenedopenaiexecutorStrategy  # noqa: F401

    assert apps_rg.reasoning.HardenedopenaiexecutorStrategy is not None