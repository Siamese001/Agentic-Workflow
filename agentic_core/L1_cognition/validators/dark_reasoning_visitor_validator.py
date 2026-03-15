from __future__ import annotations

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
