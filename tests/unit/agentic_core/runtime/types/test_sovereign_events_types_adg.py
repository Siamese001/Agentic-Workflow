"""ADG contract tests for runtime/types/sovereign_events_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.types.sovereign_events_types  # noqa: F401


def test_module_importable():
    """Module sovereign_events_types must be importable."""
    assert agentic_core.runtime.types.sovereign_events_types is not None
