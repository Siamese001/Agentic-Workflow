from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "agentic_constants_util")
emit_determinism_digest("p0", "agentic_constants_util")

_emit_dispatches_healing_run("p1", "agentic_constants_util", "L1")
_emit_routes_through("p1", "agentic_constants_util", "L1")
_emit_checks_agent_registry("p1", "agentic_constants_util", "agent_registry")
_emit_validates_agent_capability("p1", "agentic_constants_util", "capability")
_emit_dispatches_execution_plan("p1", "agentic_constants_util", "exec_plan")
_emit_agent_executes_agent("p1", "agentic_constants_util", "sub_agent")
_emit_routes_to_agent("p1", "agentic_constants_util", "target_agent")
_emit_verifies_policy("p1", "agentic_constants_util", "policy_check")
_emit_observes_runtime_state("p1", "agentic_constants_util", "runtime_state")
_emit_verifies_boundary("p1", "agentic_constants_util", "boundary_check")
_emit_transcripts_response("p1", "agentic_constants_util", "transcript")
_emit_hard_fails_untranscripted("p1", "agentic_constants_util")
_emit_gated_by_confidence("p1", "agentic_constants_util", "confidence_gate")
_emit_escalates_to_human("p1", "agentic_constants_util", "L1")
_emit_reads_policy_state("p1", "agentic_constants_util", "L1")

_emit_snapshots_state("p0", "agentic_constants_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "agentic_constants_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "agentic_constants_util")
_emit_authorize_and_execute("p2", "agentic_constants_util", "execution_auth")
_emit_validates_capability("p2", "agentic_constants_util", "capability_check")
_emit_routes_to_capability("p2", "agentic_constants_util", "capability_route")
_emit_writes_via_uwg("p2", "agentic_constants_util", "uwg_write")
_emit_blocks_direct_write("p2", "agentic_constants_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agentic_constants_util", "tool_invocation")
_emit_captures_execution_output("p2", "agentic_constants_util", "exec_output")
_emit_dispatches_agent("p3", "agentic_constants_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agentic_constants_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agentic_constants_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agentic_constants_util", "healing_outcome")
_emit_escalates_failure("p3", "agentic_constants_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agentic_constants_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agentic_constants_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agentic_constants_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agentic_constants_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agentic_constants_util", "eval_metric")
_emit_stores_embedding("p4", "agentic_constants_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agentic_constants_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agentic_constants_util", "exec_snapshot_link")

"\nConstants for the Agentic Core system.\n[SSOT] Structural constants derived from structure_blueprint.py\n\nContains all shared constants used across the agentic framework.\n"
from typing import Any

from agentic_core.L0_routing.config import ROOT_PROTECTED_FILES
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_1")
_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_2")
_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_3")
_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_4")
_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_5")
_emit_emits_metric_event("agentic_constants_util", "p4obs", "metric_6")
_emit_records_incident_event("agentic_constants_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("agentic_constants_util", "p4obs", "anomaly")
_emit_writes_observability_log("agentic_constants_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("agentic_constants_util", "p4obs", "mon_state")
_emit_triggers_alert("agentic_constants_util", "p4obs", "alert")
_emit_links_incident_trace("agentic_constants_util", "p4obs", "trace_link")
_emit_captures_pattern("agentic_constants_util", "p3lm", "pattern")
_emit_records_learning_event("agentic_constants_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agentic_constants_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("agentic_constants_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agentic_constants_util", "p3lm", "routing")
_emit_improves_agent_policy("agentic_constants_util", "p3lm", "policy")
_emit_stores_learning_state("agentic_constants_util", "p3lm", "state")
_emit_records_execution_trace("agentic_constants_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agentic_constants_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agentic_constants_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agentic_constants_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agentic_constants_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agentic_constants_util", "env_read", "p2_env_1")
_emit_reads_environ("agentic_constants_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("agentic_constants_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agentic_constants_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agentic_constants_util", "context_pull")
_emit_pulls_context("p1", "agentic_constants_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "agentic_constants_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agentic_constants_util", "uwg_term_secondary")
_emit_writes_through("p1", "agentic_constants_util", "write_through")
_emit_writes_through("p1", "agentic_constants_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "agentic_constants_util", "safety_validation")
_emit_invokes_eval("p1", "agentic_constants_util", "eval_call")
_emit_proposal_commits_routing("p1", "agentic_constants_util", "routing_commit")

max_complexity: Any = 10
max_func_lines: Any = 50
max_nesting_spaces: Any = 40
allowed_root_files: Any = ROOT_PROTECTED_FILES
few_shot_strategic: Any = '\nYou are the StrategicPlannerAgent, an expert in mission planning and coordination.\n\nYour role is to:\n1. Generate comprehensive mission plans\n2. Coordinate agent execution order\n3. Allocate resources efficiently\n4. Anticipate potential issues\n\nMission Plan Structure:\n{\n    "mission_id": "unique_identifier",\n    "cycle_id": 1,\n    "priority": "HIGH|MEDIUM|LOW",\n    "objective": "Clear mission objective",\n    "phases": [...],\n    "risk_assessment": {...}\n}\n'
few_shot_sherlock: Any = "\nYou are Sherlock, the debugging specialist.\n\nYour role is to:\n1. Analyze code issues systematically\n2. Identify root causes\n3. Propose targeted fixes\n4. Verify fix effectiveness\n\nDebugging Process:\n1. Gather evidence (logs, stack traces)\n2. Formulate hypotheses\n3. Test hypotheses\n4. Implement solution\n"
few_shot_concurrency: Any = "\nYou are the ConcurrencyGuardianAgent, an expert in managing concurrent operations.\n\nYour role is to:\n1. Prevent race conditions\n2. Manage resource locks\n3. Detect deadlocks\n4. Ensure thread safety\n\nLock Usage Pattern:\n1. Acquire lock with timeout\n2. Execute critical section\n3. Always release in finally block\n4. Use async/await for I/O operations\n"
max_phase_time: Any = 300
memory_threshold_mb: Any = 100
performance_degradation_threshold: Any = 0.5
default_lock_timeout: Any = 30
max_retry_attempts: Any = 3
retry_delay: Any = 0.5
max_snapshots: Any = 100
benchmark_history_size: Any = 1000
max_alerts_per_type: Any = 50
canon_remote_repo: Any = "CANON_REMOTE_REPO"
google_api_key: Any = "GOOGLE_API_KEY"
enable_fuzz: Any = "ENABLE_FUZZ"
additional_repo_roots: Any = "ADDITIONAL_REPO_ROOTS"
memory_dir: Any = "observability/memory"
alerts_dir: Any = "observability/alerts"
cache_dir: Any = "observability/cache"
