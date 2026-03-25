"""ADG importability contract for agentic_core/L4_state/enforcement/citation_enforcement.py."""
from __future__ import annotations

import agentic_core.L4_state.enforcement.citation_enforcement  # noqa: F401


def test_module_importable():
    """Module citation_enforcement must be importable."""
    assert agentic_core.L4_state.enforcement.citation_enforcement is not None
