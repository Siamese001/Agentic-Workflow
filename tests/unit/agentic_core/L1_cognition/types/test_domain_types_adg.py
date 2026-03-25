"""ADG contract tests for agentic_core/L1_cognition/types/domain_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L1_cognition.types.domain_types  # noqa: F401


def test_module_importable():
    """Module domain_types must be importable."""
    assert agentic_core.L1_cognition.types.domain_types is not None
