"""L2 Execution Entry — packet intake and normalization (doc 04.1).

This package owns the L2 *entry surface* — the bridge between the governed
channel (L0 single-step packet, L3 current-step contract, or replay-resume)
and E1 Prep.
"""

from agentic_core.L2_execution.entry.packet_normalizer import (
    NormalizationResult,
    normalize_to_request,
)

__all__ = [
    "NormalizationResult",
    "normalize_to_request",
]
