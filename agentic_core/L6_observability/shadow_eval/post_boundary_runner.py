"""Post-boundary L6 shadow runner — drive 6A + observer from sealed exhaust.

Convenience seam for callers that have a sealed ``raw_exhaust`` mapping (built by
``agentic_core.runtime.exhaust.shadow_raw_exhaust_adapter.build_l6_shadow_raw_exhaust``)
and want to run L6 shadow observability over it **after the current-run
boundary**.

Process-map law preserved (this module adds no new authority):
  * L6 runs only over sealed exhaust — 6A ingest refuses in-flight runs at the
    completed-run marker.
  * Observer + readiness are read-only.
  * 6B evaluation runs only when readiness is scorable AND a governance baseline
    is supplied; it produces records/receipts and never writes L4.
  * Promotion (6D) is **not** run here — that requires an explicitly injected
    UWG commit function and is the caller's decision, never automatic.
"""

from __future__ import annotations

from typing import Mapping

from agentic_core.L6_observability.shadow_eval.evaluation import GovernanceBaseline
from agentic_core.L6_observability.shadow_eval.observer import (
    READINESS_PARTIAL,
    READINESS_READY,
)
from agentic_core.L6_observability.shadow_eval.pipeline import (
    L6PipelineState,
    run_6a,
    run_6b,
    run_observer,
)
from agentic_core.L6_observability.shadow_eval.spearman_calibration import (
    CalibrationContext,
)

__all__ = ["run_l6_shadow_from_sealed_exhaust"]

#: Readiness decisions for which 6B evaluation may proceed.
_SCORABLE_DECISIONS = frozenset({READINESS_READY, READINESS_PARTIAL})


def run_l6_shadow_from_sealed_exhaust(
    raw_exhaust: Mapping[str, object],
    *,
    governance_baseline: GovernanceBaseline | None = None,
    run_eval: bool = True,
    calibration_context: CalibrationContext | None = None,
) -> L6PipelineState:
    """Run 6A ingest + observer (always) and 6B evaluation (when scorable).

    Args:
        raw_exhaust: sealed post-Exit exhaust mapping (see the shadow adapter).
        governance_baseline: required to run 6B; when ``None``, only ingest +
            observer/readiness run.
        run_eval: set False to stop after observer even with a baseline supplied.

    Returns:
        The populated :class:`L6PipelineState` (ingest + readiness always set;
        ``eval`` set only when 6B ran). No L4 write is performed; no promotion.
    """
    state = L6PipelineState()
    run_6a(state, raw_exhaust)
    readiness = run_observer(state)
    if run_eval and governance_baseline is not None and readiness.readiness_decision in _SCORABLE_DECISIONS:
        run_6b(
            state,
            readiness,
            governance_baseline=governance_baseline,
            calibration_context=calibration_context,
        )
    return state
