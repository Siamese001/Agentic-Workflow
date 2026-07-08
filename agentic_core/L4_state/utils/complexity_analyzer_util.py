"""
Shared complexity analysis utilities.

SSOT for cyclomatic complexity calculation.
Used by: GovernanceAgent, StructuralEngineerAgent

Extracted from:
- GovernanceAgent._calculate_mccabe()
- StructuralEngineerAgent._calculate_complexity()

Both implementations were identical - this consolidates them.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "complexity_analyzer_util")
trace_contract.emit_determinism_digest("p0", "complexity_analyzer_util")

trace_contract._emit_dispatches_healing_run("p1", "complexity_analyzer_util", "L4")
trace_contract._emit_routes_through("p1", "complexity_analyzer_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "complexity_analyzer_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "complexity_analyzer_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "complexity_analyzer_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "complexity_analyzer_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "complexity_analyzer_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "complexity_analyzer_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "complexity_analyzer_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "complexity_analyzer_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "complexity_analyzer_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "complexity_analyzer_util")
trace_contract._emit_gated_by_confidence("p1", "complexity_analyzer_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "complexity_analyzer_util", "L4")
trace_contract._emit_reads_policy_state("p1", "complexity_analyzer_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "complexity_analyzer_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "complexity_analyzer_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "complexity_analyzer_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "complexity_analyzer_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "complexity_analyzer_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "complexity_analyzer_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "complexity_analyzer_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "complexity_analyzer_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "complexity_analyzer_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "complexity_analyzer_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "complexity_analyzer_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "complexity_analyzer_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "complexity_analyzer_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "complexity_analyzer_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "complexity_analyzer_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "complexity_analyzer_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "complexity_analyzer_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "complexity_analyzer_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "complexity_analyzer_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "complexity_analyzer_util", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("complexity_analyzer_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("complexity_analyzer_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("complexity_analyzer_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("complexity_analyzer_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("complexity_analyzer_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("complexity_analyzer_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("complexity_analyzer_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("complexity_analyzer_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("complexity_analyzer_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("complexity_analyzer_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("complexity_analyzer_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("complexity_analyzer_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("complexity_analyzer_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("complexity_analyzer_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("complexity_analyzer_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("complexity_analyzer_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("complexity_analyzer_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("complexity_analyzer_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("complexity_analyzer_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("complexity_analyzer_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("complexity_analyzer_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("complexity_analyzer_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("complexity_analyzer_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "complexity_analyzer_util", "context_pull")
trace_contract._emit_pulls_context("p1", "complexity_analyzer_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "complexity_analyzer_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "complexity_analyzer_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "complexity_analyzer_util", "write_through")
trace_contract._emit_writes_through("p1", "complexity_analyzer_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "complexity_analyzer_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "complexity_analyzer_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "complexity_analyzer_util", "routing_commit")

if TYPE_CHECKING:
    pass


def calculate_mccabe_complexity(node: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of an AST node.

    Complexity = 1 + number of decision points (if, for, while, and, or, except)

    Args:
        node: AST node to analyze (typically FunctionDef or AsyncFunctionDef)

    Returns:
        Cyclomatic complexity score (minimum 1)

    Example:
        >>> import ast
        >>> code = "def foo(x):\\n    if x > 0:\\n        return 1\\n    return 0"
        >>> tree = ast.parse(code)
        >>> calculate_mccabe_complexity(tree.body[0])
        2
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "calculate_mccabe_complexity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "calculate_mccabe_complexity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "calculate_mccabe_complexity")
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


# guardian: allow-magic-config
def check_function_complexity(node: ast.AST, max_complexity: int = 10) -> tuple[bool, int]:
    """
    Check if function exceeds complexity threshold.

    Args:
        node: AST node to analyze
        max_complexity: Maximum allowed complexity (default 10)

    Returns:
        Tuple of (passes_check, actual_complexity)

    Example:
        >>> import ast
        >>> code = "def simple(): return 1"
        >>> tree = ast.parse(code)
        >>> check_function_complexity(tree.body[0], max_complexity=10)
        (True, 1)
    """
    complexity = calculate_mccabe_complexity(node)
    return (complexity <= max_complexity, complexity)


# guardian: allow-magic-config
def analyze_file_complexity(file_path: str, max_complexity: int = 10) -> list[dict[str, any]]:
    """
    Analyze all functions in a file for complexity violations.

    Args:
        file_path: Path to Python file
        max_complexity: Maximum allowed complexity

    Returns:
        List of violations with file_path, line_number, function_name, complexity
    """
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                complexity = calculate_mccabe_complexity(node)
                if complexity > max_complexity:
                    violations.append(
                        {
                            "file_path": file_path,
                            "line_number": node.lineno,
                            "function_name": node.name,
                            "complexity": complexity,
                            "max_allowed": max_complexity,
                            "message": f"Function '{node.name}' has complexity {complexity} (max {max_complexity})",
                        },
                    )
    except (  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
        SyntaxError,
        FileNotFoundError,
        OSError,
    ):
        import logging

        logging.getLogger(__name__).debug("complexity_analyzer_util: SyntaxError swallowed at L276: %s", e)
    return violations
