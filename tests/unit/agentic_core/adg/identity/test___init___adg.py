"""ADG-driven tests for agentic_core/adg/identity/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.identity.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module identity must be importable."""
    assert _mod is not None
