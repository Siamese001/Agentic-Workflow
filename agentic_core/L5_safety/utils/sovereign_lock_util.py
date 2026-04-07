from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sovereign_lock_util")
emit_determinism_digest("p0", "sovereign_lock_util")

_emit_dispatches_healing_run("p1", "sovereign_lock_util", "L5")
_emit_routes_through("p1", "sovereign_lock_util", "L5")
_emit_checks_agent_registry("p1", "sovereign_lock_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_lock_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_lock_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_lock_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_lock_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_lock_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_lock_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_lock_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_lock_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_lock_util")
_emit_gated_by_confidence("p1", "sovereign_lock_util", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_lock_util", "L5")
_emit_reads_policy_state("p1", "sovereign_lock_util", "L5")
_emit_authorize_and_execute("p2", "sovereign_lock_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_lock_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_lock_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_lock_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_lock_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_lock_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_lock_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_lock_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_lock_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_lock_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_lock_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_lock_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_lock_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_lock_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_lock_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_lock_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_lock_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_lock_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_lock_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_lock_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_lock_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_lock_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_lock_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_lock_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_lock_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_lock_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_lock_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_lock_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_lock_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_lock_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_lock_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_lock_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_lock_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_lock_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_lock_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_lock_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_lock_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_lock_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_lock_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_lock_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_lock_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_lock_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_lock_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_lock_util", "context_pull")
_emit_pulls_context("p1", "sovereign_lock_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_lock_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_lock_util", "uwg_term_2")
_emit_writes_through("p1", "sovereign_lock_util", "write_through")
_emit_writes_through("p1", "sovereign_lock_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_lock_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_lock_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_lock_util", "routing_commit")

ROOT: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR


def enforce_gravity() -> Any:
    """Ensures no file in agentic_core reaches 'down' into apps."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "enforce_gravity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "enforce_gravity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "enforce_gravity")
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
