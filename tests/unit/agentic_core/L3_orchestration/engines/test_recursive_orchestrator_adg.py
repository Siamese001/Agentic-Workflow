"""ADG-driven tests for agentic_core/L3_orchestration/engines/recursive_orchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.recursive_orchestrator  # noqa: F401


def test_module_importable():
    """Module recursive_orchestrator must be importable."""
    assert agentic_core.L3_orchestration.engines.recursive_orchestrator is not None
