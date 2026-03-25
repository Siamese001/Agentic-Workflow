"""Foundational behavioral tests for system_learning/adapters/system_learning_memory_bridge.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.adapters.system_learning_memory_bridge  # noqa: F401


def test_module_importable():
    """Module system_learning_memory_bridge must be importable."""
    assert system_learning.adapters.system_learning_memory_bridge is not None
