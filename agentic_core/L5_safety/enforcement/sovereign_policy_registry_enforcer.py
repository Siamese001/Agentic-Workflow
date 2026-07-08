from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_policy_registry_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_policy_registry_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_policy_registry_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_policy_registry_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_policy_registry_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_policy_registry_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_policy_registry_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_policy_registry_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_policy_registry_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_policy_registry_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_policy_registry_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_policy_registry_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_policy_registry_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_policy_registry_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_policy_registry_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_policy_registry_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_policy_registry_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_policy_registry_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_policy_registry_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_policy_registry_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_policy_registry_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_policy_registry_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_policy_registry_enforcer", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "sovereign_policy_registry_enforcer")
trace_contract.emit_determinism_digest("p0", "sovereign_policy_registry_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_policy_registry_enforcer", "L5")
trace_contract._emit_routes_through("p1", "sovereign_policy_registry_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "sovereign_policy_registry_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_policy_registry_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_policy_registry_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_policy_registry_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_policy_registry_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_policy_registry_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_policy_registry_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_policy_registry_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_policy_registry_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_policy_registry_enforcer")
trace_contract._emit_gated_by_confidence("p1", "sovereign_policy_registry_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_policy_registry_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "sovereign_policy_registry_enforcer", "L5")
trace_contract._emit_pulls_context("p1", "sovereign_policy_registry_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_policy_registry_enforcer", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_policy_registry_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_policy_registry_enforcer", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "sovereign_policy_registry_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_policy_registry_enforcer", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_policy_registry_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_policy_registry_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_policy_registry_enforcer", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "sovereign_policy_registry_enforcer")
trace_contract._emit_applies_guardrail("p0", "sovereign_policy_registry_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "sovereign_policy_registry_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "sovereign_policy_registry_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_policy_registry_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_policy_registry_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_policy_registry_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_policy_registry_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_policy_registry_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_policy_registry_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_policy_registry_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_policy_registry_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_policy_registry_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_policy_registry_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_policy_registry_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_policy_registry_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_policy_registry_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_policy_registry_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_policy_registry_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_policy_registry_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_policy_registry_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_policy_registry_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_policy_registry_enforcer", "exec_snapshot_link")


class PolicySeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SovereignPolicy:
    id: str
    description: str
    severity: PolicySeverity
    enabled: bool = True


class SovereignPolicyRegistry:
    """
    The Immutable Constitution of the Agentic Core.
    Defines what IS allowed, independent of HOW it is checked.
    """

    DATA_LOCALITY = SovereignPolicy(
        id="GOV-001",
        description="L4 State must not leave local execution environment without explicit encryption.",
        severity=PolicySeverity.CRITICAL,
    )
    MAX_TOKENS_PER_TURN = SovereignPolicy(
        id="GOV-002",
        description="Single LLM turn must not exceed 32k tokens.",
        severity=PolicySeverity.HIGH,
    )
    NO_PLAINTEXT_SECRETS = SovereignPolicy(
        id="GOV-003",
        description="No high-entropy strings (API keys) in logs or stdout.",
        severity=PolicySeverity.CRITICAL,
    )

    @classmethod
    def get_all(cls):
        return [v for k, v in cls.__dict__.items() if isinstance(v, SovereignPolicy)]
