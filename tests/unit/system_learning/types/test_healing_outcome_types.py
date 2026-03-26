"""Foundational behavioral tests for system_learning/types/healing_outcome_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module healing_outcome_types must be importable."""
    import system_learning.types.healing_outcome_types  # noqa: F401

    assert system_learning.types.healing_outcome_types is not None