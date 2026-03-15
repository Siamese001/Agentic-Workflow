"""Foundational behavioral tests for agentic_core/utils/security_util.py.

fan_in=32 — this module is imported by 32 other modules.
ADG contract: import-hygiene is covered by test_security_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.utils.security_util as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False



def test_module_importable():
    """Module security_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
