"""
03_runtime/compat/exceptions.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: d2d558e890be9cbd155f8be867113d7ceff8ba02ef566e28d4f878726b50e6ff
"""


from __future__ import annotations

# Re-export all exceptions from the canonical location
from ..shared.exceptions import (
    AgenticWorkflowError,
    HopExecutionError,
    StagingBufferError,
    CircuitBreakerOpenError,
    PhaseTimeoutError,
    FactualFailureException,
    ValidationError,
    ConfigurationError,
    APIError,
    MCPClientInitializationError,
    SemanticCacheError,
    PipelineError,
    is_recoverable,
    get_error_chain,
)

__all__ = [
    "AgenticWorkflowError",
    "HopExecutionError",
    "StagingBufferError",
    "CircuitBreakerOpenError",
    "PhaseTimeoutError",
    "FactualFailureException",
    "ValidationError",
    "ConfigurationError",
    "APIError",
    "MCPClientInitializationError",
    "SemanticCacheError",
    "PipelineError",
    "is_recoverable",
    "get_error_chain",
]
