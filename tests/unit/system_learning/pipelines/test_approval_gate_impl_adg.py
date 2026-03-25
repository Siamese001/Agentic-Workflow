"""ADG-driven tests for system_learning/pipelines/approval_gate_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.pipelines.approval_gate_impl  # noqa: F401


def test_module_importable():
    """Module approval_gate_impl must be importable."""
    assert system_learning.pipelines.approval_gate_impl is not None
