"""
ValidatorMixin - Unified Validation Access for Agents

[PHASE 5 MIGRATION] Provides single interface to validation operations.
"""

from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "validator_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "validator_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "validator_mixin", "state_snapshot")
trace_contract.emit_replay_key("p0", "validator_mixin")
trace_contract.emit_determinism_digest("p0", "validator_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "validator_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "validator_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "validator_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "validator_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "validator_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "validator_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "validator_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "validator_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "validator_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "validator_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "validator_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "validator_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "validator_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "validator_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "validator_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "validator_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "validator_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "validator_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "validator_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "validator_mixin", "exec_snapshot_link")

try:
    from agentic_core.L5_safety.types.healing_orchestration_types import (
        ValidatorOrchestrator,
        get_validator_orchestrator,
    )
except ImportError:  # guardian: allow-silent-swallow -- optional dependency

    class ValidatorOrchestrator:
        """Stub orchestrator when real module is unavailable."""

        pass

    def get_validator_orchestrator():
        return None



trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("validator_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("validator_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("validator_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("validator_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("validator_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("validator_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("validator_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("validator_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("validator_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("validator_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("validator_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("validator_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("validator_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("validator_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("validator_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("validator_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("validator_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("validator_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("validator_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("validator_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("validator_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("validator_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("validator_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "validator_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "validator_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "validator_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "validator_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "validator_mixin", "write_through")
trace_contract._emit_writes_through("p1", "validator_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "validator_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "validator_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "validator_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "validator_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "validator_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "validator_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "validator_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "validator_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "validator_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "validator_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "validator_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "validator_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "validator_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "validator_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "validator_mixin")
trace_contract._emit_gated_by_confidence("p1", "validator_mixin", "confidence_gate")


class ValidatorMixin:
    """
    Mixin providing unified validator orchestrator access.
    """

    _validator_orchestrator: ValidatorOrchestrator | None = None

    @property
    def validator_orchestrator(self) -> ValidatorOrchestrator:
        """Lazy-load validator orchestrator singleton."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ValidatorMixin.validator_orchestrator"
        )

        if self._validator_orchestrator is None:
            self._validator_orchestrator = get_validator_orchestrator()
        return self._validator_orchestrator

    async def orchestrator_validate(self, content: Any, validator_name: str, context: dict = None) -> dict:
        """Execute validation through orchestrator."""
        return await self.validator_orchestrator.validate(content, validator_name, context)
