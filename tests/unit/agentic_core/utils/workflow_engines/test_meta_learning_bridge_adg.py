"""ADG-driven tests for agentic_core/utils/workflow_engines/meta_learning_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.meta_learning_bridge  # noqa: F401


def test_module_importable():
    """Module meta_learning_bridge must be importable."""
    assert agentic_core.utils.workflow_engines.meta_learning_bridge is not None
