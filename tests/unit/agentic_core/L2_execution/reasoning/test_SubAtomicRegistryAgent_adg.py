"""ADG-driven tests for agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.reasoning.SubAtomicRegistryAgent  # noqa: F401


def test_module_importable():
    """Module SubAtomicRegistryAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.SubAtomicRegistryAgent is not None
