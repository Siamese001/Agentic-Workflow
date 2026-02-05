"""Utility modules for apps_shared.

Migrated from archives/Reachout Engine Archive/Agentic LIC/:
- state_manager.py: StateManager for HOP-based state I/O
- vector_memory.py: VectorMemoryStore for ChromaDB integration
- circuit_breaker.py: CircuitBreaker pattern utilities

Phase 4 Optimization - Native Python Utilities:
- text_processing.py: Text processing and regex utilities
- math_operations.py: Mathematical operations and scoring
- json_parser.py: JSON parsing and manipulation
"""

from __future__ import annotations

from apps_shared.utils.json_parser_validator import JsonParser, ParseResult
from apps_shared.utils.math_operations import MathProcessor, ScoreResult
from apps_shared.utils.text_processing_validator import TextMatch, TextProcessor

# Lazy imports to avoid circular dependencies
__all__ = [
    "StateManager",
    "VectorMemoryStore",
    "CircuitBreaker",
    "TextProcessor",
    "TextMatch",
    "MathProcessor",
    "ScoreResult",
    "JsonParser",
    "ParseResult",
]
