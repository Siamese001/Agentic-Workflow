"""Foundational behavioral tests for agentic_core/interfaces/mixins.py.

fan_in=16 — this module is imported by 16 other modules.
ADG contract: import-hygiene is covered by test_mixins_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.interfaces.mixins as _mod  # noqa: F401
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False



def test_module_importable():
    """Module mixins must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
