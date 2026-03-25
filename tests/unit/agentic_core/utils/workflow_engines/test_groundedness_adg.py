"""ADG-driven tests for agentic_core/utils/workflow_engines/groundedness.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.groundedness  # noqa: F401


def test_module_importable():
    """Module groundedness must be importable."""
    assert agentic_core.utils.workflow_engines.groundedness is not None
