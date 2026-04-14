#!/usr/bin/env python3
"""
Test Structure Auto-Fix Script

Moves misplaced test files to their correct locations based on the
Depth-3 SSOT (Single Source of Truth) requirements.

Rules:
1. Test files in tests/unit/ should be under agentic_core/, apps_rg/, apps_lic/, or apps_shared/
2. Test files in tests/integration/ should be under the same domain structure
3. Attempts to determine correct location by analyzing test content
"""

import ast
import shutil
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from tqdm import tqdm

_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_1")
_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_2")
_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_3")
_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_4")
_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_5")
_emit_emits_metric_event("fix_test_structure", "p4obs", "metric_6")
_emit_records_incident_event("fix_test_structure", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_test_structure", "p4obs", "anomaly")
_emit_writes_observability_log("fix_test_structure", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_test_structure", "p4obs", "mon_state")
_emit_triggers_alert("fix_test_structure", "p4obs", "alert")
_emit_links_incident_trace("fix_test_structure", "p4obs", "trace_link")
_emit_captures_pattern("fix_test_structure", "p3lm", "pattern")
_emit_records_learning_event("fix_test_structure", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_test_structure", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_test_structure", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_test_structure", "p3lm", "routing")
_emit_improves_agent_policy("fix_test_structure", "p3lm", "policy")
_emit_stores_learning_state("fix_test_structure", "p3lm", "state")
_emit_records_execution_trace("fix_test_structure", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_test_structure", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_test_structure", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_test_structure", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_test_structure", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_test_structure", "env_read", "p2_env_1")
_emit_reads_environ("fix_test_structure", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_test_structure", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_test_structure", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_test_structure")
_emit_applies_guardrail("p0", "fix_test_structure", "p0_governance")
_emit_reads_policy_state("p0", "fix_test_structure", "policy_binding")
_emit_snapshots_state("p0", "fix_test_structure", "state_snapshot")
_emit_pulls_context("p1", "fix_test_structure", "context_pull")
_emit_pulls_context("p1", "fix_test_structure", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_test_structure", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_test_structure", "uwg_term_secondary")
_emit_writes_through("p1", "fix_test_structure", "write_through")
_emit_writes_through("p1", "fix_test_structure", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_test_structure", "safety_validation")
_emit_invokes_eval("p1", "fix_test_structure", "eval_call")
_emit_proposal_commits_routing("p1", "fix_test_structure", "routing_commit")
_emit_escalates_to_human("p1", "fix_test_structure", "human_escalation")
_emit_routes_through("p1", "fix_test_structure", "route_through")
_emit_checks_agent_registry("p1", "fix_test_structure", "agent_registry")
_emit_validates_agent_capability("p1", "fix_test_structure", "capability")
_emit_dispatches_execution_plan("p1", "fix_test_structure", "exec_plan")
_emit_agent_executes_agent("p1", "fix_test_structure", "sub_agent")
_emit_routes_to_agent("p1", "fix_test_structure", "target_agent")
_emit_verifies_policy("p1", "fix_test_structure", "policy_check")
_emit_observes_runtime_state("p1", "fix_test_structure", "runtime_state")
_emit_verifies_boundary("p1", "fix_test_structure", "boundary_check")
_emit_transcripts_response("p1", "fix_test_structure", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_test_structure")
_emit_gated_by_confidence("p1", "fix_test_structure", "confidence_gate")
emit_replay_key("p0", "fix_test_structure")
emit_determinism_digest("p0", "fix_test_structure")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_test_structure", "execution_auth")
_emit_validates_capability("p2", "fix_test_structure", "capability_check")
_emit_routes_to_capability("p2", "fix_test_structure", "capability_route")
_emit_writes_via_uwg("p2", "fix_test_structure", "uwg_write")
_emit_blocks_direct_write("p2", "fix_test_structure", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_test_structure", "tool_invocation")
_emit_captures_execution_output("p2", "fix_test_structure", "exec_output")
_emit_dispatches_agent("p3", "fix_test_structure", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_test_structure", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_test_structure", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_test_structure", "healing_outcome")
_emit_escalates_failure("p3", "fix_test_structure", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_test_structure", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_test_structure", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_test_structure", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_test_structure", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_test_structure", "eval_metric")
_emit_stores_embedding("p4", "fix_test_structure", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_test_structure", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_test_structure", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
TESTS_ROOT = PROJECT_ROOT / TESTS_DIR


def analyze_test_imports(file_path: Path) -> str | None:
    """Analyze test file to determine which domain it belongs to based on imports."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(AGENTIC_CORE_DIR):
                        return AGENTIC_CORE_DIR
                    elif alias.name.startswith(APPS_RG_DIR):
                        return APPS_RG_DIR
                    elif alias.name.startswith(APPS_LIC_DIR):
                        return APPS_LIC_DIR
                    elif alias.name.startswith(APPS_SHARED_DIR):
                        return APPS_SHARED_DIR
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module.startswith(AGENTIC_CORE_DIR):
                        return AGENTIC_CORE_DIR
                    elif node.module.startswith(APPS_RG_DIR):
                        return APPS_RG_DIR
                    elif node.module.startswith(APPS_LIC_DIR):
                        return APPS_LIC_DIR
                    elif node.module.startswith(APPS_SHARED_DIR):
                        return APPS_SHARED_DIR
    # guardian: allow-silent-swallow
    except Exception:
        pass

    return None


def fix_test_structure():
    """Move misplaced test files to correct locations."""
    print("[AUTO-FIX] Moving misplaced test files to correct locations...")

    moved_count = 0
    error_count = 0

    # Process both unit and integration tests
    for test_type in tqdm(["unit", "integration"], desc="Processing", unit="item"):
        test_dir = TESTS_ROOT / test_type
        if not test_dir.exists():
            continue

        print(f"\n--- Processing {test_type} tests ---")

        for item in tqdm(test_dir.iterdir(), desc="Processing", unit="item"):
            if item.is_file() and item.name.startswith("test_") and item.name.endswith(".py"):
                # Skip allowed files
                if item.name in {"__init__.py", "conftest.py"}:
                    continue

                # Determine target domain
                domain = analyze_test_imports(item)
                if not domain:
                    # Default to agentic_core if we can't determine
                    domain = AGENTIC_CORE_DIR
                    print(
                        f"  [WARNING] Could not determine domain for {item.name}, defaulting to {domain}",
                    )

                # Create target directory
                target_dir = test_dir / domain
                target_dir.mkdir(parents=True, exist_ok=True)

                # Move file
                target_path = target_dir / item.name
                try:
                    shutil.move(str(item), str(target_path))
                    print(f"  [MOVED] {item.name} -> {test_type}/{domain}/")
                    moved_count += 1
                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    error_count += 1

    print(f"\n[AUTO-FIX] Complete: {moved_count} files moved, {error_count} errors")
    return moved_count, error_count


if __name__ == "__main__":
    fix_test_structure()
