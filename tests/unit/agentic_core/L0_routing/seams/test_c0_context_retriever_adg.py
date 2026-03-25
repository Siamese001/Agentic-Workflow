"""ADG-driven tests for agentic_core/L0_routing/seams/c0_context_retriever.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.seams.c0_context_retriever  # noqa: F401


def test_module_importable():
    """Module c0_context_retriever must be importable."""
    assert agentic_core.L0_routing.seams.c0_context_retriever is not None
