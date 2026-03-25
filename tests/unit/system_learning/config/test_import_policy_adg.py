"""ADG-driven tests for system_learning/config/import_policy.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.config.import_policy  # noqa: F401


def test_module_importable():
    """Module import_policy must be importable."""
    assert system_learning.config.import_policy is not None
