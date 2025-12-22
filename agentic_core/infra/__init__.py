"""
Agentic Core Infrastructure - The Nervous System
Provides universal context, memory management, and LLM client access.
"""

from .context import (
    GeminiConfig,
    MemoryConfig,
    ThermalProfile,
    UniversalContext,
    context,
    get_context,
)

__all__ = [
    "UniversalContext",
    "get_context",
    "context",
    "ThermalProfile",
    "MemoryConfig",
    "GeminiConfig",
]
