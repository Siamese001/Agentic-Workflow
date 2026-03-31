"""
L4 State — Retrieval Bridge Module

Provides L4StateRetrievalBridge for wiring L4 canonical state store
to the retrieval pipeline across all apps_* packages.
"""

from __future__ import annotations

from typing import Any

# L4 State components for retrieval
from agentic_core.L4_state.memory.chunk_manifest_registry import ChunkManifestRegistry
from agentic_core.L4_state.memory.unified_memory_facade import UnifiedMemoryFacade

__all__ = [
    "L4StateRetrievalBridge",
]


class L4StateRetrievalBridge:
    """Bridge L4 state store to retrieval pipeline.
    
    This class is imported by apps_* to establish ADG edges
    from apps to L4_state retrieval components.
    
    Minimal implementation: re-exports L4 retrieval functionality.
    """

    # Re-export core L4 classes for retrieval wiring
    ChunkManifestRegistry = ChunkManifestRegistry
    UnifiedMemoryFacade = UnifiedMemoryFacade

    @staticmethod
    def get_chunk_manifest_registry() -> type[ChunkManifestRegistry]:
        """Return the ChunkManifestRegistry class."""
        return ChunkManifestRegistry

    @staticmethod
    def get_memory_facade() -> type[UnifiedMemoryFacade]:
        """Return the UnifiedMemoryFacade class."""
        return UnifiedMemoryFacade
