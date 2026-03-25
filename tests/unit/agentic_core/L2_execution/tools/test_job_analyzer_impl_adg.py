"""ADG-driven tests for agentic_core/L2_execution/tools/job_analyzer_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.job_analyzer_impl  # noqa: F401


def test_module_importable():
    """Module job_analyzer_impl must be importable."""
    assert agentic_core.L2_execution.tools.job_analyzer_impl is not None
