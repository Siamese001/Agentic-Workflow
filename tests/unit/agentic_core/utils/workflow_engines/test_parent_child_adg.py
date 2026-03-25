"""ADG-driven tests for agentic_core/utils/workflow_engines/parent_child.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.parent_child  # noqa: F401


def test_module_importable():
    """Module parent_child must be importable."""
    assert agentic_core.utils.workflow_engines.parent_child is not None
