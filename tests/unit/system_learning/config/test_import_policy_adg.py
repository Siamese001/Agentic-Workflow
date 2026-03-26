"""ADG-driven tests for system_learning/config/import_policy.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module import_policy must be importable."""
    import system_learning.config.import_policy  # noqa: F401

    assert system_learning.config.import_policy is not None
