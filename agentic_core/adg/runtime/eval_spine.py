"""
DEPRECATED: Moved to agentic_core.runtime.eval_spine (L_RUNTIME).

This module now provides a backward-compatible shim. Please update imports to:
    from agentic_core.runtime.eval_spine import EvalSpine, EvalSpineReport

Reason for move: L_SHARED (evaluation) importing L_TOOLS (adg runtime) creates
layer boundary violation. Eval spine is runtime infrastructure and belongs in L_RUNTIME.

This shim will be removed in a future release.
"""

from __future__ import annotations

import warnings

# Backward-compatible re-exports
from agentic_core.runtime.eval_spine import (  # noqa: F401
    DPOBatch,
    DriftAlert,
    EvalMetricResult,
    EvalSpine,
    EvalSpineReport,
    OptimizationProposal,
    OptimizationStage,
    PreferencePair,
)

warnings.warn(
    "agentic_core.adg.runtime.eval_spine is deprecated. "
    "Import from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_tracing, "
    "instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OptimizationStage",
    "EvalMetricResult",
    "DriftAlert",
    "PreferencePair",
    "DPOBatch",
    "OptimizationProposal",
    "EvalSpineReport",
    "EvalSpine",
]
