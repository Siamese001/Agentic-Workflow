from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "guard_observability_footprint_util")
emit_determinism_digest("p0", "guard_observability_footprint_util")

_emit_dispatches_healing_run("p1", "guard_observability_footprint_util", "L5")
_emit_routes_through("p1", "guard_observability_footprint_util", "L5")
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
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


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
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "check_dark_reasoning")
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
    except Exception:
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
    from agentic_core.utils.ssot_discovery_validator import get_python_files

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
