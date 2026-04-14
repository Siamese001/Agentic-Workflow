"""Debug script to identify invocation pipeline discrepancy."""

import json
import sys
from pathlib import Path

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
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
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_1")
_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_2")
_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_3")
_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_4")
_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_5")
_emit_emits_metric_event("debug_invocation_pipeline_util", "p4obs", "metric_6")
_emit_records_incident_event("debug_invocation_pipeline_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("debug_invocation_pipeline_util", "p4obs", "anomaly")
_emit_writes_observability_log("debug_invocation_pipeline_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("debug_invocation_pipeline_util", "p4obs", "mon_state")
_emit_triggers_alert("debug_invocation_pipeline_util", "p4obs", "alert")
_emit_links_incident_trace("debug_invocation_pipeline_util", "p4obs", "trace_link")
_emit_captures_pattern("debug_invocation_pipeline_util", "p3lm", "pattern")
_emit_records_learning_event("debug_invocation_pipeline_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("debug_invocation_pipeline_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("debug_invocation_pipeline_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("debug_invocation_pipeline_util", "p3lm", "routing")
_emit_improves_agent_policy("debug_invocation_pipeline_util", "p3lm", "policy")
_emit_stores_learning_state("debug_invocation_pipeline_util", "p3lm", "state")
_emit_records_execution_trace("debug_invocation_pipeline_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("debug_invocation_pipeline_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("debug_invocation_pipeline_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("debug_invocation_pipeline_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("debug_invocation_pipeline_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("debug_invocation_pipeline_util", "env_read", "p2_env_1")
_emit_reads_environ("debug_invocation_pipeline_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("debug_invocation_pipeline_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("debug_invocation_pipeline_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "debug_invocation_pipeline_util")
emit_determinism_digest("p0", "debug_invocation_pipeline_util")

_emit_dispatches_healing_run("p1", "debug_invocation_pipeline_util", "L0")
_emit_routes_through("p1", "debug_invocation_pipeline_util", "L0")
_emit_checks_agent_registry("p1", "debug_invocation_pipeline_util", "agent_registry")
_emit_validates_agent_capability("p1", "debug_invocation_pipeline_util", "capability")
_emit_dispatches_execution_plan("p1", "debug_invocation_pipeline_util", "exec_plan")
_emit_agent_executes_agent("p1", "debug_invocation_pipeline_util", "sub_agent")
_emit_routes_to_agent("p1", "debug_invocation_pipeline_util", "target_agent")
_emit_verifies_policy("p1", "debug_invocation_pipeline_util", "policy_check")
_emit_observes_runtime_state("p1", "debug_invocation_pipeline_util", "runtime_state")
_emit_verifies_boundary("p1", "debug_invocation_pipeline_util", "boundary_check")
_emit_transcripts_response("p1", "debug_invocation_pipeline_util", "transcript")
_emit_hard_fails_untranscripted("p1", "debug_invocation_pipeline_util")
_emit_gated_by_confidence("p1", "debug_invocation_pipeline_util", "confidence_gate")
_emit_escalates_to_human("p1", "debug_invocation_pipeline_util", "L0")
_emit_reads_policy_state("p1", "debug_invocation_pipeline_util", "L0")
_emit_pulls_context("p1", "debug_invocation_pipeline_util", "context_pull")
_emit_pulls_context("p1", "debug_invocation_pipeline_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "debug_invocation_pipeline_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "debug_invocation_pipeline_util", "uwg_term_secondary")
_emit_writes_through("p1", "debug_invocation_pipeline_util", "write_through")
_emit_writes_through("p1", "debug_invocation_pipeline_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "debug_invocation_pipeline_util", "safety_validation")
_emit_invokes_eval("p1", "debug_invocation_pipeline_util", "eval_call")
_emit_proposal_commits_routing("p1", "debug_invocation_pipeline_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "debug_invocation_pipeline_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_invocation_pipeline_util", "p0_governance")
_emit_snapshots_state("p0", "debug_invocation_pipeline_util", "state_snapshot")
_emit_authorize_and_execute("p2", "debug_invocation_pipeline_util", "execution_auth")
_emit_validates_capability("p2", "debug_invocation_pipeline_util", "capability_check")
_emit_routes_to_capability("p2", "debug_invocation_pipeline_util", "capability_route")
_emit_writes_via_uwg("p2", "debug_invocation_pipeline_util", "uwg_write")
_emit_blocks_direct_write("p2", "debug_invocation_pipeline_util", "direct_write_block")
_emit_records_tool_invocation("p2", "debug_invocation_pipeline_util", "tool_invocation")
_emit_captures_execution_output("p2", "debug_invocation_pipeline_util", "exec_output")
_emit_dispatches_agent("p3", "debug_invocation_pipeline_util", "agent_dispatch")
_emit_coordinates_agents("p3", "debug_invocation_pipeline_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "debug_invocation_pipeline_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "debug_invocation_pipeline_util", "healing_outcome")
_emit_escalates_failure("p3", "debug_invocation_pipeline_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "debug_invocation_pipeline_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "debug_invocation_pipeline_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "debug_invocation_pipeline_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "debug_invocation_pipeline_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "debug_invocation_pipeline_util", "eval_metric")
_emit_stores_embedding("p4", "debug_invocation_pipeline_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "debug_invocation_pipeline_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "debug_invocation_pipeline_util", "exec_snapshot_link")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "agentic_core").exists():
            return candidate
    raise RuntimeError(f"Could not determine project root from {__file__}")


def main() -> int:
    project_root = _find_project_root()
    discovery_path = project_root / AGENT_DISCOVERY_JSON
    if not discovery_path.exists():
        print(f"[ERROR] Registry file not found: {discovery_path}")
        return 1

    with discovery_path.open(encoding="utf-8") as f:
        registry = json.load(f)

    print(f"JSON agents: {len(registry)}")
    registry_by_path = {}
    for entry in registry:
        rel = (entry.get("path") or "").replace("\\", "/")
        if rel:
            registry_by_path[rel] = entry

    print(f"Registry paths: {len(registry_by_path)}")
    inv_counts = {}
    for entry in registry:
        inv = entry.get("invocation", "Missing")
        inv_counts[inv] = inv_counts.get(inv, 0) + 1
    print(f"JSON invocation counts: {inv_counts}")

    all_agents = []
    for agent in registry:
        path_str = agent.get("path", "")
        if path_str:
            full_path = project_root / path_str
            if full_path.exists():
                all_agents.append(full_path)

    print(f"Resolved agent paths: {len(all_agents)}")
    found = 0
    not_found = 0
    not_found_paths = []
    invocation_from_lookup = {"Yes": 0, "No (missing super)": 0, "Inherited": 0}

    for agent in all_agents:
        rel_path = str(agent.relative_to(project_root)).replace("\\", "/")
        entry = registry_by_path.get(rel_path)
        if entry:
            found += 1
            inv = entry.get("invocation", "Inherited")
            invocation_from_lookup[inv] = invocation_from_lookup.get(inv, 0) + 1
        else:
            not_found += 1
            not_found_paths.append(rel_path)

    print(f"\nLookup results: found={found}, not_found={not_found}")
    if not_found_paths:
        print("Not found paths:")
        for rel_path in not_found_paths[:10]:
            print(f"  {rel_path}")
    print(f"Invocation from lookup: {invocation_from_lookup}")

    yes = invocation_from_lookup.get("Yes", 0)
    inh = invocation_from_lookup.get("Inherited", 0)
    no = invocation_from_lookup.get("No (missing super)", 0)
    total = yes + inh + no
    if total > 0:
        pct = (yes + inh) / total * 100
        print(f"\nExpected Invocation %: {pct:.1f}%")

    print("\nSample registry paths:")
    for rel_path in list(registry_by_path.keys())[:5]:
        print(f"  {rel_path}")

    print("\nSample agent rel_paths:")
    for agent in all_agents[:5]:
        print(f"  {str(agent.relative_to(project_root)).replace(chr(92), '/')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
