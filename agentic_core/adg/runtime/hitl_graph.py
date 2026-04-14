"""
DEPRECATED: Moved to agentic_core.L5_safety.hitl.hitl_graph (L5).

This module now provides a backward-compatible shim. Please update imports to:
    from agentic_core.L5_safety.enforcement.hitl.hitl_graph import HITLGraph, HITLRuntimeRecorder

Reason for move: L5 (safety/governance) importing L_TOOLS (adg runtime) creates
layer boundary violation. HITL is a safety concern and belongs in L5.

This shim will be removed in a future release.
"""

from __future__ import annotations

import warnings

# Backward-compatible re-exports
from agentic_core.L5_safety.enforcement.hitl.hitl_graph import (  # noqa: F401
    HITLCheckpoint,
    HITLDecisionType,
    HITLGraph,
    HITLRuntimeRecorder,
    HumanDecision,
)

warnings.warn(
    "agentic_core.adg.runtime.hitl_graph is deprecated. "
    "Import from agentic_core.L5_safety.enforcement.hitl.hitl_graph instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "HITLDecisionType",
    "HITLCheckpoint",
    "HumanDecision",
    "HITLGraph",
    "HITLRuntimeRecorder",
]
