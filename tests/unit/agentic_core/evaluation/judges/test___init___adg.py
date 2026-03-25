"""ADG-driven tests for agentic_core/evaluation/judges/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.evaluation.judges.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module judges must be importable."""
    assert _mod is not None
