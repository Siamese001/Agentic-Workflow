"""ADG-driven tests for agentic_core/utils/workflow_engines/fusion.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.fusion  # noqa: F401


def test_module_importable():
    """Module fusion must be importable."""
    assert agentic_core.utils.workflow_engines.fusion is not None
