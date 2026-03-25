"""ADG-driven tests for L0_routing/types/artifact_typed_compat_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.types.artifact_typed_compat_types  # noqa: F401


def test_module_importable():
    """Module artifact_typed_compat_types must be importable."""
    assert agentic_core.L0_routing.types.artifact_typed_compat_types is not None
