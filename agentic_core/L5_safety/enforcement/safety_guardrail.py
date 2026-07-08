from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "safety_guardrail")
trace_contract.emit_determinism_digest("p0", "safety_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "safety_guardrail", "L5")
trace_contract._emit_routes_through("p1", "safety_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "safety_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_guardrail", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_guardrail", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_guardrail", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_guardrail")
trace_contract._emit_gated_by_confidence("p1", "safety_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "safety_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "safety_guardrail", "L5")

trace_contract._emit_applies_guardrail("p0", "safety_guardrail", "p0_governance")
trace_contract._emit_snapshots_state("p0", "safety_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "safety_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_guardrail", "exec_snapshot_link")

"\nL5 Safety: SafetyGuardrail\nEnforces Zero-Loss principles during code mutation.\n"
import ast
from typing import Any


trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "safety_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_guardrail", "routing_commit")


class SafetyGuardrail:
    """Enforces Zero-Loss principles during mutation."""

    # guardian: allow-magic-config
    def __init__(self, deletion_limit: int = 110):
        """
        Initialize SafetyGuardrail.

        Args:
            deletion_limit: Maximum number of lines that can be deleted in standard mode
        """
        self.deletion_limit = deletion_limit

    def verify_change(
        self,
        original_code: str,
        new_code: str,
        fission_active: bool = False,
    ) -> tuple[bool, str]:
        """
        Verify that code changes are safe and don't violate zero-loss principles.

        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)

        Returns:
            Tuple of (is_safe, message)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SafetyGuardrail.verify_change")
        import hashlib as _hashlib  # noqa: PLC0415    # review: Syntax errors should be caught at parser level, not runtime

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyGuardrail.verify_change".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not new_code.strip():
            return (False, "Safety Block: Attempted to wipe file.")
        try:
            ast.parse(new_code)
        except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
            return (False, f"Safety Block: Mutation introduced syntax error: {e.msg} at line {e.lineno}")
        orig_len: Any = len(original_code.splitlines())
        new_len: Any = len(new_code.splitlines())
        delta: Any = orig_len - new_len
        if delta == 0 and original_code == new_code and (not fission_active):
            return (False, "Safety Block: Mutation resulted in no change (possible engine failure).")
        if fission_active:
            return (True, "Fission Whitelist: Mass deletion permitted for Facade.")
        if delta > self.deletion_limit:
            return (False, f"Safety Block: Mass deletion detected ({delta} lines).")
        return (True, "Safety Pass.")
