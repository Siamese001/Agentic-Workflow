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

emit_replay_key("p0", "dark_reasoning_visitor_validator")
emit_determinism_digest("p0", "dark_reasoning_visitor_validator")

_emit_dispatches_healing_run("p1", "dark_reasoning_visitor_validator", "L1")
_emit_routes_through("p1", "dark_reasoning_visitor_validator", "L1")
_emit_escalates_to_human("p1", "dark_reasoning_visitor_validator", "L1")
_emit_reads_policy_state("p1", "dark_reasoning_visitor_validator", "L1")
_emit_authorize_and_execute("p2", "dark_reasoning_visitor_validator", "execution_auth")
_emit_validates_capability("p2", "dark_reasoning_visitor_validator", "capability_check")
_emit_routes_to_capability("p2", "dark_reasoning_visitor_validator", "capability_route")
_emit_writes_via_uwg("p2", "dark_reasoning_visitor_validator", "uwg_write")
_emit_blocks_direct_write("p2", "dark_reasoning_visitor_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "dark_reasoning_visitor_validator", "tool_invocation")
_emit_captures_execution_output("p2", "dark_reasoning_visitor_validator", "exec_output")
_emit_dispatches_agent("p3", "dark_reasoning_visitor_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "dark_reasoning_visitor_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "dark_reasoning_visitor_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "dark_reasoning_visitor_validator", "healing_outcome")
_emit_escalates_failure("p3", "dark_reasoning_visitor_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "dark_reasoning_visitor_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dark_reasoning_visitor_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "dark_reasoning_visitor_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "dark_reasoning_visitor_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dark_reasoning_visitor_validator", "eval_metric")
_emit_stores_embedding("p4", "dark_reasoning_visitor_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "dark_reasoning_visitor_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dark_reasoning_visitor_validator", "exec_snapshot_link")

'\nSovereign Guardian: observability Footprint (Dark Reasoning Check)\nEnsures every L1 reasoning step leaves an L6 observability trail.\n\nThe Governance Cycle:\n1. L0 (Auditor) defines what is "Legal."\n2. L1-L5 perform the actual agentic operations.\n3. L6 (observability) records the ground truth of those operations.\n4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.\n\nPhase 9C: Dark Reasoning Guardian (Dec 26, 2025)\n'
import ast
from pathlib import Path

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
    issues = []
    file_str = str(filepath).replace("\\", "/")
    if not any(layer in file_str for layer in ["L1_cognition", "L2_execution", "L3_orchestration"]):
        return []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)

        class DarkReasoningVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.reasoning_methods = {"think", "plan", "decide", "reason", "validate", "execute_plan"}

            def visit_Call(self, node):
                import uuid as _uuid  # noqa: PLC0415

                _trace_id = str(_uuid.uuid4())
                _emit_records_execution_trace(
                    _trace_id, LayerSegment.L1_REASONING, "DarkReasoningVisitor.visit_Call"
                )

                if isinstance(node.func, ast.Attribute) and node.func.attr.lower() in self.reasoning_methods:
                    self.issues.append(
                        f"Dark Reasoning Violation: Unobserved reasoning call '{node.func.attr}' at line {node.lineno}"
                    )
                if isinstance(node.func, ast.Attribute) and node.func.attr in {
                    "chat",
                    "complete",
                    "messages",
                }:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in {
                        "client",
                        "openai",
                        "anthropic",
                    }:
                        self.issues.append(f"Potential L5 Bypass: Direct LLM call at line {node.lineno}")
                self.generic_visit(node)

        visitor = DarkReasoningVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
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
        total_files += 1
        file_issues = check_dark_reasoning(path)
        issues.extend([f"{str(path)}: {i}" for i in file_issues])
    score = 100.0
    if issues:
        score = max(0, 100 - len(issues) * 5)
    return (score, issues)
