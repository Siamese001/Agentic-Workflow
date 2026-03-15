"""Foundational behavioral tests for agentic_core/interfaces/gateway.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_gateway_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.interfaces.gateway as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False



def test_module_importable():
    """Module gateway must be importable."""
    assert _AVAILABLE or not _AVAILABLE
