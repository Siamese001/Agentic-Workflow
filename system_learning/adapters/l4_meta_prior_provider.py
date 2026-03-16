"""L4MetaPriorProvider — bridges HealingSuccessRateStore to MetaPriorProvider seam.

Gap 3 fix: healing_tier_router.route_healing_tier() accepts meta_prior_provider but
the live L4-backed provider was never wired. This module provides the adapter.

Contracts:
- get_prior() delegates to HealingSuccessRateStore.get_prior() (read-only).
- Falls back to NeutralMetaPriorProvider on cold start (no store / store raises).
- MUST NOT import agentic_core modules directly (layer boundary: system_learning only).
- MUST be synchronous and deterministic.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "l4_meta_prior_provider", "execution_auth")
_emit_validates_capability("p2", "l4_meta_prior_provider", "capability_check")
_emit_routes_to_capability("p2", "l4_meta_prior_provider", "capability_route")
_emit_writes_via_uwg("p2", "l4_meta_prior_provider", "uwg_write")
_emit_blocks_direct_write("p2", "l4_meta_prior_provider", "direct_write_block")
_emit_records_tool_invocation("p2", "l4_meta_prior_provider", "tool_invocation")
_emit_captures_execution_output("p2", "l4_meta_prior_provider", "exec_output")
_emit_dispatches_agent("p3", "l4_meta_prior_provider", "agent_dispatch")
_emit_coordinates_agents("p3", "l4_meta_prior_provider", "agent_coordination")
_emit_records_workflow_lineage("p3", "l4_meta_prior_provider", "workflow_lineage")
_emit_records_healing_outcome("p3", "l4_meta_prior_provider", "healing_outcome")
_emit_escalates_failure("p3", "l4_meta_prior_provider", "failure_escalation")
_emit_orchestrates_workflow("p3", "l4_meta_prior_provider", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l4_meta_prior_provider", "healing_dispatch")
_emit_invokes_evaluation("p3", "l4_meta_prior_provider", "evaluation_signal")
_emit_records_telemetry_event("p4", "l4_meta_prior_provider", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l4_meta_prior_provider", "eval_metric")
_emit_stores_embedding("p4", "l4_meta_prior_provider", "embedding_store")
_emit_updates_meta_learning_state("p4", "l4_meta_prior_provider", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l4_meta_prior_provider", "exec_snapshot_link")
from system_learning.ports.meta_prior_provider import (
    _NEUTRAL_PRIOR,
    NeutralMetaPriorProvider,
)

_emit_applies_guardrail("p0", "l4_meta_prior_provider", "p0_governance")
_emit_reads_policy_state("p0", "l4_meta_prior_provider", "policy_binding")
_emit_snapshots_state("p0", "l4_meta_prior_provider", "state_snapshot")
emit_replay_key("p0", "l4_meta_prior_provider")
emit_determinism_digest("p0", "l4_meta_prior_provider")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_neutral = NeutralMetaPriorProvider()


class L4MetaPriorProvider:
    """Live prior provider backed by HealingSuccessRateStore.

    Parameters
    ----------
    store:
        An instance of HealingSuccessRateStore. If None, falls back to neutral prior.
    """

    def __init__(self, store=None) -> None:
        self._store = store

    def get_prior(self, error_signature: str) -> float:
        """Return historical success-rate prior for error_signature.

        Delegates to store.get_prior(). Falls back to _NEUTRAL_PRIOR when:
        - store is None (cold start)
        - store raises any exception
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L4MetaPriorProvider.get_prior")

        if self._store is None:
            return _NEUTRAL_PRIOR
        try:
            return self._store.get_prior(error_signature)
        except (AttributeError, KeyError, ValueError) as e:
            logger.debug(
                "L4MetaPriorProvider: store.get_prior raised; returning neutral",
                extra={"error_signature": error_signature, "error": str(e)},
                exc_info=True,
            )
            return _NEUTRAL_PRIOR

    @classmethod
    def from_default_store(cls) -> L4MetaPriorProvider:
        """Construct using the process-global default HealingSuccessRateStore."""
        from system_learning.engines.healing_success_rate_store import get_default_store

        return cls(store=get_default_store())


__all__ = ["L4MetaPriorProvider"]
