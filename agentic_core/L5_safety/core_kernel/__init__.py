"""
Core Kernel - Classification SSOT.

This module contains the canonical classification kernel relocated from agentic_core/core/.
"""

from .classification_kernel import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    FileType,
    classification_cache_context,
    classification_cache_info,
    classify_file_standalone,
    clear_classification_cache,
    is_agent_file,
    is_agent_or_orchestrator,
)

__all__ = [
    "FileType",
    "classify_file_standalone",
    "is_agent_file",
    "is_agent_or_orchestrator",
    "clear_classification_cache",
    "classification_cache_info",
    "classification_cache_context",
]
