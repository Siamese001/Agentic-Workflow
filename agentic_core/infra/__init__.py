"""
Agentic Core Infrastructure - The Nervous System
Provides universal context, memory management, and LLM client access.
"""

from .context import (
    UniversalContext,
    get_context,
    context,
    ThermalProfile,
    MemoryConfig,
    GeminiConfig,
)

__all__ = [
    "UniversalContext",
    "get_context",
    "context",
    "ThermalProfile",
    "MemoryConfig",
    "GeminiConfig",
]
