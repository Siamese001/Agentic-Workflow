"""Compatibility exports for runtime ADG span emitters.

The canonical implementation lives in
``agentic_core.L6_system_learning.runtime_adg.runtime_span_emitter``.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_EXIT_DISPOSITION,
    SPAN_STEP_SEAL,
    SPAN_TRACE_ROOT,
    back_patch_trace_id,
    emit_exit_disposition,
    emit_trace_root,
    get_current_adapter,
    reset_current_adapter,
    seal_step,
    set_current_adapter,
)

__all__ = [
    "SPAN_EXIT_DISPOSITION",
    "SPAN_STEP_SEAL",
    "SPAN_TRACE_ROOT",
    "back_patch_trace_id",
    "emit_exit_disposition",
    "emit_trace_root",
    "get_current_adapter",
    "reset_current_adapter",
    "seal_step",
    "set_current_adapter",
]
