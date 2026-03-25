"""ADG-driven tests for L2_execution/types/vm_status_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.vm_status_types  # noqa: F401


def test_module_importable():
    """Module vm_status_types must be importable."""
    assert agentic_core.L2_execution.types.vm_status_types is not None
