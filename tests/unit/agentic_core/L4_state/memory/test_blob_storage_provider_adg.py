"""ADG importability contract for agentic_core/L4_state/memory/blob_storage_provider.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.memory.blob_storage_provider  # noqa: F401


def test_module_importable():
        import agentic_core.L4_state.memory.blob_storage_provider  # noqa: F401
        """Module blob_storage_provider must be importable."""
        assert agentic_core.L4_state.memory.blob_storage_provider is not None

    assert agentic_core.L4_state.memory.blob_storage_provider is not None
