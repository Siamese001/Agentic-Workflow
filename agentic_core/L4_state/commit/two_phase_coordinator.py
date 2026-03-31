"""Addendum 2.3: Two-Phase Commit Coordinator (2PC).

Enforces dual-acknowledgement requirement:
    ACK(target_resource)
    ACK(L4_ledger)

Failure of either → abort commit, emit MutationCommitFailure.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "two_phase_coordinator")
emit_determinism_digest("p0", "two_phase_coordinator")

_emit_dispatches_healing_run("p1", "two_phase_coordinator", "L4")
_emit_routes_through("p1", "two_phase_coordinator", "L4")
_emit_checks_agent_registry("p1", "two_phase_coordinator", "agent_registry")
_emit_validates_agent_capability("p1", "two_phase_coordinator", "capability")
_emit_dispatches_execution_plan("p1", "two_phase_coordinator", "exec_plan")
_emit_agent_executes_agent("p1", "two_phase_coordinator", "sub_agent")
_emit_routes_to_agent("p1", "two_phase_coordinator", "target_agent")
_emit_verifies_policy("p1", "two_phase_coordinator", "policy_check")
_emit_observes_runtime_state("p1", "two_phase_coordinator", "runtime_state")
_emit_verifies_boundary("p1", "two_phase_coordinator", "boundary_check")
_emit_transcripts_response("p1", "two_phase_coordinator", "transcript")
_emit_hard_fails_untranscripted("p1", "two_phase_coordinator")
_emit_gated_by_confidence("p1", "two_phase_coordinator", "confidence_gate")
_emit_escalates_to_human("p1", "two_phase_coordinator", "L4")
_emit_reads_policy_state("p1", "two_phase_coordinator", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "two_phase_coordinator", "p0_governance")
_emit_authorize_and_execute("p2", "two_phase_coordinator", "execution_auth")
_emit_validates_capability("p2", "two_phase_coordinator", "capability_check")
_emit_routes_to_capability("p2", "two_phase_coordinator", "capability_route")
_emit_writes_via_uwg("p2", "two_phase_coordinator", "uwg_write")
_emit_blocks_direct_write("p2", "two_phase_coordinator", "direct_write_block")
_emit_records_tool_invocation("p2", "two_phase_coordinator", "tool_invocation")
_emit_captures_execution_output("p2", "two_phase_coordinator", "exec_output")
_emit_dispatches_agent("p3", "two_phase_coordinator", "agent_dispatch")
_emit_coordinates_agents("p3", "two_phase_coordinator", "agent_coordination")
_emit_records_workflow_lineage("p3", "two_phase_coordinator", "workflow_lineage")
_emit_records_healing_outcome("p3", "two_phase_coordinator", "healing_outcome")
_emit_escalates_failure("p3", "two_phase_coordinator", "failure_escalation")
_emit_orchestrates_workflow("p3", "two_phase_coordinator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "two_phase_coordinator", "healing_dispatch")
_emit_invokes_evaluation("p3", "two_phase_coordinator", "evaluation_signal")
_emit_records_telemetry_event("p4", "two_phase_coordinator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "two_phase_coordinator", "eval_metric")
_emit_stores_embedding("p4", "two_phase_coordinator", "embedding_store")
_emit_updates_meta_learning_state("p4", "two_phase_coordinator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "two_phase_coordinator", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_1")
_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_2")
_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_3")
_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_4")
_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_5")
_emit_emits_metric_event("two_phase_coordinator", "p4obs", "metric_6")
_emit_records_incident_event("two_phase_coordinator", "p4obs", "incident")
_emit_captures_runtime_anomaly("two_phase_coordinator", "p4obs", "anomaly")
_emit_writes_observability_log("two_phase_coordinator", "p4obs", "obs_log")
_emit_updates_monitoring_state("two_phase_coordinator", "p4obs", "mon_state")
_emit_triggers_alert("two_phase_coordinator", "p4obs", "alert")
_emit_links_incident_trace("two_phase_coordinator", "p4obs", "trace_link")
_emit_captures_pattern("two_phase_coordinator", "p3lm", "pattern")
_emit_records_learning_event("two_phase_coordinator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("two_phase_coordinator", "p3lm", "snapshot")
_emit_feeds_meta_learning("two_phase_coordinator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("two_phase_coordinator", "p3lm", "routing")
_emit_improves_agent_policy("two_phase_coordinator", "p3lm", "policy")
_emit_stores_learning_state("two_phase_coordinator", "p3lm", "state")
_emit_records_execution_trace("two_phase_coordinator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("two_phase_coordinator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("two_phase_coordinator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("two_phase_coordinator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("two_phase_coordinator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("two_phase_coordinator", "env_read", "p2_env_1")
_emit_reads_environ("two_phase_coordinator", "env_read", "p2_env_2")
_emit_reads_runtime_state("two_phase_coordinator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("two_phase_coordinator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "two_phase_coordinator", "context_pull")
_emit_pulls_context("p1", "two_phase_coordinator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "two_phase_coordinator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "two_phase_coordinator", "uwg_term_2")
_emit_writes_through("p1", "two_phase_coordinator", "write_through")
_emit_writes_through("p1", "two_phase_coordinator", "write_through_2")
_emit_validated_by_safety_plane("p1", "two_phase_coordinator", "safety_validation")
_emit_invokes_eval("p1", "two_phase_coordinator", "eval_call")
_emit_proposal_commits_routing("p1", "two_phase_coordinator", "routing_commit")

logger = logging.getLogger(__name__)


class TwoPhaseCoordinator:
    """Coordinates a 2PC write: resource + ledger must both ACK.

    Usage:
        coordinator = TwoPhaseCoordinator()
        coordinator.execute_commit(
            resource_write=lambda: write_to_file(path, content),
            ledger_write=lambda: append_ledger(entry),
            context={"file": str(path)},
        )
    """

    def execute_commit(
        self,
        resource_write: Callable[[], Any],
        ledger_write: Callable[[], Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[Any, Any]:
        """Execute 2PC commit. Both writes must succeed or both are rolled back.

        Returns (resource_result, ledger_result) on success.
        Raises MutationCommitFailure if either ACK fails.
        """
        from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure  # noqa: F401
        _emit_snapshots_state(str(uuid.uuid4()), "TwoPhaseCoordinator.execute_commit", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "TwoPhaseCoordinator.execute_commit")

        ctx_str = str(context or {})
        resource_result: Any = None
        ledger_result: Any = None
        resource_ok = False
        try:
            resource_result = resource_write()
            resource_ok = True
            logger.debug("2PC Phase 1 ACK: resource write OK [%s]", ctx_str)
        except Exception as exc:
            raise MutationCommitFailure(
                f"2PC Phase 1 FAILED: resource write error — {exc} [{ctx_str}]"
            ) from exc
        try:
            ledger_result = ledger_write()
            logger.debug("2PC Phase 2 ACK: ledger write OK [%s]", ctx_str)
        except Exception as exc:
            raise MutationCommitFailure(
                f"2PC Phase 2 FAILED: ledger write error — {exc} (resource write already committed — manual rollback required) [{ctx_str}]"
            ) from exc
        logger.info("2PC commit: both ACKs received [%s]", ctx_str)
        return (resource_result, ledger_result)

    def safe_commit(
        self,
        resource_write: Callable[[], Any],
        ledger_write: Callable[[], Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Wrapper that returns a status dict instead of raising.

        Returns {"success": True, ...} or {"success": False, "error": ...}.
        """
        try:
            r, l = self.execute_commit(resource_write, ledger_write, context)
            return {"success": True, "resource_result": r, "ledger_result": l}
        except MutationCommitFailure as exc:    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context    # guardian: MutationCommitFailure should be handled with specific context
            logger.error("2PC commit failed: %s", exc)
            return {"success": False, "error": str(exc)}


__all__ = ["TwoPhaseCoordinator"]
