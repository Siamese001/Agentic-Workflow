"""Foundational behavioral tests for system_learning/types/meta_learning_types.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module meta_learning_types must be importable."""
    import agentic_core.L6_system_learning.meta_learning_types

    assert system_learning.types.meta_learning_types is not None
