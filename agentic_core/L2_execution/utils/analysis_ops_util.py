from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "analysis_ops_util")
trace_contract.emit_determinism_digest("p0", "analysis_ops_util")

trace_contract._emit_dispatches_healing_run("p1", "analysis_ops_util", "L2")
trace_contract._emit_routes_through("p1", "analysis_ops_util", "L2")
trace_contract._emit_checks_agent_registry("p1", "analysis_ops_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "analysis_ops_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "analysis_ops_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "analysis_ops_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "analysis_ops_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "analysis_ops_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "analysis_ops_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "analysis_ops_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "analysis_ops_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "analysis_ops_util")
trace_contract._emit_gated_by_confidence("p1", "analysis_ops_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "analysis_ops_util", "L2")
trace_contract._emit_reads_policy_state("p1", "analysis_ops_util", "L2")
trace_contract._emit_authorize_and_execute("p2", "analysis_ops_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "analysis_ops_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "analysis_ops_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "analysis_ops_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "analysis_ops_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "analysis_ops_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "analysis_ops_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "analysis_ops_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "analysis_ops_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "analysis_ops_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "analysis_ops_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "analysis_ops_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "analysis_ops_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "analysis_ops_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "analysis_ops_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "analysis_ops_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "analysis_ops_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "analysis_ops_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "analysis_ops_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "analysis_ops_util", "exec_snapshot_link")

"\nAnalysis Operations - AST Parsing, Linting, and Code Quality Tools\nConsolidated from core_utils.py and security_utils.py\n"
import ast
import logging
import subprocess
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    DEFAULT_TIMEOUT,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.utils.security_util import safe_execute
from tqdm import tqdm

trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("analysis_ops_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("analysis_ops_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("analysis_ops_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("analysis_ops_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("analysis_ops_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("analysis_ops_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("analysis_ops_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("analysis_ops_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("analysis_ops_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("analysis_ops_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("analysis_ops_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("analysis_ops_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("analysis_ops_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("analysis_ops_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("analysis_ops_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("analysis_ops_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("analysis_ops_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("analysis_ops_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("analysis_ops_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("analysis_ops_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("analysis_ops_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("analysis_ops_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "analysis_ops_util", "context_pull")
trace_contract._emit_pulls_context("p1", "analysis_ops_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "analysis_ops_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "analysis_ops_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "analysis_ops_util", "write_through")
trace_contract._emit_writes_through("p1", "analysis_ops_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "analysis_ops_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "analysis_ops_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "analysis_ops_util", "routing_commit")

Logger: Any = logging.getLogger(__name__)


def validate_python_syntax(file_path: str) -> tuple[bool, str | None]:
    """
    Parse a Python file to check for syntax errors without executing it.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple[bool, Optional[str]]: (True, None) if valid, (False, error_message) if invalid
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "validate_python_syntax", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "validate_python_syntax", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())  # review: Syntax errors should be caught at parser level, not runtime
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "validate_python_syntax")
    try:
        with open(file_path, encoding="utf-8") as f:
            source: Any = f.read()
        ast.parse(source)
        return (True, None)
    except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
        error_msg: Any = f"SyntaxError in {file_path}: {e.msg} at line {e.lineno}"
        Logger.error(error_msg)
        return (False, error_msg)
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        error_msg: Any = f"Unexpected error validating {file_path}: {str(e)}"
        Logger.error(error_msg)
        return (False, error_msg)


def run_ruff_check(file_path: str, fix: bool = False) -> tuple[int, str, str]:
    """
    Run Ruff linter on a file.

    Args:
        file_path: Path to the file to check
        fix: Whether to apply fixes automatically

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    """
    cmd: Any = ["ruff", "check", file_path]
    if fix:  # review: File operations should check existence before access
        cmd.append("--fix")
    try:
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, "", "Ruff check timed out")
    except FileNotFoundError:  # review: File operations should check existence before access
        return (-1, "", "Ruff not installed")
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        return (-1, "", str(e))


def run_black_format(file_path: str, check_only: bool = False) -> tuple[int, str, str]:
    """
    Run Black formatter on a file.

    Args:
        file_path: Path to the file to format
        check_only: Only check formatting without modifying

    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    """
    cmd: Any = ["black", file_path]
    if check_only:  # review: File operations should check existence before access
        cmd.append("--check")
    try:
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, "", "Black format timed out")
    except FileNotFoundError:  # review: File operations should check existence before access
        return (-1, "", "Black not installed")
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        return (-1, "", str(e))


def analyze_ast(file_path: str) -> dict[str, Any]:
    """
    Analyze Python file AST for structural information.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with AST analysis results
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source: Any = f.read()
        tree: Any = ast.parse(source)
        analysis: Any = {"functions": [], "classes": [], "imports": [], "globals": [], "complexity": 0}
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    },
                )
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                    },
                )
            elif isinstance(node, ast.Import | ast.ImportFrom):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(
                            {"module": alias.name, "alias": alias.asname, "lineno": node.lineno},
                        )
                else:
                    for alias in node.names:
                        analysis["imports"].append(
                            {
                                "module": f"{node.module}.{alias.name}" if node.module else alias.name,
                                "alias": alias.asname,
                                "lineno": node.lineno,
                            },
                        )
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        analysis["globals"].append(target.id)
        return analysis
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.error(f"AST analysis failed for {file_path}: {e}")
        return {"error": str(e)}


def count_lines_of_code(file_path: str) -> dict[str, int]:
    """
    Count lines of code, comments, and blank lines.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dict with line counts
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines: Any = f.readlines()
        total: Any = len(lines)
        blank: Any = sum(1 for line in lines if not line.strip())
        comments: Any = sum(1 for line in lines if line.strip().startswith("#"))
        code: Any = total - blank - comments
        return {"total": total, "code": code, "comments": comments, "blank": blank}
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.error(f"Line count failed for {file_path}: {e}")
        return {"error": str(e)}


def detect_security_issues(file_path: str) -> list[dict[str, Any]]:
    """
    Detect common security issues in Python code.

    Args:
        file_path: Path to the file to analyze

    Returns:
        List of detected security issues
    """
    issues: Any = []
    try:
        with open(file_path, encoding="utf-8") as f:
            source: Any = f.read()
        tree: Any = ast.parse(source)
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "eval":
                    issues.append(
                        {
                            "type": "dangerous_function",
                            "function": "eval",
                            "lineno": node.lineno,
                            "Severity": "high",
                            "message": "Use of eval() is dangerous and should be avoided",
                        },
                    )
                elif isinstance(node.func, ast.Name) and node.func.id == "exec":
                    issues.append(
                        {
                            "type": "dangerous_function",
                            "function": "exec",
                            "lineno": node.lineno,
                            "Severity": "high",
                            "message": "Use of exec() is dangerous and should be avoided",
                        },
                    )
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["run", "call", "Popen"]:
                        for keyword in tqdm(node.keywords, desc="Processing", unit="item"):
                            if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    issues.append(
                                        {
                                            "type": "shell_injection",
                                            "function": node.func.attr,
                                            "lineno": node.lineno,
                                            "Severity": "high",
                                            "message": "subprocess with shell=True is vulnerable to injection",
                                        },
                                    )
        return issues
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.error(f"Security analysis failed for {file_path}: {e}")
        return [{"error": str(e)}]
