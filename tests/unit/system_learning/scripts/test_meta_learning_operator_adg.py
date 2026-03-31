"""ADG-driven tests for system_learning/scripts/meta_learning_operator.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module meta_learning_operator must be importable."""
    import system_learning.scripts.meta_learning_operator
    assert system_learning.scripts.meta_learning_operator is not None
