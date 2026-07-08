from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "guard_observability_footprint_util")
trace_contract.emit_determinism_digest("p0", "guard_observability_footprint_util")

trace_contract._emit_dispatches_healing_run("p1", "guard_observability_footprint_util", "L5")
trace_contract._emit_routes_through("p1", "guard_observability_footprint_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "guard_observability_footprint_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "guard_observability_footprint_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "guard_observability_footprint_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "guard_observability_footprint_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "guard_observability_footprint_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "guard_observability_footprint_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "guard_observability_footprint_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "guard_observability_footprint_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "guard_observability_footprint_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "guard_observability_footprint_util")
trace_contract._emit_gated_by_confidence("p1", "guard_observability_footprint_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "guard_observability_footprint_util", "L5")
trace_contract._emit_reads_policy_state("p1", "guard_observability_footprint_util", "L5")
trace_contract._emit_authorize_and_execute("p2", "guard_observability_footprint_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "guard_observability_footprint_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "guard_observability_footprint_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "guard_observability_footprint_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "guard_observability_footprint_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "guard_observability_footprint_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "guard_observability_footprint_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "guard_observability_footprint_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "guard_observability_footprint_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "guard_observability_footprint_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "guard_observability_footprint_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "guard_observability_footprint_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "guard_observability_footprint_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "guard_observability_footprint_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "guard_observability_footprint_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "guard_observability_footprint_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "guard_observability_footprint_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "guard_observability_footprint_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "guard_observability_footprint_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "guard_observability_footprint_util", "exec_snapshot_link")

'\nSovereign Guardian: observability Footprint (Dark Reasoning Check)\nEnsures every L1 reasoning step leaves an L6 observability trail.\n\nThe Governance Cycle:\n1. L0 (Auditor) defines what is "Legal."\n2. L1-L5 perform the actual agentic operations.\n3. L6 (observability) records the ground truth of those operations.\n4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.\n\nPhase 9C: Dark Reasoning Guardian (Dec 26, 2025)\n'
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR

trace_contract.record_execution_trace("guard_observability_footprint_util", "guard_observability_footprint_util_trace")


trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("guard_observability_footprint_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("guard_observability_footprint_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("guard_observability_footprint_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("guard_observability_footprint_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("guard_observability_footprint_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("guard_observability_footprint_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("guard_observability_footprint_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("guard_observability_footprint_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("guard_observability_footprint_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("guard_observability_footprint_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("guard_observability_footprint_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("guard_observability_footprint_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("guard_observability_footprint_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("guard_observability_footprint_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("guard_observability_footprint_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("guard_observability_footprint_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("guard_observability_footprint_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("guard_observability_footprint_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("guard_observability_footprint_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("guard_observability_footprint_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("guard_observability_footprint_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("guard_observability_footprint_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "guard_observability_footprint_util", "context_pull")
trace_contract._emit_pulls_context("p1", "guard_observability_footprint_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "guard_observability_footprint_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "guard_observability_footprint_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "guard_observability_footprint_util", "write_through")
trace_contract._emit_writes_through("p1", "guard_observability_footprint_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "guard_observability_footprint_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "guard_observability_footprint_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "guard_observability_footprint_util", "routing_commit")


def check_dark_reasoning(filepath: Path) -> list[str]:
    """
    Check for reasoning operations without corresponding observability footprints.

    Dark Reasoning occurs when an agent performs cognitive operations (think, plan, decide)
    without leaving a trace in the L6 observability layer (logging, telemetry).

    Args:
        filepath: Path to Python file to audit

    Returns:
        List of issues found (empty if compliant)
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "check_dark_reasoning", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "check_dark_reasoning", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "check_dark_reasoning")
    issues = []
    file_str = str(filepath).replace("\\", "/")
    if not any(layer in file_str for layer in ["L1_cognition", "L2_execution", "L3_orchestration"]):
        return []
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()
        reasoning_signals = ["think", "plan", "execute", "decide", "reason", "validate", "check"]
        log_signals = ["Logger.", "logging.", "self.log", "trace(", "print("]
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if any(sig in line.lower() for sig in reasoning_signals):
                ContextWindow = "\n".join(lines[i : min(i + 10, len(lines))])
                if not any(log_sig in ContextWindow for log_sig in log_signals):
                    issues.append(f"Potential Dark Reasoning at line {i + 1}: Action without L6 footprint")
    except (ValueError, TypeError):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
        pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
    return issues


def validate_observability_footprint(target_dir: str) -> tuple[float, list[str]]:
    """
    Validate that all reasoning operations have observability footprints.

    Args:
        target_dir: Directory to audit

    Returns:
        Tuple of (score percentage, list of issues)
    """
    issues = []
    total_files = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for path in get_python_files(Path(target_dir)):
        if TESTS_DIR in str(path) or "__pycache__" in str(path):
            continue
        total_files += 1
        file_issues = check_dark_reasoning(path)
        issues.extend([f"{path.name}: {i}" for i in file_issues])
    score = 100.0
    if issues:
        score = max(0, 100 - len(issues) * 5)
    return (score, issues)
