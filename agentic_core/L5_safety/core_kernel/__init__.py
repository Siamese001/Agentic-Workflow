"""
Core Kernel - Classification SSOT.

This module contains the canonical classification kernel relocated from agentic_core/core/.
"""

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

from .classification_kernel import (
    FileType,
    classification_cache_context,
    classification_cache_info,
    classify_file_standalone,
    clear_classification_cache,
    is_agent_file,
    is_agent_or_orchestrator,
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    "FileType",
    "classify_file_standalone",
    "is_agent_file",
    "is_agent_or_orchestrator",
    "clear_classification_cache",
    "classification_cache_info",
    "classification_cache_context",
]
