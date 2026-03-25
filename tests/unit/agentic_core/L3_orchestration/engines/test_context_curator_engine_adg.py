"""ADG-driven tests for agentic_core/L3_orchestration/engines/context_curator_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.context_curator_engine  # noqa: F401


def test_module_importable():
    """Module context_curator_engine must be importable."""
    assert agentic_core.L3_orchestration.engines.context_curator_engine is not None
