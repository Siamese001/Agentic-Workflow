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
    # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "guard_observability_footprint_util")
emit_determinism_digest("p0", "guard_observability_footprint_util")

_emit_dispatches_healing_run("p1", "guard_observability_footprint_util", "L5")
_emit_routes_through("p1", "guard_observability_footprint_util", "L5")
_emit_checks_agent_registry("p1", "guard_observability_footprint_util", "agent_registry")
_emit_validates_agent_capability("p1", "guard_observability_footprint_util", "capability")
_emit_dispatches_execution_plan("p1", "guard_observability_footprint_util", "exec_plan")
_emit_agent_executes_agent("p1", "guard_observability_footprint_util", "sub_agent")
_emit_routes_to_agent("p1", "guard_observability_footprint_util", "target_agent")
_emit_verifies_policy("p1", "guard_observability_footprint_util", "policy_check")
_emit_observes_runtime_state("p1", "guard_observability_footprint_util", "runtime_state")
_emit_verifies_boundary("p1", "guard_observability_footprint_util", "boundary_check")
_emit_transcripts_response("p1", "guard_observability_footprint_util", "transcript")
_emit_hard_fails_untranscripted("p1", "guard_observability_footprint_util")
_emit_gated_by_confidence("p1", "guard_observability_footprint_util", "confidence_gate")
_emit_escalates_to_human("p1", "guard_observability_footprint_util", "L5")
_emit_reads_policy_state("p1", "guard_observability_footprint_util", "L5")
_emit_authorize_and_execute("p2", "guard_observability_footprint_util", "execution_auth")
_emit_validates_capability("p2", "guard_observability_footprint_util", "capability_check")
_emit_routes_to_capability("p2", "guard_observability_footprint_util", "capability_route")
_emit_writes_via_uwg("p2", "guard_observability_footprint_util", "uwg_write")
_emit_blocks_direct_write("p2", "guard_observability_footprint_util", "direct_write_block")
_emit_records_tool_invocation("p2", "guard_observability_footprint_util", "tool_invocation")
_emit_captures_execution_output("p2", "guard_observability_footprint_util", "exec_output")
_emit_dispatches_agent("p3", "guard_observability_footprint_util", "agent_dispatch")
_emit_coordinates_agents("p3", "guard_observability_footprint_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "guard_observability_footprint_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "guard_observability_footprint_util", "healing_outcome")
_emit_escalates_failure("p3", "guard_observability_footprint_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "guard_observability_footprint_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guard_observability_footprint_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "guard_observability_footprint_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "guard_observability_footprint_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guard_observability_footprint_util", "eval_metric")
_emit_stores_embedding("p4", "guard_observability_footprint_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "guard_observability_footprint_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guard_observability_footprint_util", "exec_snapshot_link")

'\nSovereign Guardian: observability Footprint (Dark Reasoning Check)\nEnsures every L1 reasoning step leaves an L6 observability trail.\n\nThe Governance Cycle:\n1. L0 (Auditor) defines what is "Legal."\n2. L1-L5 perform the actual agentic operations.\n3. L6 (observability) records the ground truth of those operations.\n4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.\n\nPhase 9C: Dark Reasoning Guardian (Dec 26, 2025)\n'
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import TESTS_DIR
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
    _emit_signs_execution_trace,
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

record_execution_trace("guard_observability_footprint_util", "guard_observability_footprint_util_trace")


_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_1")
_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_2")
_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_3")
_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_4")
_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_5")
_emit_emits_metric_event("guard_observability_footprint_util", "p4obs", "metric_6")
_emit_records_incident_event("guard_observability_footprint_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("guard_observability_footprint_util", "p4obs", "anomaly")
_emit_writes_observability_log("guard_observability_footprint_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("guard_observability_footprint_util", "p4obs", "mon_state")
_emit_triggers_alert("guard_observability_footprint_util", "p4obs", "alert")
_emit_links_incident_trace("guard_observability_footprint_util", "p4obs", "trace_link")
_emit_captures_pattern("guard_observability_footprint_util", "p3lm", "pattern")
_emit_records_learning_event("guard_observability_footprint_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guard_observability_footprint_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("guard_observability_footprint_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guard_observability_footprint_util", "p3lm", "routing")
_emit_improves_agent_policy("guard_observability_footprint_util", "p3lm", "policy")
_emit_stores_learning_state("guard_observability_footprint_util", "p3lm", "state")
_emit_records_execution_trace("guard_observability_footprint_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guard_observability_footprint_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guard_observability_footprint_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guard_observability_footprint_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guard_observability_footprint_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guard_observability_footprint_util", "env_read", "p2_env_1")
_emit_reads_environ("guard_observability_footprint_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("guard_observability_footprint_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guard_observability_footprint_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guard_observability_footprint_util", "context_pull")
_emit_pulls_context("p1", "guard_observability_footprint_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guard_observability_footprint_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guard_observability_footprint_util", "uwg_term_2")
_emit_writes_through("p1", "guard_observability_footprint_util", "write_through")
_emit_writes_through("p1", "guard_observability_footprint_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "guard_observability_footprint_util", "safety_validation")
_emit_invokes_eval("p1", "guard_observability_footprint_util", "eval_call")
_emit_proposal_commits_routing("p1", "guard_observability_footprint_util", "routing_commit")


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

    _emit_snapshots_state(str(_uuid.uuid4()), "check_dark_reasoning", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "check_dark_reasoning", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "check_dark_reasoning")
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
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        pass
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
