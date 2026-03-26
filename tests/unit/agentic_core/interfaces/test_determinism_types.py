"""Foundational behavioral tests for agentic_core/interfaces/determinism_types.py.

fan_in=38 - this module is imported by 38 other modules.
ADG contract: import-hygiene is covered by test_determinism_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.interfaces.determinism_types as _mod  # noqa: F401


def test_module_importable():
        import agentic_core.interfaces.determinism_types as _mod  # noqa: F401
        """Module determinism_types must be importable or skip gracefully."""
        assert _mod.__name__ == "agentic_core.interfaces.determinism_types"

    assert _mod.__name__ == "agentic_core.interfaces.determinism_types"


def test_module_exposes_public_api():
    """determinism_types module exposes expected public symbols."""
    public_symbols = [n for n in dir(_mod) if not n.startswith("_")]
    assert len(public_symbols) >= 1, "determinism_types must expose at least one public symbol"
