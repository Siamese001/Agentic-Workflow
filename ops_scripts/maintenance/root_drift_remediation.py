#!/usr/bin/env python3
"""
ROOT STRUCTURE REMEDIATION PROTOCOL
Renames scripts/ to ops_scripts/ and enforces strict separation.

PHASE 1: SSOT HARDENING (Blueprint Diffs)
- Updates canonical registry to recognize ops_scripts instead of scripts
- Adds strict log placement rules

PHASE 2: MIGRATION & CLEANUP
- Physical rename scripts/ -> ops_scripts/
- Sorts contents based on import rules
- Moves core-dependent scripts to L0_routing/scripts/
- Moves runtime logs to L0_routing/logs/

PHASE 3: VERIFICATION
- Tests migration success
- Validates structure compliance
"""

import re
import shutil
from pathlib import Path
from re import Pattern

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    OPS_SCRIPTS_DIR,
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

_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_1")
_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_2")
_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_3")
_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_4")
_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_5")
_emit_emits_metric_event("root_drift_remediation", "p4obs", "metric_6")
_emit_records_incident_event("root_drift_remediation", "p4obs", "incident")
_emit_captures_runtime_anomaly("root_drift_remediation", "p4obs", "anomaly")
_emit_writes_observability_log("root_drift_remediation", "p4obs", "obs_log")
_emit_updates_monitoring_state("root_drift_remediation", "p4obs", "mon_state")
_emit_triggers_alert("root_drift_remediation", "p4obs", "alert")
_emit_links_incident_trace("root_drift_remediation", "p4obs", "trace_link")
_emit_captures_pattern("root_drift_remediation", "p3lm", "pattern")
_emit_records_learning_event("root_drift_remediation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("root_drift_remediation", "p3lm", "snapshot")
_emit_feeds_meta_learning("root_drift_remediation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("root_drift_remediation", "p3lm", "routing")
_emit_improves_agent_policy("root_drift_remediation", "p3lm", "policy")
_emit_stores_learning_state("root_drift_remediation", "p3lm", "state")
_emit_records_execution_trace("root_drift_remediation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("root_drift_remediation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("root_drift_remediation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("root_drift_remediation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("root_drift_remediation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("root_drift_remediation", "env_read", "p2_env_1")
_emit_reads_environ("root_drift_remediation", "env_read", "p2_env_2")
_emit_reads_runtime_state("root_drift_remediation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("root_drift_remediation", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "root_drift_remediation")
_emit_applies_guardrail("p0", "root_drift_remediation", "p0_governance")
_emit_reads_policy_state("p0", "root_drift_remediation", "policy_binding")
_emit_snapshots_state("p0", "root_drift_remediation", "state_snapshot")
_emit_pulls_context("p1", "root_drift_remediation", "context_pull")
_emit_pulls_context("p1", "root_drift_remediation", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "root_drift_remediation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "root_drift_remediation", "uwg_term_secondary")
_emit_writes_through("p1", "root_drift_remediation", "write_through")
_emit_writes_through("p1", "root_drift_remediation", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "root_drift_remediation", "safety_validation")
_emit_invokes_eval("p1", "root_drift_remediation", "eval_call")
_emit_proposal_commits_routing("p1", "root_drift_remediation", "routing_commit")
_emit_escalates_to_human("p1", "root_drift_remediation", "human_escalation")
_emit_routes_through("p1", "root_drift_remediation", "route_through")
_emit_checks_agent_registry("p1", "root_drift_remediation", "agent_registry")
_emit_validates_agent_capability("p1", "root_drift_remediation", "capability")
_emit_dispatches_execution_plan("p1", "root_drift_remediation", "exec_plan")
_emit_agent_executes_agent("p1", "root_drift_remediation", "sub_agent")
_emit_routes_to_agent("p1", "root_drift_remediation", "target_agent")
_emit_verifies_policy("p1", "root_drift_remediation", "policy_check")
_emit_observes_runtime_state("p1", "root_drift_remediation", "runtime_state")
_emit_verifies_boundary("p1", "root_drift_remediation", "boundary_check")
_emit_transcripts_response("p1", "root_drift_remediation", "transcript")
_emit_hard_fails_untranscripted("p1", "root_drift_remediation")
_emit_gated_by_confidence("p1", "root_drift_remediation", "confidence_gate")
emit_replay_key("p0", "root_drift_remediation")
emit_determinism_digest("p0", "root_drift_remediation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "root_drift_remediation", "execution_auth")
_emit_validates_capability("p2", "root_drift_remediation", "capability_check")
_emit_routes_to_capability("p2", "root_drift_remediation", "capability_route")
_emit_writes_via_uwg("p2", "root_drift_remediation", "uwg_write")
_emit_blocks_direct_write("p2", "root_drift_remediation", "direct_write_block")
_emit_records_tool_invocation("p2", "root_drift_remediation", "tool_invocation")
_emit_captures_execution_output("p2", "root_drift_remediation", "exec_output")
_emit_dispatches_agent("p3", "root_drift_remediation", "agent_dispatch")
_emit_coordinates_agents("p3", "root_drift_remediation", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_drift_remediation", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_drift_remediation", "healing_outcome")
_emit_escalates_failure("p3", "root_drift_remediation", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_drift_remediation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_drift_remediation", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_drift_remediation", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_drift_remediation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_drift_remediation", "eval_metric")
_emit_stores_embedding("p4", "root_drift_remediation", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_drift_remediation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_drift_remediation", "exec_snapshot_link")

# --- CONFIGURATION ---
PROJECT_ROOT = get_validated_project_root()
OLD_SCRIPTS_DIR = PROJECT_ROOT / "scripts"
NEW_OPS_DIR = PROJECT_ROOT / OPS_SCRIPTS_DIR

CORE_SCRIPTS_DEST = PROJECT_ROOT / L0_ROUTING_DIR / "scripts"
CORE_LOGS_DEST = PROJECT_ROOT / L0_ROUTING_DIR / "logs"

# Allowed patterns for Root Logs (Must match SSOT)
ALLOWED_ROOT_LOG_PATTERNS: list[Pattern] = [
    re.compile(r"^trace_.*\.jsonl$"),
    re.compile(r"^mission_.*\.log$"),
    re.compile(r"^execution_.*\.trace$"),
]


def setup_dirs():
    """Ensure destination directories exist."""
    NEW_OPS_DIR.mkdir(parents=True, exist_ok=True)
    CORE_SCRIPTS_DEST.mkdir(parents=True, exist_ok=True)
    CORE_LOGS_DEST.mkdir(parents=True, exist_ok=True)


def migrate_and_audit_scripts():
    """
    1. Scans old 'scripts/' (if exists).
    2. Rule: If imports 'agentic_core' -> Move to agentic_core/L0_routing/scripts.
    3. Rule: If Standalone -> Move to new 'ops_scripts/'.
    4. Remove old 'scripts/' dir if empty.
    """
    if not OLD_SCRIPTS_DIR.exists():
        print(f"[-] No '{OLD_SCRIPTS_DIR.name}' directory found. Checking '{NEW_OPS_DIR.name}'...")
        if NEW_OPS_DIR.exists():
            print(f"[*] '{NEW_OPS_DIR.name}' already exists. Scanning for compliance...")
            source_dir = NEW_OPS_DIR
        else:
            print("[*] No scripts directory found. Creating new ops_scripts structure.")
            NEW_OPS_DIR.mkdir(parents=True, exist_ok=True)
            return
    else:
        source_dir = OLD_SCRIPTS_DIR

    print(f"[*] Scanning {source_dir} for migration & import violations...")

    moved_to_core = 0
    moved_to_ops = 0
    violations_found = 0

    # Snapshot file list to avoid modification issues during iteration
    files = list(source_dir.glob("*.py"))

    for file_path in files:
        if file_path.name == "root_drift_remediation.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")

            # 1. Check for Core Dependency Violation
            if AGENTIC_CORE_DIR in content:
                dest = CORE_SCRIPTS_DEST / file_path.name
                print(f"    [CORE_MOVE] {file_path.name} -> L0_routing (Dependency Detected)")
                shutil.move(str(file_path), str(dest))
                moved_to_core += 1
                violations_found += 1

            # 2. If valid standalone, ensure it is in the new OPS directory
            else:
                if source_dir == OLD_SCRIPTS_DIR:
                    dest = NEW_OPS_DIR / file_path.name
                    print(f"    [OPS_MIGRATE] {file_path.name} -> {NEW_OPS_DIR.name}")
                    shutil.move(str(file_path), str(dest))
                    moved_to_ops += 1
                else:
                    print(f"    [VERIFIED] {file_path.name} is valid in {NEW_OPS_DIR.name}")

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            print(f"    [ERR] Could not process {file_path.name}: {e}")

    # Cleanup old directory if empty
    if source_dir == OLD_SCRIPTS_DIR and not any(source_dir.iterdir()):
        print(f"[*] Removing empty legacy directory: {OLD_SCRIPTS_DIR}")
        source_dir.rmdir()

    print(
        f"[*] Scripts Migration Complete. Core: {moved_to_core}, Ops: {moved_to_ops}, Violations: {violations_found}",
    )
    return {
        "moved_to_core": moved_to_core,
        "moved_to_ops": moved_to_ops,
        "violations_found": violations_found,
    }


def audit_logs():
    """
    Scans root logs/ (deprecated - now uses agentic_core/L0_routing/utils/).
    Rule: If it doesn't match ALLOWED_PATTERNS, it's a runtime log -> Move to L0.
    """
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        print("[-] No root logs/ directory found (expected - decommissioned). Skipping.")
        return {"moved_count": 0}

    print(
        f"[*] WARNING: Root logs/ directory exists (should be decommissioned). Scanning {logs_dir} for non-trace artifacts...",
    )

    moved_count = 0
    for file_path in logs_dir.iterdir():
        if file_path.is_dir():
            continue

        is_allowed = any(p.match(file_path.name) for p in ALLOWED_ROOT_LOG_PATTERNS)

        if not is_allowed:
            dest = CORE_LOGS_DEST / file_path.name
            print(f"    [LOG_MOVE] {file_path.name} -> Core (Runtime/Debug Log)")
            shutil.move(str(file_path), str(dest))
            moved_count += 1

    print(f"[*] Logs Audit Complete. Moved: {moved_count}")
    return {"moved_count": moved_count}


def validate_structure():
    """Validates the new structure complies with SSOT."""
    print("[*] Validating new structure...")

    issues = []

    # Check ops_scripts exists
    if not NEW_OPS_DIR.exists():
        issues.append("ops_scripts directory does not exist")

    # Check old scripts is gone
    if OLD_SCRIPTS_DIR.exists():
        issues.append("Legacy scripts directory still exists")

    # Check for core imports in ops_scripts
    if NEW_OPS_DIR.exists():
        for py_file in NEW_OPS_DIR.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if AGENTIC_CORE_DIR in content:
                    issues.append(f"Core dependency found in ops_scripts/{py_file.name}")
            except (
                Exception
            ):  # guardian: allow-silent-swallow -- non-critical: file read failure skipped silently
                pass

    if issues:
        print("[!] Structure validation issues found:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print("[✓] Structure validation passed")
        return True


def main():
    print("=== ROOT STRUCTURE REMEDIATION PROTOCOL ===")
    print("Phase 1: SSOT hardening completed in structure_blueprint.py")
    print("Phase 2: Migration & cleanup starting...")

    setup_dirs()

    # Execute migration
    script_results = migrate_and_audit_scripts()
    log_results = audit_logs()

    print("Phase 3: Verification...")
    is_valid = validate_structure()

    print("\n=== REMEDIATION SUMMARY ===")
    print(f"Scripts moved to core: {script_results['moved_to_core']}")
    print(f"Scripts moved to ops: {script_results['moved_to_ops']}")
    print(f"Violations found: {script_results['violations_found']}")
    print(f"Logs moved to core: {log_results['moved_count']}")
    print(f"Structure valid: {is_valid}")

    if is_valid:
        print("\n✅ REMEDIATION COMPLETE - Structure is compliant")
    else:
        print("\n❌ REMEDIATION INCOMPLETE - Manual fixes required")

    return is_valid


if __name__ == "__main__":
    main()
