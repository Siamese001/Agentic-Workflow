"""ADG importability contract for agentic_core/L4_state/memory/blob_storage_provider.py."""
from __future__ import annotations

import agentic_core.L4_state.memory.blob_storage_provider  # noqa: F401


def test_module_importable():
    """Module blob_storage_provider must be importable."""
    assert agentic_core.L4_state.memory.blob_storage_provider is not None
