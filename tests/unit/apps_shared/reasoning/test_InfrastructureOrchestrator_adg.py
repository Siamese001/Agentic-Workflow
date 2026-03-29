"""ADG-driven tests for apps_shared/reasoning/InfrastructureOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module InfrastructureOrchestrator must be importable."""
    import apps_shared.reasoning.InfrastructureOrchestrator  # noqa: F401

    assert apps_shared.reasoning.InfrastructureOrchestrator is not None