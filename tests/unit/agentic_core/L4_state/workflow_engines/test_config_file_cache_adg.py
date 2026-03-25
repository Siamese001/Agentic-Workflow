"""ADG-driven tests for agentic_core/L4_state/workflow_engines/config_file_cache.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.workflow_engines.config_file_cache  # noqa: F401


def test_module_importable():
    """Module config_file_cache must be importable."""
    assert agentic_core.L4_state.workflow_engines.config_file_cache is not None
