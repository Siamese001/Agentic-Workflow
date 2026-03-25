"""ADG-driven tests for agentic_core/L4_state/enforcement/embedding_sovereignty_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.enforcement.embedding_sovereignty_guard  # noqa: F401


def test_module_importable():
    """Module embedding_sovereignty_guard must be importable."""
    assert agentic_core.L4_state.enforcement.embedding_sovereignty_guard is not None
