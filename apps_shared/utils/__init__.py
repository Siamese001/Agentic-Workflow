from __future__ import annotations

"""Utility modules for apps_shared.

Migrated from archives/Reachout Engine Archive/Agentic LIC/:
- state_manager.py: StateManager for HOP-based state I/O
- vector_memory.py: VectorMemoryStore for ChromaDB integration
- circuit_breaker.py: CircuitBreaker pattern utilities
"""

# Lazy imports to avoid circular dependencies
__all__ = [
    "StateManager",
    "VectorMemoryStore",
    "CircuitBreaker",
]
