"""ADG importability contract for agentic_core/L4_state/storage/persistent_store.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.storage.persistent_store  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.storage.persistent_store  # noqa: F401
    """Module persistent_store must be importable."""
    assert agentic_core.L4_state.storage.persistent_store is not None
