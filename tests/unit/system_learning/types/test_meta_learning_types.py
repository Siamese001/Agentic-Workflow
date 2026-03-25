"""Foundational behavioral tests for system_learning/types/meta_learning_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.types.meta_learning_types  # noqa: F401


def test_module_importable():
    """Module meta_learning_types must be importable."""
    assert system_learning.types.meta_learning_types is not None
