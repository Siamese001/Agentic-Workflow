"""Foundational behavioral tests for agentic_core/mixins/atomic_execution_mixin.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.mixins.atomic_execution_mixin  # noqa: F401


def test_module_importable():
    """Module atomic_execution_mixin must be importable."""
    assert agentic_core.mixins.atomic_execution_mixin is not None
