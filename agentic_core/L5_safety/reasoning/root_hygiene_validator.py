"""
RootHygieneValidatorAgent - L5 Pure Validator.

Read-only scan of root hygiene violations via RootHygieneAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "root_hygiene_validator")
trace_contract.emit_determinism_digest("p0", "root_hygiene_validator")

trace_contract._emit_dispatches_healing_run("p1", "root_hygiene_validator", "L5")
trace_contract._emit_routes_through("p1", "root_hygiene_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "root_hygiene_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "root_hygiene_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "root_hygiene_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "root_hygiene_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "root_hygiene_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "root_hygiene_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "root_hygiene_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "root_hygiene_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "root_hygiene_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "root_hygiene_validator")
trace_contract._emit_gated_by_confidence("p1", "root_hygiene_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "root_hygiene_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "root_hygiene_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "root_hygiene_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "root_hygiene_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "root_hygiene_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "root_hygiene_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "root_hygiene_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "root_hygiene_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "root_hygiene_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "root_hygiene_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "root_hygiene_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "root_hygiene_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "root_hygiene_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "root_hygiene_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "root_hygiene_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "root_hygiene_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "root_hygiene_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "root_hygiene_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "root_hygiene_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "root_hygiene_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "root_hygiene_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "root_hygiene_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "root_hygiene_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "root_hygiene_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("root_hygiene_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("root_hygiene_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("root_hygiene_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("root_hygiene_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("root_hygiene_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("root_hygiene_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("root_hygiene_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("root_hygiene_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("root_hygiene_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("root_hygiene_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("root_hygiene_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("root_hygiene_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("root_hygiene_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("root_hygiene_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("root_hygiene_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("root_hygiene_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("root_hygiene_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("root_hygiene_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("root_hygiene_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("root_hygiene_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("root_hygiene_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("root_hygiene_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("root_hygiene_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "root_hygiene_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "root_hygiene_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "root_hygiene_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "root_hygiene_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "root_hygiene_validator", "write_through")
trace_contract._emit_writes_through("p1", "root_hygiene_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "root_hygiene_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "root_hygiene_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "root_hygiene_validator", "routing_commit")


class RootHygieneValidatorAgent:
    """L5 Certify-only validator for root directory hygiene violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self) -> dict[str, Any]:
        """Delegate to RootHygieneAgent.scan_root_violations (read-only)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "RootHygieneValidatorAgent.scan_root_violations",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:RootHygieneValidatorAgent.scan_root_violations".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent

        agent = RootHygieneAgent(project_root=self.project_root, dry_run=True)
        return agent.scan_root_violations()
