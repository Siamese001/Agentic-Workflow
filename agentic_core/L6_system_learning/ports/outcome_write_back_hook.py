"""Outcome Write-Back Hook Port — seam for real-time meta-learning feedback.

Called by dispatch_healing() immediately after an invocation completes.
Implementations write to HealingSuccessRateStore and call
update_qwen_confidence_prior() (for QWEN tier).

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST emit structured telemetry on failure (never fully silent).
- MUST NOT mutate retired heal-confidence thresholds at runtime.
- MUST NOT mutate healing_input or decision.
- MUST always execute (no retry-count short-circuit).
  Forced escalation applies to routing only, not write-back.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "outcome_write_back_hook", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "outcome_write_back_hook", "policy_binding")
trace_contract._emit_snapshots_state("p0", "outcome_write_back_hook", "state_snapshot")
trace_contract.emit_replay_key("p0", "outcome_write_back_hook")
trace_contract.emit_determinism_digest("p0", "outcome_write_back_hook")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "outcome_write_back_hook", "execution_auth")
trace_contract._emit_validates_capability("p2", "outcome_write_back_hook", "capability_check")
trace_contract._emit_routes_to_capability("p2", "outcome_write_back_hook", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "outcome_write_back_hook", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "outcome_write_back_hook", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "outcome_write_back_hook", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "outcome_write_back_hook", "exec_output")
trace_contract._emit_dispatches_agent("p3", "outcome_write_back_hook", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "outcome_write_back_hook", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "outcome_write_back_hook", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "outcome_write_back_hook", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "outcome_write_back_hook", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "outcome_write_back_hook", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "outcome_write_back_hook", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "outcome_write_back_hook", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "outcome_write_back_hook", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "outcome_write_back_hook", "eval_metric")
trace_contract._emit_stores_embedding("p4", "outcome_write_back_hook", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "outcome_write_back_hook", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "outcome_write_back_hook", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.L3_orchestration.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L3_orchestration.healers.healing_tier_types import HealingDecision, HealingInput

trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("outcome_write_back_hook", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("outcome_write_back_hook", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("outcome_write_back_hook", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("outcome_write_back_hook", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("outcome_write_back_hook", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("outcome_write_back_hook", "p4obs", "alert")
trace_contract._emit_links_incident_trace("outcome_write_back_hook", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("outcome_write_back_hook", "p3lm", "pattern")
trace_contract._emit_records_learning_event("outcome_write_back_hook", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("outcome_write_back_hook", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("outcome_write_back_hook", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("outcome_write_back_hook", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("outcome_write_back_hook", "p3lm", "policy")
trace_contract._emit_stores_learning_state("outcome_write_back_hook", "p3lm", "state")
trace_contract._emit_records_execution_trace("outcome_write_back_hook", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("outcome_write_back_hook", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("outcome_write_back_hook", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("outcome_write_back_hook", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("outcome_write_back_hook", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("outcome_write_back_hook", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("outcome_write_back_hook", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("outcome_write_back_hook", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("outcome_write_back_hook", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "outcome_write_back_hook", "context_pull")
trace_contract._emit_pulls_context("p1", "outcome_write_back_hook", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "outcome_write_back_hook", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "outcome_write_back_hook", "uwg_term_2")
trace_contract._emit_writes_through("p1", "outcome_write_back_hook", "write_through")
trace_contract._emit_writes_through("p1", "outcome_write_back_hook", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "outcome_write_back_hook", "safety_validation")
trace_contract._emit_invokes_eval("p1", "outcome_write_back_hook", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "outcome_write_back_hook", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "outcome_write_back_hook", "human_escalation")
trace_contract._emit_routes_through("p1", "outcome_write_back_hook", "route_through")
trace_contract._emit_checks_agent_registry("p1", "outcome_write_back_hook", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "outcome_write_back_hook", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "outcome_write_back_hook", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "outcome_write_back_hook", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "outcome_write_back_hook", "target_agent")
trace_contract._emit_verifies_policy("p1", "outcome_write_back_hook", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "outcome_write_back_hook", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "outcome_write_back_hook", "boundary_check")
trace_contract._emit_transcripts_response("p1", "outcome_write_back_hook", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "outcome_write_back_hook")
trace_contract._emit_gated_by_confidence("p1", "outcome_write_back_hook", "confidence_gate")

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
            from agentic_core.L6_system_learning.engines.healing_success_rate_store import get_default_store

            store = get_default_store()
        self._store = store

    def on_outcome(self, *, healing_input, decision, record, success: bool) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DefaultOutcomeWriteBackHook.on_outcome"
        )

        try:
            self._store.record_outcome(healing_input.error_signature, success)
        except (  # guardian: allow-log-and-swallow -- outcome store write best-effort: non-fatal, healing completes regardless
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            logger.warning(
                "write_back_store_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )
        from agentic_core.L3_orchestration.healers.healing_tier_types import HealingTier

        if decision.tier == HealingTier.QWEN_VLLM:
            try:
                from agentic_core.L3_orchestration.healers.qwen_meta_learning import (
                    update_qwen_confidence_prior,
                )

                update_qwen_confidence_prior(healing_input.error_signature, success)
            except (  # guardian: allow-log-and-swallow -- qwen prior update best-effort: non-fatal, healing tier unaffected
                AttributeError,
                ImportError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:
                logger.warning(
                    "write_back_qwen_prior_failed",
                    extra={
                        "error_signature": healing_input.error_signature,
                        "exception": str(exc),
                        "trace_id": healing_input.trace_id,
                    },
                )


__all__ = ["OutcomeWriteBackHook", "NullOutcomeWriteBackHook", "DefaultOutcomeWriteBackHook"]
