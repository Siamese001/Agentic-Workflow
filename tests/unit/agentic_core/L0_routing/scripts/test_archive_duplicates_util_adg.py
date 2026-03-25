"""ADG-driven tests for agentic_core/L0_routing/scripts/archive_duplicates_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.archive_duplicates_util  # noqa: F401


def test_module_importable():
    """Module archive_duplicates_util must be importable."""
    assert agentic_core.L0_routing.scripts.archive_duplicates_util is not None
