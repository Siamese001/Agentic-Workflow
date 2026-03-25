"""ADG importability contract for agentic_core/L4_state/types/retrieval_anchor_types.py."""
from __future__ import annotations

import agentic_core.L4_state.types.retrieval_anchor_types  # noqa: F401


def test_module_importable():
    """Module retrieval_anchor_types must be importable."""
    assert agentic_core.L4_state.types.retrieval_anchor_types is not None
