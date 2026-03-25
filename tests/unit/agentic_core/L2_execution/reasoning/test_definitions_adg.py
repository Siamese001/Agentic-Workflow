"""ADG-driven tests for L2_execution/reasoning/definitions.py — re-export shim."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.reasoning.definitions  # noqa: F401


def test_module_importable():
    """Module definitions must be importable."""
    assert agentic_core.L2_execution.reasoning.definitions is not None
