"""Foundational behavioral tests for system_learning/types/app_signal_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

def test_module_importable():
    """Module app_signal_types must be importable."""
    import system_learning.types.app_signal_types
    assert system_learning.types.app_signal_types is not None
