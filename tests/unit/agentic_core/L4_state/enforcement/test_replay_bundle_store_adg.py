"""ADG importability contract for agentic_core/L4_state/enforcement/replay_bundle_store.py."""
from __future__ import annotations

import agentic_core.L4_state.enforcement.replay_bundle_store  # noqa: F401


def test_module_importable():
    """Module replay_bundle_store must be importable."""
    assert agentic_core.L4_state.enforcement.replay_bundle_store is not None
