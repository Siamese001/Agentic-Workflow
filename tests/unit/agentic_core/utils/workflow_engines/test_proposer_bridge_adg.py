"""ADG-driven tests for agentic_core/utils/workflow_engines/proposer_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.proposer_bridge  # noqa: F401


def test_module_importable():
    """Module proposer_bridge must be importable."""
    assert agentic_core.utils.workflow_engines.proposer_bridge is not None
