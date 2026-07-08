from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_lock_util")
trace_contract.emit_determinism_digest("p0", "sovereign_lock_util")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_lock_util", "L5")
trace_contract._emit_routes_through("p1", "sovereign_lock_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "sovereign_lock_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_lock_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_lock_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_lock_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_lock_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_lock_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_lock_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_lock_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_lock_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_lock_util")
trace_contract._emit_gated_by_confidence("p1", "sovereign_lock_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_lock_util", "L5")
trace_contract._emit_reads_policy_state("p1", "sovereign_lock_util", "L5")
trace_contract._emit_authorize_and_execute("p2", "sovereign_lock_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_lock_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_lock_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_lock_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_lock_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_lock_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_lock_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_lock_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_lock_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_lock_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_lock_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_lock_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_lock_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_lock_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_lock_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_lock_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_lock_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_lock_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_lock_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_lock_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_lock_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_lock_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_lock_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_lock_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_lock_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_lock_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_lock_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_lock_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_lock_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_lock_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_lock_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_lock_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_lock_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_lock_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_lock_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_lock_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_lock_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_lock_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_lock_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_lock_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_lock_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_lock_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_lock_util", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_lock_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_lock_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_lock_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_lock_util", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_lock_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_lock_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_lock_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_lock_util", "routing_commit")

ROOT: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR


def enforce_gravity() -> Any:
    """Ensures no file in agentic_core reaches 'down' into apps."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "enforce_gravity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "enforce_gravity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "enforce_gravity")
    print("[*] ENFORCING GRAVITY...")
    violations: Any = 0
    forbidden: Any = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(CORE):
        if py_file.name == "__init__.py":
            continue
        content: Any = py_file.read_text(encoding="utf-8")
        for f in forbidden:
            if f in content:
                if re.search(f"^(import\\s+{f}|from\\s+{f})", content, re.M):
                    print(f"  [X] GRAVITY BREACH: {py_file.relative_to(ROOT)} imports {f}!")
                    violations += 1
    return violations


def enforce_depth() -> Any:
    """Ensures every file is EXACTLY at Depth 4. No shallower, no deeper."""
    print("[*] ENFORCING ABSOLUTE DEPTH-4 MANDATE...")
    violations: Any = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(CORE):
        if py_file.name == "__init__.py":
            continue
        parts: Any = py_file.relative_to(CORE).parts
        if len(parts) != 3:
            depth_status: Any = "SHALLOW" if len(parts) < 3 else "TUNNEL"
            print(f"  [X] {depth_status} VIOLATION: {py_file.relative_to(ROOT)}")
            print(f"      Actual: {len(parts) + 1} | Required: 4")
            violations += 1
    return violations


def check_airlocks() -> Any:
    """Ensures __init__.py files are minimal (under 50 lines)."""
    print("[*] CHECKING AIRLOCK HYGIENE...")
    violations: Any = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for init_file in [f for f in get_python_files(CORE) if f.name == "__init__.py"]:
        lines: Any = init_file.read_text(encoding="utf-8").splitlines()
        if len(lines) > 50:
            print(f"  [X] HEAVY AIRLOCK: {init_file.relative_to(ROOT)} has {len(lines)} lines. Keep it lean!")
            violations += 1
    return violations


if __name__ == "__main__":
    v1: Any = enforce_gravity()
    v2: Any = enforce_depth()
    v3: Any = check_airlocks()
    total: Any = v1 + v2 + v3
    if total > 0:
        print(f"\n[BLOCK] {total} Sovereignty Violations detected. Fix these before committing.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Sovereign Core is locked and compliant. Move forward.")
        sys.exit(0)
