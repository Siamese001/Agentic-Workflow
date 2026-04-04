"""Foundational behavioral tests for system_learning/types/rollout_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

def test_module_importable():
    """Module rollout_types must be importable."""
    import system_learning.types.rollout_types
    assert system_learning.types.rollout_types is not None
