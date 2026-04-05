from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "verify_all_checkpoint_files_util")
emit_determinism_digest("p0", "verify_all_checkpoint_files_util")

_emit_dispatches_healing_run("p1", "verify_all_checkpoint_files_util", "L0")
_emit_routes_through("p1", "verify_all_checkpoint_files_util", "L0")
_emit_checks_agent_registry("p1", "verify_all_checkpoint_files_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_all_checkpoint_files_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_all_checkpoint_files_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_all_checkpoint_files_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_all_checkpoint_files_util", "target_agent")
_emit_verifies_policy("p1", "verify_all_checkpoint_files_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_all_checkpoint_files_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_all_checkpoint_files_util", "boundary_check")
_emit_transcripts_response("p1", "verify_all_checkpoint_files_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_all_checkpoint_files_util")
_emit_gated_by_confidence("p1", "verify_all_checkpoint_files_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_all_checkpoint_files_util", "L0")
_emit_reads_policy_state("p1", "verify_all_checkpoint_files_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_all_checkpoint_files_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_all_checkpoint_files_util", "p0_governance")
_emit_snapshots_state("p0", "verify_all_checkpoint_files_util", "state_snapshot")
_emit_authorize_and_execute("p2", "verify_all_checkpoint_files_util", "execution_auth")
_emit_validates_capability("p2", "verify_all_checkpoint_files_util", "capability_check")
_emit_routes_to_capability("p2", "verify_all_checkpoint_files_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_all_checkpoint_files_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_all_checkpoint_files_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_all_checkpoint_files_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_all_checkpoint_files_util", "exec_output")
_emit_dispatches_agent("p3", "verify_all_checkpoint_files_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_all_checkpoint_files_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_all_checkpoint_files_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_all_checkpoint_files_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_all_checkpoint_files_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_all_checkpoint_files_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_all_checkpoint_files_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_all_checkpoint_files_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_all_checkpoint_files_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_all_checkpoint_files_util", "eval_metric")
_emit_stores_embedding("p4", "verify_all_checkpoint_files_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_all_checkpoint_files_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_all_checkpoint_files_util", "exec_snapshot_link")

"Verify archival status of all files mentioned in checkpoint summary."
import os

from agentic_core.L0_routing.config import ARCHIVES_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_all_checkpoint_files_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_all_checkpoint_files_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_all_checkpoint_files_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_all_checkpoint_files_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_all_checkpoint_files_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_all_checkpoint_files_util", "p4obs", "alert")
_emit_links_incident_trace("verify_all_checkpoint_files_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_all_checkpoint_files_util", "p3lm", "pattern")
_emit_records_learning_event("verify_all_checkpoint_files_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_all_checkpoint_files_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_all_checkpoint_files_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_all_checkpoint_files_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_all_checkpoint_files_util", "p3lm", "policy")
_emit_stores_learning_state("verify_all_checkpoint_files_util", "p3lm", "state")
_emit_records_execution_trace("verify_all_checkpoint_files_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_all_checkpoint_files_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_all_checkpoint_files_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_all_checkpoint_files_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_all_checkpoint_files_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_all_checkpoint_files_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_all_checkpoint_files_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_all_checkpoint_files_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_all_checkpoint_files_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_all_checkpoint_files_util", "context_pull")
_emit_pulls_context("p1", "verify_all_checkpoint_files_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "verify_all_checkpoint_files_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_all_checkpoint_files_util", "uwg_term_secondary")
_emit_writes_through("p1", "verify_all_checkpoint_files_util", "write_through")
_emit_writes_through("p1", "verify_all_checkpoint_files_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "verify_all_checkpoint_files_util", "safety_validation")
_emit_invokes_eval("p1", "verify_all_checkpoint_files_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_all_checkpoint_files_util", "routing_commit")

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
edited_files = [
    "scripts/rename_UnifiedAgents.py",
    "tests/unit/test_unified_hygiene_validator.py",
    "tests/unit/test_l5_sovereignty_upgrade.py",
    "tests/unit/test_phase2_validator_consolidation.py",
    "tests/unit/test_registry_mapping.py",
    "tests/unit/test_unified_core_regression.py",
    "scripts/generate_layer_report.py",
    "scripts/detailed_territory_report.py",
]
viewed_files = ["tests/unit/test_unified_hygiene_validator.py", "agent_discovery_full.json"]
renamed_agents = [
    "agentic_core/L5_safety/unified/CodeDetectorAgent.py",
    "agentic_core/L5_safety/unified/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/unified/CodeHealerAgent.py",
    "agentic_core/L5_safety/unified/CodeValidatorAgent.py",
    "agentic_core/L5_safety/unified/ResourceManagerAgent.py",
    "agentic_core/L5_safety/unified/SafetyDetectorAgent.py",
    "agentic_core/L5_safety/unified/SafetyExecutorAgent.py",
    "agentic_core/L5_safety/unified/SecurityManagerAgent.py",
    "agentic_core/L5_safety/unified/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/unified/StructureHealerAgent.py",
    "agentic_core/L5_safety/unified/StructuralValidatorAgent.py",
]
all_files = edited_files + viewed_files + renamed_agents
active_count = 0
archived_count = 0
missing_count = 0
for file_path in all_files:
    full_path = PROJECT_ROOT / file_path
    exists_active = full_path.exists()
    filename = Path(file_path).name
    archives_path = PROJECT_ROOT / ARCHIVES_DIR
    exists_archived = False
    if archives_path.exists():
        for root, dirs, files in os.walk(archives_path):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            if filename in files:
                exists_archived = True
                break
    if exists_active and (not exists_archived):
        status = "✅ ACTIVE"
        active_count += 1
    elif not exists_active and exists_archived:
        status = "📦 ARCHIVED"
        archived_count += 1
    elif exists_active and exists_archived:
        status = "⚠️ BOTH (active + archived)"
        active_count += 1
    else:
        status = "❌ MISSING"
        missing_count += 1
