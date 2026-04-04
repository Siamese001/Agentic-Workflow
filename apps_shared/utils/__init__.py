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

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from apps_shared.utils.governed_prompt_adapter import GovernedPromptAdapter
from apps_shared.utils.json_parser_validator_util import JsonParser, ParseResult
from apps_shared.utils.math_operations_util import MathProcessor, ScoreResult
from apps_shared.utils.text_processing_validator_util import TextMatch, TextProcessor

__all__ = ['TextProcessor', 'TextMatch', 'MathProcessor', 'ScoreResult', 'JsonParser', 'ParseResult', 'GovernedPromptAdapter']
