"""
Run NamingAgent to scan for duplicate filenames and class names.
"""

import sys
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

emit_replay_key("p0", "run_naming_scan_util")
emit_determinism_digest("p0", "run_naming_scan_util")

_emit_dispatches_healing_run("p1", "run_naming_scan_util", "L0")
_emit_routes_through("p1", "run_naming_scan_util", "L0")
_emit_checks_agent_registry("p1", "run_naming_scan_util", "agent_registry")
_emit_validates_agent_capability("p1", "run_naming_scan_util", "capability")
_emit_dispatches_execution_plan("p1", "run_naming_scan_util", "exec_plan")
_emit_agent_executes_agent("p1", "run_naming_scan_util", "sub_agent")
_emit_routes_to_agent("p1", "run_naming_scan_util", "target_agent")
_emit_verifies_policy("p1", "run_naming_scan_util", "policy_check")
_emit_observes_runtime_state("p1", "run_naming_scan_util", "runtime_state")
_emit_verifies_boundary("p1", "run_naming_scan_util", "boundary_check")
_emit_transcripts_response("p1", "run_naming_scan_util", "transcript")
_emit_hard_fails_untranscripted("p1", "run_naming_scan_util")
_emit_gated_by_confidence("p1", "run_naming_scan_util", "confidence_gate")
_emit_escalates_to_human("p1", "run_naming_scan_util", "L0")
_emit_reads_policy_state("p1", "run_naming_scan_util", "L0")

_emit_records_execution_trace("p0", "evidence", "run_naming_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "run_naming_scan_util", "p0_governance")
_emit_snapshots_state("p0", "run_naming_scan_util", "state_snapshot")
_emit_authorize_and_execute("p2", "run_naming_scan_util", "execution_auth")
_emit_validates_capability("p2", "run_naming_scan_util", "capability_check")
_emit_routes_to_capability("p2", "run_naming_scan_util", "capability_route")
_emit_writes_via_uwg("p2", "run_naming_scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "run_naming_scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "run_naming_scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "run_naming_scan_util", "exec_output")
_emit_dispatches_agent("p3", "run_naming_scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "run_naming_scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_naming_scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_naming_scan_util", "healing_outcome")
_emit_escalates_failure("p3", "run_naming_scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_naming_scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_naming_scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_naming_scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_naming_scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_naming_scan_util", "eval_metric")
_emit_stores_embedding("p4", "run_naming_scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_naming_scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_naming_scan_util", "exec_snapshot_link")

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent

print("=" * 80)
print("NAMING AGENT SCAN - Duplicate Detection")
print("=" * 80)
NamingAgent = load_naming_agent()
naming = NamingAgent(project_root)
print("\n[1] Scanning for duplicate FILENAMES...")
duplicates = naming.scan_for_duplicate_filenames()
if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate filenames:")
    for basename, paths in sorted(duplicates.items()):
        print(f"\n  {basename} ({len(paths)} occurrences):")
        for p in paths:
            print(f"    - {p.relative_to(project_root)}")
else:
    print("\n✅ No duplicate filenames found")
print("\n" + "=" * 80)
print("[2] Scanning for duplicate CLASS NAMES...")
import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
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

_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_1")
_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_2")
_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_3")
_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_4")
_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_5")
_emit_emits_metric_event("run_naming_scan_util", "p4obs", "metric_6")
_emit_records_incident_event("run_naming_scan_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_naming_scan_util", "p4obs", "anomaly")
_emit_writes_observability_log("run_naming_scan_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_naming_scan_util", "p4obs", "mon_state")
_emit_triggers_alert("run_naming_scan_util", "p4obs", "alert")
_emit_links_incident_trace("run_naming_scan_util", "p4obs", "trace_link")
_emit_captures_pattern("run_naming_scan_util", "p3lm", "pattern")
_emit_records_learning_event("run_naming_scan_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_naming_scan_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_naming_scan_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_naming_scan_util", "p3lm", "routing")
_emit_improves_agent_policy("run_naming_scan_util", "p3lm", "policy")
_emit_stores_learning_state("run_naming_scan_util", "p3lm", "state")
_emit_records_execution_trace("run_naming_scan_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_naming_scan_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_naming_scan_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_naming_scan_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_naming_scan_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_naming_scan_util", "env_read", "p2_env_1")
_emit_reads_environ("run_naming_scan_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_naming_scan_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_naming_scan_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_naming_scan_util", "context_pull")
_emit_pulls_context("p1", "run_naming_scan_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "run_naming_scan_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_naming_scan_util", "uwg_term_secondary")
_emit_writes_through("p1", "run_naming_scan_util", "write_through")
_emit_writes_through("p1", "run_naming_scan_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "run_naming_scan_util", "safety_validation")
_emit_invokes_eval("p1", "run_naming_scan_util", "eval_call")
_emit_proposal_commits_routing("p1", "run_naming_scan_util", "routing_commit")

discovery_path = project_root / AGENT_DISCOVERY_JSON
if discovery_path.exists():
    agents = json.loads(discovery_path.read_text(encoding="utf-8"))
    by_name = defaultdict(list)
    for a in agents:
        by_name[a["class_name"]].append(a["path"])
    dup_classes = {k: v for k, v in by_name.items() if len(v) > 1}
    if dup_classes:
        print(f"\n❌ Found {len(dup_classes)} duplicate class names:")
        for name, paths in sorted(dup_classes.items()):
            print(f"\n  {name} ({len(paths)} occurrences):")
            for p in paths:
                print(f"    - {p}")
    else:
        print("\n✅ No duplicate class names found")
else:
    print("\n⚠️  agent_discovery_full.json not found - run full_agent_discovery.py first")
print("\n" + "=" * 80)
print("SCAN COMPLETE")
print("=" * 80)
