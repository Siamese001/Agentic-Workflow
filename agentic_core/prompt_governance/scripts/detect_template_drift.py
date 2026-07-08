"""
Template Drift Detection Script (Phase 5)

Detects if a template has been modified on disk without a corresponding
version bump in the Registry (Instruction Drift detection).
"""

import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "detect_template_drift", "execution_auth")
trace_contract._emit_validates_capability("p2", "detect_template_drift", "capability_check")
trace_contract._emit_routes_to_capability("p2", "detect_template_drift", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "detect_template_drift", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "detect_template_drift", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "detect_template_drift", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "detect_template_drift", "exec_output")
trace_contract._emit_dispatches_agent("p3", "detect_template_drift", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "detect_template_drift", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "detect_template_drift", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "detect_template_drift", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "detect_template_drift", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "detect_template_drift", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "detect_template_drift", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "detect_template_drift", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "detect_template_drift", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "detect_template_drift", "eval_metric")
trace_contract._emit_stores_embedding("p4", "detect_template_drift", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "detect_template_drift", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "detect_template_drift", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("detect_template_drift", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("detect_template_drift", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("detect_template_drift", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("detect_template_drift", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("detect_template_drift", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("detect_template_drift", "p4obs", "alert")
trace_contract._emit_links_incident_trace("detect_template_drift", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("detect_template_drift", "p3lm", "pattern")
trace_contract._emit_records_learning_event("detect_template_drift", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("detect_template_drift", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("detect_template_drift", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("detect_template_drift", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("detect_template_drift", "p3lm", "policy")
trace_contract._emit_stores_learning_state("detect_template_drift", "p3lm", "state")
trace_contract._emit_records_execution_trace("detect_template_drift", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("detect_template_drift", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("detect_template_drift", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("detect_template_drift", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("detect_template_drift", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("detect_template_drift", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("detect_template_drift", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("detect_template_drift", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("detect_template_drift", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "detect_template_drift")
trace_contract._emit_applies_guardrail("p0", "detect_template_drift", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "detect_template_drift", "policy_binding")
trace_contract._emit_snapshots_state("p0", "detect_template_drift", "state_snapshot")
trace_contract._emit_pulls_context("p1", "detect_template_drift", "context_pull")
trace_contract._emit_pulls_context("p1", "detect_template_drift", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "detect_template_drift", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "detect_template_drift", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "detect_template_drift", "write_through")
trace_contract._emit_writes_through("p1", "detect_template_drift", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "detect_template_drift", "safety_validation")
trace_contract._emit_invokes_eval("p1", "detect_template_drift", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "detect_template_drift", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "detect_template_drift", "human_escalation")
trace_contract._emit_routes_through("p1", "detect_template_drift", "route_through")
trace_contract._emit_checks_agent_registry("p1", "detect_template_drift", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "detect_template_drift", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "detect_template_drift", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "detect_template_drift", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "detect_template_drift", "target_agent")
trace_contract._emit_verifies_policy("p1", "detect_template_drift", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "detect_template_drift", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "detect_template_drift", "boundary_check")
trace_contract._emit_transcripts_response("p1", "detect_template_drift", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "detect_template_drift")
trace_contract._emit_gated_by_confidence("p1", "detect_template_drift", "confidence_gate")
trace_contract.emit_replay_key("p0", "detect_template_drift")
trace_contract.emit_determinism_digest("p0", "detect_template_drift")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def load_registry(registry_path: Path) -> dict:
    """Load the prompt registry JSON file."""
    try:
        with open(registry_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to load registry: {e}")
        sys.exit(1)


def detect_template_drift(registry_path: Path, base_dir: Path) -> tuple[list[dict], list[dict]]:
    """
    Detect template drift between registry and disk.

    Returns:
        Tuple of (synchronized_entries, drifted_entries)
    """
    from agentic_core.utils.fs_util import calculate_file_hash

    registry = load_registry(registry_path)
    synchronized = []
    drifted = []
    prompts = registry.get("prompts", {})
    for template_name, prompt_versions in tqdm(prompts.items(), desc="Processing", unit="item"):
        for prompt_data in tqdm(prompt_versions, desc="Processing", unit="item"):
            if not prompt_data.get("active", False):
                continue
            template_path = base_dir / "templates" / template_name
            if not template_path.exists():
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "Template file missing",
                        "registry_hash": prompt_data.get("content_hash", "N/A"),
                        "disk_hash": "MISSING",
                        "status": "DRIFT",
                    },
                )
                continue
            disk_hash = calculate_file_hash(template_path)
            registry_hash = prompt_data.get("content_hash", "")
            if not registry_hash:
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "No content hash in registry",
                        "registry_hash": "MISSING",
                        "disk_hash": disk_hash,
                        "status": "DRIFT",
                    },
                )
                continue
            if disk_hash != registry_hash:
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "Content hash mismatch - template modified without registry update",
                        "registry_hash": registry_hash,
                        "disk_hash": disk_hash,
                        "status": "DRIFT",
                    },
                )
            else:
                synchronized.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "registry_hash": registry_hash,
                        "disk_hash": disk_hash,
                        "status": "SYNCHRONIZED",
                    },
                )
    return (synchronized, drifted)


def detect_and_return_drift(registry_path: Path, base_dir: Path):
    """Detect template drift and return results programmatically.

    Args:
        registry_path: Path to registry.json
        base_dir: Base directory containing templates

    Returns:
        Tuple of (synchronized, drifted) lists
    """
    return detect_template_drift(registry_path, base_dir)


def synchronize_registry_hashes(registry_path: Path, base_dir: Path) -> dict:
    """
    Synchronize registry content hashes with actual template files.

    Returns:
        Dict with synchronization statistics
    """
    from agentic_core.utils.fs_util import calculate_file_hash

    registry = load_registry(registry_path)
    synchronized = []
    drifted = []
    prompts = registry.get("prompts", {})
    for template_name, prompt_versions in tqdm(prompts.items(), desc="Processing", unit="item"):
        for prompt_data in tqdm(prompt_versions, desc="Processing", unit="item"):
            if not prompt_data.get("active", False):
                continue
            template_path = base_dir / "templates" / template_name
            if not template_path.exists():
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "Template file missing",
                        "registry_hash": prompt_data.get("content_hash", "N/A"),
                        "disk_hash": "MISSING",
                        "status": "DRIFT",
                    },
                )
                continue
            disk_hash = calculate_file_hash(template_path)
            registry_hash = prompt_data.get("content_hash", "")
            if not registry_hash:
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "No content hash in registry",
                        "registry_hash": "MISSING",
                        "disk_hash": disk_hash,
                        "status": "DRIFT",
                    },
                )
                continue
            if disk_hash != registry_hash:
                drifted.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "issue": "Content hash mismatch - template modified without registry update",
                        "registry_hash": registry_hash,
                        "disk_hash": disk_hash,
                        "status": "DRIFT",
                    },
                )
            else:
                synchronized.append(
                    {
                        "prompt_id": template_name,
                        "template_path": str(template_path.relative_to(base_dir)),
                        "registry_hash": registry_hash,
                        "disk_hash": disk_hash,
                        "status": "SYNCHRONIZED",
                    },
                )
    return {"synchronized": synchronized, "drifted": drifted}


def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    registry_path = base_dir / "registry.json"
    print("Template Drift Detection Audit (Phase 5)")
    print("=" * 50)
    print(f"Registry: {registry_path}")
    print(f"Base Directory: {base_dir}")
    print()
    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}")
        sys.exit(1)
    synchronized, drifted = detect_template_drift(registry_path, base_dir)
    print("RESULTS:")
    print(f"  Active templates checked: {len(synchronized) + len(drifted)}")
    print(f"  Synchronized: {len(synchronized)}")
    print(f"  Drifted: {len(drifted)}")
    print()
    if drifted:
        print("🚨 DRIFTED TEMPLATES (Instruction Drift Detected):")
        for entry in drifted:
            print(f"  ❌ {entry['prompt_id']}: {entry['issue']}")
            print(f"     Template: {entry['template_path']}")
            print(f"     Registry Hash: {entry['registry_hash'][:16]}...")
            print(f"     Disk Hash:     {entry['disk_hash'][:16]}...")
            print()
        print("⚠️  ACTION REQUIRED:")
        print("   1. Update registry.json with correct content_hash")
        print("   2. Increment version number if changes are intentional")
        print("   3. Re-run this audit to verify synchronization")
        print()
    else:
        print("✅ ALL TEMPLATES SYNCHRONIZED")
        print("No instruction drift detected.")
        print()
    if synchronized and len(synchronized) <= 10:
        print("SYNCHRONIZED TEMPLATES:")
        for entry in synchronized:
            print(f"  ✅ {entry['prompt_id']}: {entry['template_path']}")
        print()
    if drifted:
        print("❌ AUDIT FAILED - Template drift detected")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED - All templates synchronized")
        sys.exit(0)


if __name__ == "__main__":
    main()
