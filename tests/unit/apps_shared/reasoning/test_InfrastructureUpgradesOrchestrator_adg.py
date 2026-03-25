"""ADG-driven tests for apps_shared/reasoning/InfrastructureUpgradesOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.reasoning.InfrastructureUpgradesOrchestrator  # noqa: F401


def test_module_importable():
    """Module InfrastructureUpgradesOrchestrator must be importable."""
    assert apps_shared.reasoning.InfrastructureUpgradesOrchestrator is not None
