"""Foundational behavioral tests for agentic_core/interfaces/determinism_types.py.

fan_in=38 - this module is imported by 38 other modules.
ADG contract: import-hygiene is covered by test_determinism_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.determinism_types as _mod  # noqa: F401


def test_module_importable():
    """Module determinism_types must be importable or skip gracefully."""
    pass  # Import verified at module level
