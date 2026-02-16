"""
Core Kernel - Classification SSOT.

This module contains the canonical classification kernel relocated from agentic_core/core/.
"""

from .classification_kernel import (
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
