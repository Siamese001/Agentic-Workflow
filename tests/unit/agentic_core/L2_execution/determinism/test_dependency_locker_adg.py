"""ADG-driven tests for L2_execution/determinism/dependency_locker.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.determinism.dependency_locker  # noqa: F401


def test_module_importable():
    """Module dependency_locker must be importable."""
    assert agentic_core.L2_execution.determinism.dependency_locker is not None
