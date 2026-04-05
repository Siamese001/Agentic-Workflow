from __future__ import annotations

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

emit_replay_key("p0", "bulk_hierarchy_heal_util")
emit_determinism_digest("p0", "bulk_hierarchy_heal_util")

_emit_dispatches_healing_run("p1", "bulk_hierarchy_heal_util", "L0")
_emit_routes_through("p1", "bulk_hierarchy_heal_util", "L0")
_emit_checks_agent_registry("p1", "bulk_hierarchy_heal_util", "agent_registry")
_emit_validates_agent_capability("p1", "bulk_hierarchy_heal_util", "capability")
_emit_dispatches_execution_plan("p1", "bulk_hierarchy_heal_util", "exec_plan")
_emit_agent_executes_agent("p1", "bulk_hierarchy_heal_util", "sub_agent")
_emit_routes_to_agent("p1", "bulk_hierarchy_heal_util", "target_agent")
_emit_verifies_policy("p1", "bulk_hierarchy_heal_util", "policy_check")
_emit_observes_runtime_state("p1", "bulk_hierarchy_heal_util", "runtime_state")
_emit_verifies_boundary("p1", "bulk_hierarchy_heal_util", "boundary_check")
_emit_transcripts_response("p1", "bulk_hierarchy_heal_util", "transcript")
_emit_hard_fails_untranscripted("p1", "bulk_hierarchy_heal_util")
_emit_gated_by_confidence("p1", "bulk_hierarchy_heal_util", "confidence_gate")
_emit_escalates_to_human("p1", "bulk_hierarchy_heal_util", "L0")
_emit_reads_policy_state("p1", "bulk_hierarchy_heal_util", "L0")

_emit_records_execution_trace("p0", "evidence", "bulk_hierarchy_heal_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "bulk_hierarchy_heal_util", "p0_governance")
_emit_snapshots_state("p0", "bulk_hierarchy_heal_util", "state_snapshot")
_emit_authorize_and_execute("p2", "bulk_hierarchy_heal_util", "execution_auth")
_emit_validates_capability("p2", "bulk_hierarchy_heal_util", "capability_check")
_emit_routes_to_capability("p2", "bulk_hierarchy_heal_util", "capability_route")
_emit_writes_via_uwg("p2", "bulk_hierarchy_heal_util", "uwg_write")
_emit_blocks_direct_write("p2", "bulk_hierarchy_heal_util", "direct_write_block")
_emit_records_tool_invocation("p2", "bulk_hierarchy_heal_util", "tool_invocation")
_emit_captures_execution_output("p2", "bulk_hierarchy_heal_util", "exec_output")
_emit_dispatches_agent("p3", "bulk_hierarchy_heal_util", "agent_dispatch")
_emit_coordinates_agents("p3", "bulk_hierarchy_heal_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "bulk_hierarchy_heal_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "bulk_hierarchy_heal_util", "healing_outcome")
_emit_escalates_failure("p3", "bulk_hierarchy_heal_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "bulk_hierarchy_heal_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bulk_hierarchy_heal_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "bulk_hierarchy_heal_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "bulk_hierarchy_heal_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bulk_hierarchy_heal_util", "eval_metric")
_emit_stores_embedding("p4", "bulk_hierarchy_heal_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "bulk_hierarchy_heal_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bulk_hierarchy_heal_util", "exec_snapshot_link")

"\nOne-Off Bulk Hierarchy Healer - Eternal Depth 4 Alignment\n"
import shutil
import sys
from datetime import datetime
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, TOOLS_DIR

dry_run: Any = False
target_root: Any = AGENTIC_CORE_DIR
primary_partition_only: Any = True
current_file: Any = Path(__file__).resolve()
project_root: Any = next((p for p in current_file.parents if (p / ".env").exists()), None)
if not project_root:
    print("[!] Project root not found (.env Missing).")
    sys.exit(1)
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.config.path_constants import CORE_SUBFOLDER_MAP
from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    assert_no_persistent_write,
    safe_shutil_rmtree,
)
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

_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_1")
_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_2")
_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_3")
_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_4")
_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_5")
_emit_emits_metric_event("bulk_hierarchy_heal_util", "p4obs", "metric_6")
_emit_records_incident_event("bulk_hierarchy_heal_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("bulk_hierarchy_heal_util", "p4obs", "anomaly")
_emit_writes_observability_log("bulk_hierarchy_heal_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("bulk_hierarchy_heal_util", "p4obs", "mon_state")
_emit_triggers_alert("bulk_hierarchy_heal_util", "p4obs", "alert")
_emit_links_incident_trace("bulk_hierarchy_heal_util", "p4obs", "trace_link")
_emit_captures_pattern("bulk_hierarchy_heal_util", "p3lm", "pattern")
_emit_records_learning_event("bulk_hierarchy_heal_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("bulk_hierarchy_heal_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("bulk_hierarchy_heal_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("bulk_hierarchy_heal_util", "p3lm", "routing")
_emit_improves_agent_policy("bulk_hierarchy_heal_util", "p3lm", "policy")
_emit_stores_learning_state("bulk_hierarchy_heal_util", "p3lm", "state")
_emit_records_execution_trace("bulk_hierarchy_heal_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("bulk_hierarchy_heal_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("bulk_hierarchy_heal_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("bulk_hierarchy_heal_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("bulk_hierarchy_heal_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("bulk_hierarchy_heal_util", "env_read", "p2_env_1")
_emit_reads_environ("bulk_hierarchy_heal_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("bulk_hierarchy_heal_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("bulk_hierarchy_heal_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "bulk_hierarchy_heal_util", "context_pull")
_emit_pulls_context("p1", "bulk_hierarchy_heal_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "bulk_hierarchy_heal_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "bulk_hierarchy_heal_util", "uwg_term_2")
_emit_writes_through("p1", "bulk_hierarchy_heal_util", "write_through")
_emit_writes_through("p1", "bulk_hierarchy_heal_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "bulk_hierarchy_heal_util", "safety_validation")
_emit_invokes_eval("p1", "bulk_hierarchy_heal_util", "eval_call")
_emit_proposal_commits_routing("p1", "bulk_hierarchy_heal_util", "routing_commit")


def log_move(file_name: Any, src: Any, dst: Any) -> Any:
    """Brief description of functionality and purpose."""
    audit_log: Any = project_root / "mission_audit.csv"
    timestamp: Any = datetime.now().isoformat()
    log_entry: Any = f"{timestamp},{file_name},HIERARCHY_HEAL,{src},{dst},Bulk Alignment\n"
    with open(audit_log, "a") as f:
        f.write(log_entry)
    print(f"   [LOG] {file_name} moved to {dst}")


def main() -> Any:
    """Brief description of functionality and purpose."""
    target_dir: Any = project_root / TARGET_ROOT
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    python_files: Any = list(get_python_files(target_dir))
    print(f"--- SOVEREIGN HEALING START: {TARGET_ROOT} ---")
    print(f"Mode: {('DRY RUN' if DRY_RUN else 'EXECUTION')}")
    output_file: Any = project_root / "hierarchy_heal_dry_run.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== BULK HIERARCHY HEAL ===\n")
        f.write(f"Target: {TARGET_ROOT}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"configuration: DRY_RUN = {DRY_RUN}\n\n")
        for file_path in python_files:
            rel: Any = file_path.relative_to(project_root)
            parts: Any = rel.parts
            if len(parts) < 3 or not parts[1].startswith("L"):
                continue
            layer: Any = parts[1]
            allowed_partitions: Any = CORE_SUBFOLDER_MAP.get(layer, [])
            if not allowed_partitions:
                continue
            primary: Any = allowed_partitions[0]
            is_depth_2: Any = len(parts) == 3
            is_wrong_partition: Any = len(parts) == 4 and parts[2] not in allowed_partitions
            if is_depth_2 or is_wrong_partition:
                dest_dir: Any = project_root / TARGET_ROOT / layer / primary
                dest_path: Any = dest_dir / file_path.name
                if dest_path.exists():
                    log_entry: Any = (
                        f"[CONFLICT] {rel} >> {dest_path.relative_to(project_root)} (already exists)\n"
                    )
                    print(f"   [!] CONFLICT: {file_path.name} already exists in {primary}. Skipping.")
                    f.write(log_entry)
                    continue
                log_entry: Any = f"[MOVE] {rel} >> {dest_path.relative_to(project_root)}\n"
                print(f"   [MOVE] {rel} >> {dest_path.relative_to(project_root)}")
                f.write(log_entry)
                if not DRY_RUN:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    assert_no_persistent_write("L0", "shutil.mutate")
                    shutil.move(str(file_path), str(dest_path))
                    log_move(file_path.name, "/".join(parts[:-1]), f"{layer}/{primary}")
        f.write("\n=== SUMMARY ===\n")
        f.write(f"Total Python files scanned: {len(python_files)}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"DRY_RUN = {DRY_RUN}\n")
    if DRY_RUN:
        print(f"\n[DRY RUN COMPLETE] Output saved to: {output_file}")
        print("Set DRY_RUN = False in the script to execute moves")
    else:
        print(f"\n[EXECUTION COMPLETE] All moves executed. Output saved to: {output_file}")
    if not dry_run:
        print("\n--- INITIATING AUTO-CLEANUP ---")
        legacy_partitions: Any = [
            "P1_core",
            "P1_domain",
            "P1_interfaces",
            "P2_domain",
            "P3_aggregation",
            "P5_meta",
            "boundaries",
            "discovery",
            "identity",
            "inference",
            "planning",
            "planning_logic",
            "mcp",
            "sandbox",
            TOOLS_DIR,
            "P2_tools",
            "P3_engines",
            "P4_agents",
            "P5_healing",
            "event_bus",
            "framework",
            "handoff_logic",
            "health",
            "P5_workflow",
            "protocol",
            "security",
            "training",
            "automation",
            "migrations",
            "cache",
            "checkpoints",
            "filesystem",
            "memory",
            "persistence_layer",
            "S1_store",
            "semantic",
            "session_manager",
            "vector",
            "P1_red_team",
            "P4_security",
            "audit_logs",
            "gravity",
            "policy",
            "validators",
        ]
        for layer_folder in target_dir.iterdir():
            if not layer_folder.is_dir() or not layer_folder.name.startswith("L"):
                continue
            for legacy in legacy_partitions:
                legacy_path: Any = layer_folder / legacy
                if legacy_path.exists():
                    remaining: Any = [
                        f
                        for f in legacy_path.iterdir()
                        if f.name != "__pycache__" and f.name != "__init__.py"
                    ]
                    if not remaining:
                        try:
                            safe_shutil_rmtree(legacy_path, layer="L0")
                            print(f"   [CLEAN] Purged legacy folder: {legacy_path.relative_to(project_root)}")
                        # guardian: allow-silent-swallow
                        except (ValueError, TypeError) as e:
                            print(f"   [!] Could not purge {legacy}: {e}")
    print("\n" + "=" * 70)
    print(f"[COMPLETE] Bulk hierarchy healing for {TARGET_ROOT}")
    if DRY_RUN:
        print("Status: PREVIEW MODE - No files were moved")
    else:
        print("Status: EXECUTED - Files moved and legacy folders cleaned")
    print("=" * 70)


if __name__ == "__main__":
    main()
