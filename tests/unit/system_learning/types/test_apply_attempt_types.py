"""Foundational behavioral tests for system_learning/types/apply_attempt_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.types.apply_attempt_types  # noqa: F401


def test_module_importable():
    """Module apply_attempt_types must be importable."""
    assert system_learning.types.apply_attempt_types is not None
