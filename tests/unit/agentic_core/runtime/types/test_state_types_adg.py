"""ADG contract tests for runtime/types/state_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.types.state_types  # noqa: F401


def test_module_importable():
    """Module state_types must be importable."""
    assert agentic_core.runtime.types.state_types is not None
