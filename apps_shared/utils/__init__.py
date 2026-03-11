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

from apps_shared.utils.json_parser_validator_util import JsonParser, ParseResult
from apps_shared.utils.math_operations_util import MathProcessor, ScoreResult
from apps_shared.utils.text_processing_validator_util import TextMatch, TextProcessor

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Lazy imports to avoid circular dependencies
__all__ = [
    "TextProcessor",
    "TextMatch",
    "MathProcessor",
    "ScoreResult",
    "JsonParser",
    "ParseResult",
]
