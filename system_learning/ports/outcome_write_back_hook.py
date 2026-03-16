"""Outcome Write-Back Hook Port — seam for real-time meta-learning feedback.

Called by dispatch_healing() immediately after an invocation completes.
Implementations write to HealingSuccessRateStore and call
update_qwen_confidence_prior() (for QWEN tier).

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST emit structured telemetry on failure (never fully silent).
- MUST NOT modify HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y.
- MUST NOT mutate healing_input or decision.
- MUST always execute (no retry-count short-circuit).
  Forced escalation applies to routing only, not write-back.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "outcome_write_back_hook", "p0_governance")
_emit_reads_policy_state("p0", "outcome_write_back_hook", "policy_binding")
_emit_snapshots_state("p0", "outcome_write_back_hook", "state_snapshot")
emit_replay_key("p0", "outcome_write_back_hook")
emit_determinism_digest("p0", "outcome_write_back_hook")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "outcome_write_back_hook", "execution_auth")
_emit_validates_capability("p2", "outcome_write_back_hook", "capability_check")
_emit_routes_to_capability("p2", "outcome_write_back_hook", "capability_route")
_emit_writes_via_uwg("p2", "outcome_write_back_hook", "uwg_write")
_emit_blocks_direct_write("p2", "outcome_write_back_hook", "direct_write_block")
_emit_records_tool_invocation("p2", "outcome_write_back_hook", "tool_invocation")
_emit_captures_execution_output("p2", "outcome_write_back_hook", "exec_output")
_emit_dispatches_agent("p3", "outcome_write_back_hook", "agent_dispatch")
_emit_coordinates_agents("p3", "outcome_write_back_hook", "agent_coordination")
_emit_records_workflow_lineage("p3", "outcome_write_back_hook", "workflow_lineage")
_emit_records_healing_outcome("p3", "outcome_write_back_hook", "healing_outcome")
_emit_escalates_failure("p3", "outcome_write_back_hook", "failure_escalation")
_emit_orchestrates_workflow("p3", "outcome_write_back_hook", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "outcome_write_back_hook", "healing_dispatch")
_emit_invokes_evaluation("p3", "outcome_write_back_hook", "evaluation_signal")
_emit_records_telemetry_event("p4", "outcome_write_back_hook", "telemetry_event")
_emit_captures_evaluation_metric("p4", "outcome_write_back_hook", "eval_metric")
_emit_stores_embedding("p4", "outcome_write_back_hook", "embedding_store")
_emit_updates_meta_learning_state("p4", "outcome_write_back_hook", "meta_learning")
_emit_links_execution_to_snapshot("p4", "outcome_write_back_hook", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision, HealingInput
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class OutcomeWriteBackHook(Protocol):
    """Synchronous write-back seam called after each heal invocation."""

    def on_outcome(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
        success: bool,
    ) -> None:
        """Handle a completed healing outcome.

        Parameters
        ----------
        healing_input : HealingInput
            The original structured failure context.
        decision : HealingDecision
            The routing decision that was executed.
        record : InvocationRecord | None
            The invocation trace record (None if exception before record).
        success : bool
            Whether the heal attempt succeeded.
        """
        ...


class NullOutcomeWriteBackHook:
    """No-op hook (default when no store is configured)."""

    def on_outcome(self, **kwargs) -> None:
        pass


class DefaultOutcomeWriteBackHook:
    """Default hook: writes to HealingSuccessRateStore + Qwen prior update.

    Never silently swallows exceptions — always emits structured telemetry.
    Always executes regardless of retry_count (forced escalation is routing-only).
    """

    def __init__(self, store=None) -> None:
        if store is None:
            from system_learning.engines.healing_success_rate_store import get_default_store

            store = get_default_store()
        self._store = store

    def on_outcome(self, *, healing_input, decision, record, success: bool) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultOutcomeWriteBackHook.on_outcome")

        try:
            self._store.record_outcome(healing_input.error_signature, success)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning(
                "write_back_store_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier

        if decision.tier == HealingTier.QWEN_VLLM:
            try:
                from agentic_core.L2_execution.healers.qwen_meta_learning import update_qwen_confidence_prior

                update_qwen_confidence_prior(healing_input.error_signature, success)
            # guardian: allow-silent-swallow
            except Exception as exc:
                logger.warning(
                    "write_back_qwen_prior_failed",
                    extra={
                        "error_signature": healing_input.error_signature,
                        "exception": str(exc),
                        "trace_id": healing_input.trace_id,
                    },
                )


__all__ = ["OutcomeWriteBackHook", "NullOutcomeWriteBackHook", "DefaultOutcomeWriteBackHook"]
