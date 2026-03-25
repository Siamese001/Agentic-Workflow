"""ADG-driven tests for agentic_core/L4_state/engines/readonly_retrieval_orchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.engines.readonly_retrieval_orchestrator  # noqa: F401


def test_module_importable():
    """Module readonly_retrieval_orchestrator must be importable."""
    assert agentic_core.L4_state.engines.readonly_retrieval_orchestrator is not None
