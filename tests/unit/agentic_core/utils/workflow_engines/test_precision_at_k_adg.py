"""ADG-driven tests for agentic_core/utils/workflow_engines/precision_at_k.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.precision_at_k  # noqa: F401


def test_module_importable():
    """Module precision_at_k must be importable."""
    assert agentic_core.utils.workflow_engines.precision_at_k is not None
