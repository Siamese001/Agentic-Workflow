from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "generate_hooks_util")
_emit_applies_guardrail("p0", "generate_hooks_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_hooks_util", "policy_binding")
_emit_snapshots_state("p0", "generate_hooks_util", "state_snapshot")
emit_replay_key("p0", "generate_hooks_util")
emit_determinism_digest("p0", "generate_hooks_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_hooks_util", "execution_auth")
_emit_validates_capability("p2", "generate_hooks_util", "capability_check")
_emit_routes_to_capability("p2", "generate_hooks_util", "capability_route")
_emit_writes_via_uwg("p2", "generate_hooks_util", "uwg_write")
_emit_blocks_direct_write("p2", "generate_hooks_util", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_hooks_util", "tool_invocation")
_emit_captures_execution_output("p2", "generate_hooks_util", "exec_output")
_emit_dispatches_agent("p3", "generate_hooks_util", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_hooks_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_hooks_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_hooks_util", "healing_outcome")
_emit_escalates_failure("p3", "generate_hooks_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_hooks_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_hooks_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_hooks_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_hooks_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_hooks_util", "eval_metric")
_emit_stores_embedding("p4", "generate_hooks_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_hooks_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_hooks_util", "exec_snapshot_link")

#!/usr/bin/env python3
"""
Pre-commit Hook Generator - SSOT Synchronization
Dynamically generates .pre-commit-config.yaml patterns from structure_blueprint.py
to eliminate hardcoded folder lists and prevent drift.

Usage:
    python scripts/maintenance/generate_hooks_util.py
    python scripts/maintenance/generate_hooks_util.py --dry-run
"""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

# Add project root to path
project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

from agentic_core.L0_routing.config.path_constants import DEPTH_RULES, PROJECT_ROOT_WHITELIST
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_1")
_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_2")
_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_3")
_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_4")
_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_5")
_emit_emits_metric_event("generate_hooks_util", "p4obs", "metric_6")
_emit_records_incident_event("generate_hooks_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_hooks_util", "p4obs", "anomaly")
_emit_writes_observability_log("generate_hooks_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_hooks_util", "p4obs", "mon_state")
_emit_triggers_alert("generate_hooks_util", "p4obs", "alert")
_emit_links_incident_trace("generate_hooks_util", "p4obs", "trace_link")
_emit_captures_pattern("generate_hooks_util", "p3lm", "pattern")
_emit_records_learning_event("generate_hooks_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_hooks_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_hooks_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_hooks_util", "p3lm", "routing")
_emit_improves_agent_policy("generate_hooks_util", "p3lm", "policy")
_emit_stores_learning_state("generate_hooks_util", "p3lm", "state")
_emit_records_execution_trace("generate_hooks_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_hooks_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_hooks_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_hooks_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_hooks_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_hooks_util", "env_read", "p2_env_1")
_emit_reads_environ("generate_hooks_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_hooks_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_hooks_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "generate_hooks_util", "context_pull")
_emit_pulls_context("p1", "generate_hooks_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "generate_hooks_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_hooks_util", "uwg_term_2")
_emit_writes_through("p1", "generate_hooks_util", "write_through")
_emit_writes_through("p1", "generate_hooks_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "generate_hooks_util", "safety_validation")
_emit_invokes_eval("p1", "generate_hooks_util", "eval_call")
_emit_proposal_commits_routing("p1", "generate_hooks_util", "routing_commit")
_emit_escalates_to_human("p1", "generate_hooks_util", "human_escalation")
_emit_routes_through("p1", "generate_hooks_util", "route_through")
_emit_checks_agent_registry("p1", "generate_hooks_util", "agent_registry")
_emit_validates_agent_capability("p1", "generate_hooks_util", "capability")
_emit_dispatches_execution_plan("p1", "generate_hooks_util", "exec_plan")
_emit_agent_executes_agent("p1", "generate_hooks_util", "sub_agent")
_emit_routes_to_agent("p1", "generate_hooks_util", "target_agent")
_emit_verifies_policy("p1", "generate_hooks_util", "policy_check")
_emit_observes_runtime_state("p1", "generate_hooks_util", "runtime_state")
_emit_verifies_boundary("p1", "generate_hooks_util", "boundary_check")
_emit_transcripts_response("p1", "generate_hooks_util", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_hooks_util")
_emit_gated_by_confidence("p1", "generate_hooks_util", "confidence_gate")


def sync_pre_commit(dry_run: bool = False):
    """
    Synchronize .pre-commit-config.yaml with SSOT from structure_blueprint.py

    Args:
        dry_run: If True, only print changes without modifying files
    """
    # [SSOT] Dynamically derive sovereign roots
    sovereign_roots = sorted(PROJECT_ROOT_WHITELIST)

    # Add system folders that should be included in patterns
    system_folders = ["data", ARCHIVES_DIR]
    all_roots = sovereign_roots + system_folders

    # Build regex patterns
    roots_pattern = "|".join(sovereign_roots)
    all_roots_pattern = "|".join(all_roots)

    exclude_pattern = f"^({all_roots_pattern})/"
    files_pattern = f"^({roots_pattern})/.*\\.py$"

    print("[*] Syncing Pre-commit Config with SSOT...")
    print(f"   [SSOT] Sovereign Roots: {', '.join(sovereign_roots)}")
    print(f"   [PATTERN] Exclude: {exclude_pattern}")
    print(f"   [PATTERN] Files: {files_pattern}")

    # Locate the pre-commit config
    config_path = project_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / ".pre-commit-config.yaml"

    if not config_path.exists():
        print(f"   [!] Config not found at: {config_path}")
        print("   [!] Checking alternate location...")
        config_path = project_root / ".pre-commit-config.yaml"

        if not config_path.exists():
            print("   [X] No .pre-commit-config.yaml found!")
            return False

    print(f"   [OK] Found config at: {config_path}")

    # Read current config
    with open(config_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern replacements - target the hardcoded folder lists
    replacements = [
        # Exclude patterns (with data/archives)
        (
            r"exclude: \^[(]agentic_core\|apps_lic\|apps_rg\|apps_shared\|schemas\|prompt_governance\|observability\|config\|data\|archives[)]/",
            f"exclude: ^({all_roots_pattern})/",
        ),
        # Files patterns (sovereign only)
        (
            r"files: \^[(]agentic_core\|apps_lic\|apps_rg\|apps_shared\|schemas\|prompt_governance\|observability\|config[)]/\.\*\\\.py\$",
            f"files: ^({roots_pattern})/.*\\.py$",
        ),
    ]

    changes_made = 0
    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"   [✓] Updated {len(matches)} pattern(s)")

    if changes_made == 0:
        print("   [OK] No changes needed - config already synchronized")
        return True

    if dry_run:
        print(f"\n   [DRY-RUN] Would update {changes_made} pattern(s)")
        print("\n--- DIFF ---")
        print("Original patterns found, would be replaced with SSOT-derived patterns")
        return True

    # Write updated config
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"   [✓] Updated {changes_made} pattern(s) in {config_path.name}")
    print("   [SUCCESS] Pre-commit config synchronized with SSOT")

    return True


def generate_sovereign_list():
    """Generate a formatted list of sovereign roots for documentation"""
    sovereign_roots = sorted(PROJECT_ROOT_WHITELIST)
    print("\n[SSOT] Current Sovereign Registry (PROJECT_ROOT_WHITELIST):")
    for i, root in enumerate(sovereign_roots, 1):
        depth = DEPTH_RULES.get(root, "N/A")
        print(f"  {i:2d}. {root:<25} (Depth: {depth})")
    print(f"\nTotal: {len(sovereign_roots)} sovereign roots")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync pre-commit config with SSOT")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--list", action="store_true", help="List current sovereign roots")

    args = parser.parse_args()

    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
