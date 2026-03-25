"""ADG-driven tests for agentic_core/interfaces/embeddings.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.embeddings  # noqa: F401


def test_module_importable():
    """Module embeddings must be importable."""
    assert agentic_core.interfaces.embeddings is not None
