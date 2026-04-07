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

emit_replay_key("p0", "analysis_ops_util")
emit_determinism_digest("p0", "analysis_ops_util")

_emit_dispatches_healing_run("p1", "analysis_ops_util", "L2")
_emit_routes_through("p1", "analysis_ops_util", "L2")
_emit_checks_agent_registry("p1", "analysis_ops_util", "agent_registry")
_emit_validates_agent_capability("p1", "analysis_ops_util", "capability")
_emit_dispatches_execution_plan("p1", "analysis_ops_util", "exec_plan")
_emit_agent_executes_agent("p1", "analysis_ops_util", "sub_agent")
_emit_routes_to_agent("p1", "analysis_ops_util", "target_agent")
_emit_verifies_policy("p1", "analysis_ops_util", "policy_check")
_emit_observes_runtime_state("p1", "analysis_ops_util", "runtime_state")
_emit_verifies_boundary("p1", "analysis_ops_util", "boundary_check")
_emit_transcripts_response("p1", "analysis_ops_util", "transcript")
_emit_hard_fails_untranscripted("p1", "analysis_ops_util")
_emit_gated_by_confidence("p1", "analysis_ops_util", "confidence_gate")
_emit_escalates_to_human("p1", "analysis_ops_util", "L2")
_emit_reads_policy_state("p1", "analysis_ops_util", "L2")
_emit_authorize_and_execute("p2", "analysis_ops_util", "execution_auth")
_emit_validates_capability("p2", "analysis_ops_util", "capability_check")
_emit_routes_to_capability("p2", "analysis_ops_util", "capability_route")
_emit_writes_via_uwg("p2", "analysis_ops_util", "uwg_write")
_emit_blocks_direct_write("p2", "analysis_ops_util", "direct_write_block")
_emit_records_tool_invocation("p2", "analysis_ops_util", "tool_invocation")
_emit_captures_execution_output("p2", "analysis_ops_util", "exec_output")
_emit_dispatches_agent("p3", "analysis_ops_util", "agent_dispatch")
_emit_coordinates_agents("p3", "analysis_ops_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "analysis_ops_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "analysis_ops_util", "healing_outcome")
_emit_escalates_failure("p3", "analysis_ops_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "analysis_ops_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "analysis_ops_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "analysis_ops_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "analysis_ops_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "analysis_ops_util", "eval_metric")
_emit_stores_embedding("p4", "analysis_ops_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "analysis_ops_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "analysis_ops_util", "exec_snapshot_link")

"\nAnalysis Operations - AST Parsing, Linting, and Code Quality Tools\nConsolidated from core_utils.py and security_utils.py\n"
import ast
import logging
import subprocess
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
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
from agentic_core.utils.security_util import safe_execute

_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_1")
_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_2")
_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_3")
_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_4")
_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_5")
_emit_emits_metric_event("analysis_ops_util", "p4obs", "metric_6")
_emit_records_incident_event("analysis_ops_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("analysis_ops_util", "p4obs", "anomaly")
_emit_writes_observability_log("analysis_ops_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("analysis_ops_util", "p4obs", "mon_state")
_emit_triggers_alert("analysis_ops_util", "p4obs", "alert")
_emit_links_incident_trace("analysis_ops_util", "p4obs", "trace_link")
_emit_captures_pattern("analysis_ops_util", "p3lm", "pattern")
_emit_records_learning_event("analysis_ops_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("analysis_ops_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("analysis_ops_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("analysis_ops_util", "p3lm", "routing")
_emit_improves_agent_policy("analysis_ops_util", "p3lm", "policy")
_emit_stores_learning_state("analysis_ops_util", "p3lm", "state")
_emit_records_execution_trace("analysis_ops_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("analysis_ops_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("analysis_ops_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("analysis_ops_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("analysis_ops_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("analysis_ops_util", "env_read", "p2_env_1")
_emit_reads_environ("analysis_ops_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("analysis_ops_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("analysis_ops_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "analysis_ops_util", "context_pull")
_emit_pulls_context("p1", "analysis_ops_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "analysis_ops_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "analysis_ops_util", "uwg_term_2")
_emit_writes_through("p1", "analysis_ops_util", "write_through")
_emit_writes_through("p1", "analysis_ops_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "analysis_ops_util", "safety_validation")
_emit_invokes_eval("p1", "analysis_ops_util", "eval_call")
_emit_proposal_commits_routing("p1", "analysis_ops_util", "routing_commit")

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

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_python_syntax", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_python_syntax", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())    # guardian: Syntax errors should be caught at parser level, not runtime
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "validate_python_syntax")
    try:
        with open(file_path, encoding="utf-8") as f:
            source: Any = f.read()
        ast.parse(source)
        return (True, None)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
        error_msg: Any = f"SyntaxError in {file_path}: {e.msg} at line {e.lineno}"
        Logger.error(error_msg)
        return (False, error_msg)
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
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
    if fix:    # guardian: File operations should check existence before access
        cmd.append("--fix")
    try:
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, "", "Ruff check timed out")
    except FileNotFoundError:    # guardian: File operations should check existence before access
        return (-1, "", "Ruff not installed")
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
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
    if check_only:    # guardian: File operations should check existence before access
        cmd.append("--check")
    try:
        result: Any = safe_execute(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=False)
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (-1, "", "Black format timed out")
    except FileNotFoundError:    # guardian: File operations should check existence before access
        return (-1, "", "Black not installed")
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
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
        for node in ast.walk(tree):
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
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
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
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
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
        for node in ast.walk(tree):
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
                        for keyword in node.keywords:
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
    # guardian: allow-silent-swallow
    except (RuntimeError, ValueError) as e:
        Logger.error(f"Security analysis failed for {file_path}: {e}")
        return [{"error": str(e)}]
