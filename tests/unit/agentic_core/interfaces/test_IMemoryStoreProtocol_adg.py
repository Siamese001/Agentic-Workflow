"""ADG-driven tests for agentic_core/interfaces/IMemoryStoreProtocol.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.IMemoryStoreProtocol  # noqa: F401


def test_module_importable():
    """Module IMemoryStoreProtocol must be importable."""
    assert agentic_core.interfaces.IMemoryStoreProtocol is not None
