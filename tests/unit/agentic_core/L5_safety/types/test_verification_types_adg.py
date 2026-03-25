"""ADG contract tests for agentic_core/L5_safety/types/verification_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.types.verification_types  # noqa: F401


def test_module_importable():
    """Module verification_types must be importable."""
    assert agentic_core.L5_safety.types.verification_types is not None
