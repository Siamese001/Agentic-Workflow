"""ADG-driven tests for agentic_core/L1_cognition/utils/profile_updater_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L1_cognition.utils.profile_updater_util  # noqa: F401


def test_module_importable():
    """Module profile_updater_util must be importable."""
    assert agentic_core.L1_cognition.utils.profile_updater_util is not None
