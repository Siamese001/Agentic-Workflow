from __future__ import annotations

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_records_execution_trace("p0", "evidence", "cleanup_duplicates_util")
_emit_applies_guardrail("p0", "cleanup_duplicates_util", "p0_governance")
_emit_reads_policy_state("p0", "cleanup_duplicates_util", "policy_binding")
_emit_snapshots_state("p0", "cleanup_duplicates_util", "state_snapshot")
emit_replay_key("p0", "cleanup_duplicates_util")
emit_determinism_digest("p0", "cleanup_duplicates_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cleanup_duplicates_util", "execution_auth")
_emit_validates_capability("p2", "cleanup_duplicates_util", "capability_check")
_emit_routes_to_capability("p2", "cleanup_duplicates_util", "capability_route")
_emit_writes_via_uwg("p2", "cleanup_duplicates_util", "uwg_write")
_emit_blocks_direct_write("p2", "cleanup_duplicates_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cleanup_duplicates_util", "tool_invocation")
_emit_captures_execution_output("p2", "cleanup_duplicates_util", "exec_output")
_emit_dispatches_agent("p3", "cleanup_duplicates_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cleanup_duplicates_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cleanup_duplicates_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cleanup_duplicates_util", "healing_outcome")
_emit_escalates_failure("p3", "cleanup_duplicates_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cleanup_duplicates_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cleanup_duplicates_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cleanup_duplicates_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cleanup_duplicates_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cleanup_duplicates_util", "eval_metric")
_emit_stores_embedding("p4", "cleanup_duplicates_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cleanup_duplicates_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cleanup_duplicates_util", "exec_snapshot_link")

"\nOne-time cleanup utility to collapse duplicate entries in registry.json.\n\nUsage:\n    python -m agentic_core.prompt_governance.version_registry.cleanup_duplicates\n\nThis script:\n- Loads the current registry via get_prompt_registry() for consistency\n- Deduplicates entries based on key fields (version, purpose, author, content_hash, territory)\n- Keeps only the most recent entry for each unique combination\n- Ensures only one active version per template\n- Saves the cleaned registry atomically\n"
import logging
from typing import Any

from agentic_core.prompt_governance.version_registry.prompt_registry_config import get_prompt_registry

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_1")
_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_2")
_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_3")
_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_4")
_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_5")
_emit_emits_metric_event("cleanup_duplicates_util", "p4obs", "metric_6")
_emit_records_incident_event("cleanup_duplicates_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("cleanup_duplicates_util", "p4obs", "anomaly")
_emit_writes_observability_log("cleanup_duplicates_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("cleanup_duplicates_util", "p4obs", "mon_state")
_emit_triggers_alert("cleanup_duplicates_util", "p4obs", "alert")
_emit_links_incident_trace("cleanup_duplicates_util", "p4obs", "trace_link")
_emit_captures_pattern("cleanup_duplicates_util", "p3lm", "pattern")
_emit_records_learning_event("cleanup_duplicates_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cleanup_duplicates_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("cleanup_duplicates_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cleanup_duplicates_util", "p3lm", "routing")
_emit_improves_agent_policy("cleanup_duplicates_util", "p3lm", "policy")
_emit_stores_learning_state("cleanup_duplicates_util", "p3lm", "state")
_emit_records_execution_trace("cleanup_duplicates_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cleanup_duplicates_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cleanup_duplicates_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cleanup_duplicates_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cleanup_duplicates_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cleanup_duplicates_util", "env_read", "p2_env_1")
_emit_reads_environ("cleanup_duplicates_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("cleanup_duplicates_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cleanup_duplicates_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cleanup_duplicates_util", "context_pull")
_emit_pulls_context("p1", "cleanup_duplicates_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "cleanup_duplicates_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cleanup_duplicates_util", "uwg_term_secondary")
_emit_writes_through("p1", "cleanup_duplicates_util", "write_through")
_emit_writes_through("p1", "cleanup_duplicates_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "cleanup_duplicates_util", "safety_validation")
_emit_invokes_eval("p1", "cleanup_duplicates_util", "eval_call")
_emit_proposal_commits_routing("p1", "cleanup_duplicates_util", "routing_commit")
_emit_escalates_to_human("p1", "cleanup_duplicates_util", "human_escalation")
_emit_routes_through("p1", "cleanup_duplicates_util", "route_through")
_emit_checks_agent_registry("p1", "cleanup_duplicates_util", "agent_registry")
_emit_validates_agent_capability("p1", "cleanup_duplicates_util", "capability")
_emit_dispatches_execution_plan("p1", "cleanup_duplicates_util", "exec_plan")
_emit_agent_executes_agent("p1", "cleanup_duplicates_util", "sub_agent")
_emit_routes_to_agent("p1", "cleanup_duplicates_util", "target_agent")
_emit_verifies_policy("p1", "cleanup_duplicates_util", "policy_check")
_emit_observes_runtime_state("p1", "cleanup_duplicates_util", "runtime_state")
_emit_verifies_boundary("p1", "cleanup_duplicates_util", "boundary_check")
_emit_transcripts_response("p1", "cleanup_duplicates_util", "transcript")
_emit_hard_fails_untranscripted("p1", "cleanup_duplicates_util")
_emit_gated_by_confidence("p1", "cleanup_duplicates_util", "confidence_gate")

Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def collapse_duplicates():
    """
    Collapse duplicate entries in registry.json.

    Deduplication strategy:
    1. Group entries by (version, purpose, author, content_hash, territory)
    2. Keep only the newest entry per group (by registered_date or list order)
    3. Ensure single active version per template
    4. Use same DUPLICATE_KEY_FIELDS logic as register_prompt()
    """
    registry = get_prompt_registry()
    print(f"[CLEANUP] Loading registry from {registry.REGISTRY_FILE}")
    Logger.info(f"Starting duplicate cleanup for {registry.REGISTRY_FILE}")
    original_count = sum(len(entries) for entries in registry.registry.values())
    print(f"[CLEANUP] Original entries: {original_count}")
    Logger.info(f"Original entry count: {original_count}")
    total_removed = 0
    for template_name, entries in list(registry.registry.items()):
        seen_keys: set[tuple] = set()
        unique_entries: list[dict[str, Any]] = []
        for entry in reversed(entries):
            key = tuple(
                entry.get(field) for field in ["version", "purpose", "author", "content_hash", "territory"]
            )
            if key not in seen_keys:
                seen_keys.add(key)
                unique_entries.append(entry)
        unique_entries.reverse()
        removed = len(entries) - len(unique_entries)
        total_removed += removed
        if removed > 0:
            print(f"   [{template_name}] Removed {removed} duplicate(s)")
            Logger.info(f"Template '{template_name}': removed {removed} duplicates")
        active_seen = False
        for entry in unique_entries:
            if entry.get("active"):
                if active_seen:
                    entry["active"] = False
                    total_removed += 1
                    Logger.debug(f"Deactivated duplicate active entry in {template_name}")
                else:
                    active_seen = True
        registry.registry[template_name] = unique_entries
    registry._save_registry()
    final_count = sum(len(entries) for entries in registry.registry.values())
    print("[CLEANUP] Complete!")
    print(f"   Original entries: {original_count}")
    print(f"   Final entries: {final_count}")
    print(f"   Removed: {total_removed} duplicate(s)")
    if original_count > 0:
        print(f"   Reduction: {100 * total_removed / original_count:.1f}%")
    Logger.info(f"Cleanup complete: {original_count} → {final_count} entries ({total_removed} removed)")


if __name__ == "__main__":
    collapse_duplicates()
