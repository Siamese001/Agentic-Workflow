"""Foundational behavioral tests for agentic_core/interfaces/observability.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.observability  # noqa: F401


def test_module_importable():
    """Module observability must be importable."""
    assert agentic_core.interfaces.observability is not None
