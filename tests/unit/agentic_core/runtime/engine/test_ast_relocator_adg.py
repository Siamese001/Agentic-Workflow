"""ADG-driven tests for agentic_core/runtime/engine/ast_relocator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.engine.ast_relocator  # noqa: F401


def test_module_importable():
    """Module ast_relocator must be importable."""
    assert agentic_core.runtime.engine.ast_relocator is not None
