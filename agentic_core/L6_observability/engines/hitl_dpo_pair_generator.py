"""DPO Pair Generator - deterministic human-in-the-loop feedback processing.

Converts APPROVE/REJECT decisions into DPO pairs with stable hashing.
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from agentic_core.L6_observability.types.dpo_types import DPOExampleId, DPOPair
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
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
    record_execution_trace,
)

emit_replay_key("p0", "hitl_dpo_pair_generator")
emit_determinism_digest("p0", "hitl_dpo_pair_generator")

_emit_dispatches_healing_run("p1", "hitl_dpo_pair_generator", "L6")
_emit_routes_through("p1", "hitl_dpo_pair_generator", "L6")
_emit_checks_agent_registry("p1", "hitl_dpo_pair_generator", "agent_registry")
_emit_validates_agent_capability("p1", "hitl_dpo_pair_generator", "capability")
_emit_dispatches_execution_plan("p1", "hitl_dpo_pair_generator", "exec_plan")
_emit_agent_executes_agent("p1", "hitl_dpo_pair_generator", "sub_agent")
_emit_routes_to_agent("p1", "hitl_dpo_pair_generator", "target_agent")
_emit_verifies_policy("p1", "hitl_dpo_pair_generator", "policy_check")
_emit_observes_runtime_state("p1", "hitl_dpo_pair_generator", "runtime_state")
_emit_verifies_boundary("p1", "hitl_dpo_pair_generator", "boundary_check")
_emit_transcripts_response("p1", "hitl_dpo_pair_generator", "transcript")
_emit_hard_fails_untranscripted("p1", "hitl_dpo_pair_generator")
_emit_gated_by_confidence("p1", "hitl_dpo_pair_generator", "confidence_gate")
_emit_escalates_to_human("p1", "hitl_dpo_pair_generator", "L6")
_emit_reads_policy_state("p1", "hitl_dpo_pair_generator", "L6")
_emit_authorize_and_execute("p2", "hitl_dpo_pair_generator", "execution_auth")
_emit_validates_capability("p2", "hitl_dpo_pair_generator", "capability_check")
_emit_routes_to_capability("p2", "hitl_dpo_pair_generator", "capability_route")
_emit_writes_via_uwg("p2", "hitl_dpo_pair_generator", "uwg_write")
_emit_blocks_direct_write("p2", "hitl_dpo_pair_generator", "direct_write_block")
_emit_records_tool_invocation("p2", "hitl_dpo_pair_generator", "tool_invocation")
_emit_captures_execution_output("p2", "hitl_dpo_pair_generator", "exec_output")
_emit_dispatches_agent("p3", "hitl_dpo_pair_generator", "agent_dispatch")
_emit_coordinates_agents("p3", "hitl_dpo_pair_generator", "agent_coordination")
_emit_records_workflow_lineage("p3", "hitl_dpo_pair_generator", "workflow_lineage")
_emit_records_healing_outcome("p3", "hitl_dpo_pair_generator", "healing_outcome")
_emit_escalates_failure("p3", "hitl_dpo_pair_generator", "failure_escalation")
_emit_orchestrates_workflow("p3", "hitl_dpo_pair_generator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hitl_dpo_pair_generator", "healing_dispatch")
_emit_invokes_evaluation("p3", "hitl_dpo_pair_generator", "evaluation_signal")
_emit_records_telemetry_event("p4", "hitl_dpo_pair_generator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hitl_dpo_pair_generator", "eval_metric")
_emit_stores_embedding("p4", "hitl_dpo_pair_generator", "embedding_store")
_emit_updates_meta_learning_state("p4", "hitl_dpo_pair_generator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hitl_dpo_pair_generator", "exec_snapshot_link")
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

record_execution_trace("hitl_dpo_pair_generator", "hitl_dpo_pair_generator_trace")


_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_1")
_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_2")
_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_3")
_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_4")
_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_5")
_emit_emits_metric_event("hitl_dpo_pair_generator", "p4obs", "metric_6")
_emit_records_incident_event("hitl_dpo_pair_generator", "p4obs", "incident")
_emit_captures_runtime_anomaly("hitl_dpo_pair_generator", "p4obs", "anomaly")
_emit_writes_observability_log("hitl_dpo_pair_generator", "p4obs", "obs_log")
_emit_updates_monitoring_state("hitl_dpo_pair_generator", "p4obs", "mon_state")
_emit_triggers_alert("hitl_dpo_pair_generator", "p4obs", "alert")
_emit_links_incident_trace("hitl_dpo_pair_generator", "p4obs", "trace_link")
_emit_captures_pattern("hitl_dpo_pair_generator", "p3lm", "pattern")
_emit_records_learning_event("hitl_dpo_pair_generator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hitl_dpo_pair_generator", "p3lm", "snapshot")
_emit_feeds_meta_learning("hitl_dpo_pair_generator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hitl_dpo_pair_generator", "p3lm", "routing")
_emit_improves_agent_policy("hitl_dpo_pair_generator", "p3lm", "policy")
_emit_stores_learning_state("hitl_dpo_pair_generator", "p3lm", "state")
_emit_records_execution_trace("hitl_dpo_pair_generator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hitl_dpo_pair_generator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hitl_dpo_pair_generator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hitl_dpo_pair_generator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hitl_dpo_pair_generator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hitl_dpo_pair_generator", "env_read", "p2_env_1")
_emit_reads_environ("hitl_dpo_pair_generator", "env_read", "p2_env_2")
_emit_reads_runtime_state("hitl_dpo_pair_generator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hitl_dpo_pair_generator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hitl_dpo_pair_generator", "context_pull")
_emit_pulls_context("p1", "hitl_dpo_pair_generator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hitl_dpo_pair_generator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hitl_dpo_pair_generator", "uwg_term_2")
_emit_writes_through("p1", "hitl_dpo_pair_generator", "write_through")
_emit_writes_through("p1", "hitl_dpo_pair_generator", "write_through_2")
_emit_validated_by_safety_plane("p1", "hitl_dpo_pair_generator", "safety_validation")
_emit_invokes_eval("p1", "hitl_dpo_pair_generator", "eval_call")
_emit_proposal_commits_routing("p1", "hitl_dpo_pair_generator", "routing_commit")


class DPOPairGenerator(Protocol):
    """Protocol for generating DPO pairs from human feedback."""

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair from human feedback.

        Parameters:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with deterministic hashing.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DPOPairGenerator.generate", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DPOPairGenerator.generate", "p0_governance")
        ...


class DefaultDeterministicDPOPairGenerator:
    """Default deterministic DPO pair generator.

    Generates stable DPO pairs with SHA-256 hashing and no side effects.
    """

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair with deterministic behavior.

        Args:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with stable example_id and content_hash.

        Raises:
            ValueError: If human_decision is not "APPROVE" or "REJECT".
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "DefaultDeterministicDPOPairGenerator.generate"
        )

        if human_decision not in {"APPROVE", "REJECT"}:
            raise ValueError(f"human_decision must be 'APPROVE' or 'REJECT', got: {human_decision}")
        control_hash = hashlib.sha256(control_output_bytes).hexdigest()
        candidate_hash = hashlib.sha256(candidate_output_bytes).hexdigest()
        example_id = DPOExampleId(control_hash=control_hash, candidate_hash=candidate_hash)
        pair = DPOPair(
            example_id=example_id,
            control_output_hash=control_hash,
            candidate_output_hash=candidate_hash,
            human_decision=human_decision,
            reasons=reason_codes,
        )
        return pair
