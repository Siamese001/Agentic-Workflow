"""ADG contract tests for agentic_core/L1_cognition/types/validation_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L1_cognition.types.validation_types  # noqa: F401


def test_module_importable():
    """Module validation_types must be importable."""
    assert agentic_core.L1_cognition.types.validation_types is not None
