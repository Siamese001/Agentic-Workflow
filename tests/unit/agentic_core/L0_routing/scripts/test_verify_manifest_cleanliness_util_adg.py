"""ADG-driven tests for agentic_core/L0_routing/scripts/verify_manifest_cleanliness_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.verify_manifest_cleanliness_util  # noqa: F401


def test_module_importable():
    """Module verify_manifest_cleanliness_util must be importable."""
    assert agentic_core.L0_routing.scripts.verify_manifest_cleanliness_util is not None
