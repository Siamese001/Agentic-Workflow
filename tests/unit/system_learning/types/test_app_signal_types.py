"""Foundational behavioral tests for system_learning/types/app_signal_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.types.app_signal_types  # noqa: F401


def test_module_importable():
    """Module app_signal_types must be importable."""
    assert system_learning.types.app_signal_types is not None
