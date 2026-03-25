"""Foundational behavioral tests for agentic_core/interfaces/execution.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.execution  # noqa: F401


def test_module_importable():
    """Module execution must be importable."""
    assert agentic_core.interfaces.execution is not None
