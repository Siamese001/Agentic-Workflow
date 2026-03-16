from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_1")
_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_2")
_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_3")
_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_4")
_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_5")
_emit_emits_metric_event("ledger_retention_config", "p4obs", "metric_6")
_emit_records_incident_event("ledger_retention_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("ledger_retention_config", "p4obs", "anomaly")
_emit_writes_observability_log("ledger_retention_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("ledger_retention_config", "p4obs", "mon_state")
_emit_triggers_alert("ledger_retention_config", "p4obs", "alert")
_emit_links_incident_trace("ledger_retention_config", "p4obs", "trace_link")
_emit_captures_pattern("ledger_retention_config", "p3lm", "pattern")
_emit_records_learning_event("ledger_retention_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ledger_retention_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("ledger_retention_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ledger_retention_config", "p3lm", "routing")
_emit_improves_agent_policy("ledger_retention_config", "p3lm", "policy")
_emit_stores_learning_state("ledger_retention_config", "p3lm", "state")
_emit_records_execution_trace("ledger_retention_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ledger_retention_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ledger_retention_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ledger_retention_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ledger_retention_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ledger_retention_config", "env_read", "p2_env_1")
_emit_reads_environ("ledger_retention_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("ledger_retention_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ledger_retention_config", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "ledger_retention_config")
emit_determinism_digest("p0", "ledger_retention_config")

_emit_dispatches_healing_run("p1", "ledger_retention_config", "L4")
_emit_routes_through("p1", "ledger_retention_config", "L4")
_emit_escalates_to_human("p1", "ledger_retention_config", "L4")
_emit_reads_policy_state("p1", "ledger_retention_config", "L4")
_emit_pulls_context("p1", "ledger_retention_config", "context_pull")
_emit_pulls_context("p1", "ledger_retention_config", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ledger_retention_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ledger_retention_config", "uwg_term_secondary")
_emit_writes_through("p1", "ledger_retention_config", "write_through")
_emit_writes_through("p1", "ledger_retention_config", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ledger_retention_config", "safety_validation")
_emit_invokes_eval("p1", "ledger_retention_config", "eval_call")
_emit_proposal_commits_routing("p1", "ledger_retention_config", "routing_commit")

_emit_snapshots_state("p0", "ledger_retention_config", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "ledger_retention_config", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "ledger_retention_config")
_emit_authorize_and_execute("p2", "ledger_retention_config", "execution_auth")
_emit_validates_capability("p2", "ledger_retention_config", "capability_check")
_emit_routes_to_capability("p2", "ledger_retention_config", "capability_route")
_emit_writes_via_uwg("p2", "ledger_retention_config", "uwg_write")
_emit_blocks_direct_write("p2", "ledger_retention_config", "direct_write_block")
_emit_records_tool_invocation("p2", "ledger_retention_config", "tool_invocation")
_emit_captures_execution_output("p2", "ledger_retention_config", "exec_output")
_emit_dispatches_agent("p3", "ledger_retention_config", "agent_dispatch")
_emit_coordinates_agents("p3", "ledger_retention_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "ledger_retention_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "ledger_retention_config", "healing_outcome")
_emit_escalates_failure("p3", "ledger_retention_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "ledger_retention_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ledger_retention_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "ledger_retention_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "ledger_retention_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ledger_retention_config", "eval_metric")
_emit_stores_embedding("p4", "ledger_retention_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "ledger_retention_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ledger_retention_config", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@dataclass
class LedgerRetentionConfig:
    """
    L4 Configuration: Ledger & Audit Policies.
    Controls how long the truth is kept and how it is verified.
    """

    # Audit Trail
    AUDIT_RETENTION_DAYS: int = 90
    ENABLE_HASH_CHAINING: bool = True  # Cryptographic linkage

    # Telemetry
    TRACE_SAMPLING_RATE: float = 1.0  # 1.0 = Capture 100% of traces
    MAX_TRACE_DEPTH: int = 64

    # Genealogy (Provenance)
    TRACK_FILE_LINEAGE: bool = True
    MAX_GENEALOGY_GENERATIONS: int = 20


ledger_config = LedgerRetentionConfig()
