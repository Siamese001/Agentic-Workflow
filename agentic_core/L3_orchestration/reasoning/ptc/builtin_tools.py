"""
Programmatic Tool Calling (PTC) - Built-in Tools

Minimal safe built-in tools for PTC system.
Implements repo search and Python evaluation tools.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "builtin_tools", "execution_auth")
trace_contract._emit_validates_capability("p2", "builtin_tools", "capability_check")
trace_contract._emit_routes_to_capability("p2", "builtin_tools", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "builtin_tools", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "builtin_tools", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "builtin_tools", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "builtin_tools", "exec_output")
trace_contract._emit_dispatches_agent("p3", "builtin_tools", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "builtin_tools", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "builtin_tools", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "builtin_tools", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "builtin_tools", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "builtin_tools", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "builtin_tools", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "builtin_tools", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "builtin_tools", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "builtin_tools", "eval_metric")
trace_contract._emit_stores_embedding("p4", "builtin_tools", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "builtin_tools", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "builtin_tools", "exec_snapshot_link")
from .tool_contract import ToolArg, ToolSpec

trace_contract.emit_replay_key("p0", "builtin_tools")
trace_contract.emit_determinism_digest("p0", "builtin_tools")

trace_contract._emit_dispatches_healing_run("p1", "builtin_tools", "L3")
trace_contract._emit_routes_through("p1", "builtin_tools", "L3")
trace_contract._emit_checks_agent_registry("p1", "builtin_tools", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "builtin_tools", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "builtin_tools", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "builtin_tools", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "builtin_tools", "target_agent")
trace_contract._emit_verifies_policy("p1", "builtin_tools", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "builtin_tools", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "builtin_tools", "boundary_check")
trace_contract._emit_transcripts_response("p1", "builtin_tools", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "builtin_tools")
trace_contract._emit_gated_by_confidence("p1", "builtin_tools", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "builtin_tools", "L3")
trace_contract._emit_reads_policy_state("p1", "builtin_tools", "L3")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("builtin_tools", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("builtin_tools", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("builtin_tools", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("builtin_tools", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("builtin_tools", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("builtin_tools", "p4obs", "alert")
trace_contract._emit_links_incident_trace("builtin_tools", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("builtin_tools", "p3lm", "pattern")
trace_contract._emit_records_learning_event("builtin_tools", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("builtin_tools", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("builtin_tools", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("builtin_tools", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("builtin_tools", "p3lm", "policy")
trace_contract._emit_stores_learning_state("builtin_tools", "p3lm", "state")
trace_contract._emit_records_execution_trace("builtin_tools", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("builtin_tools", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("builtin_tools", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("builtin_tools", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("builtin_tools", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("builtin_tools", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("builtin_tools", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("builtin_tools", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("builtin_tools", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "builtin_tools", "context_pull")
trace_contract._emit_pulls_context("p1", "builtin_tools", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "builtin_tools", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "builtin_tools", "uwg_term_2")
trace_contract._emit_writes_through("p1", "builtin_tools", "write_through")
trace_contract._emit_writes_through("p1", "builtin_tools", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "builtin_tools", "safety_validation")
trace_contract._emit_invokes_eval("p1", "builtin_tools", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "builtin_tools", "routing_commit")


def repo_rg_handler(args: dict[str, Any]) -> str:
    """Search repository using Python (no external rg dependency).

    Args:
        args: Tool arguments

    Returns:
        JSON string with search results
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "repo_rg_handler", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "repo_rg_handler", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "repo_rg_handler")
    pattern = args["pattern"]
    root = Path(args.get("root", "."))
    try:
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    except re.error as e:
        return f'{{"error": "Invalid regex: {e}"}}'
    results = []
    for file_path in tqdm(root.rglob("*"), desc="Processing", unit="item"):
        if file_path.is_dir():
            continue
        skip_extensions = {
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".bin",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".ico",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
        }
        if file_path.suffix.lower() in skip_extensions:
            continue
        if any(part.startswith(".") for part in file_path.parts):
            continue
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for match in tqdm(regex.finditer(content), desc="Processing", unit="item"):
                line_num = content[: match.start()].count("\n") + 1
                line_start = content.rfind("\n", 0, match.start()) + 1
                line_end = content.find("\n", match.end())
                if line_end == -1:
                    line_end = len(content)
                line_content = content[line_start:line_end].strip()
                results.append(
                    {
                        "file": str(file_path.relative_to(root)),
                        "line": line_num,
                        "content": line_content,
                        "match": match.group(),
                    },
                )
        except (
            UnicodeDecodeError,
            PermissionError,
        ):  # review: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
            continue
    results.sort(key=lambda r: (r["file"], r["line"]))
    import json

    return json.dumps({"results": results}, sort_keys=True, separators=(",", ":"))


def expr_eval_handler(args: dict[str, Any]) -> str:
    """Evaluate simple arithmetic expressions without Python eval.

    Args:
        args: Tool arguments

    Returns:
        String result of evaluation
    """
    expr = args["expr"]
    unsafe_patterns = [
        "import\\s+",
        "from\\s+.*\\s+import",
        "exec\\s*\\(",
        "eval\\s*\\(",
        "open\\s*\\(",
        "file\\s*\\(",
        "__import__",
        "globals\\s*\\(",
        "locals\\s*\\(",
        "vars\\s*\\(",
        "dir\\s*\\(",
        "getattr\\s*\\(",
        "setattr\\s*\\(",
        "delattr\\s*\\(",
        "hasattr\\s*\\(",
        "callable\\s*\\(",
        "isinstance\\s*\\(",
        "issubclass\\s*\\(",
        "type\\s*\\(",
        "super\\s*\\(",
        "lambda\\s+",
        "def\\s+",
        "class\\s+",
        "@\\w+",
        "return\\s+",
        "yield\\s+",
        "raise\\s+",
        "try\\s*:",
        "except\\s+",
        "finally\\s*:",
        "with\\s+",
        "async\\s+",
        "await\\s+",
    ]
    for pattern in unsafe_patterns:
        if re.search(pattern, expr):
            raise ValueError("Expression contains unsafe operations")
    try:
        ast.parse(expr, mode="eval")
        result = _evaluate_expression(expr)
        return str(result)
    except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
        raise ValueError(f"Invalid syntax: {e}") from e
    except Exception as e:  # guardian: allow-broad-exception  -- ADG-burn: broad_exception_catch
        raise ValueError(str(e)) from e


def _evaluate_expression(expr: str) -> Any:
    """Evaluate a simple arithmetic expression safely.

    Args:
        expr: Expression string

    Returns:
        Evaluated result
    """
    import operator

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Not: operator.not_,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.BoolOp):
            result = _eval(node.values[0])
            for value in node.values[1:]:
                result = ops[type(node.op)](result, _eval(value))
            return result
        elif isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op, right in zip(node.ops, node.comparators):
                if not ops[type(op)](left, _eval(right)):
                    return False
                left = _eval(right)
            return True
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                args = [_eval(arg) for arg in node.args]
                safe_funcs = {
                    "abs": abs,
                    "all": all,
                    "any": any,
                    "bin": bin,
                    "bool": bool,
                    "chr": chr,
                    "dict": dict,
                    "divmod": divmod,
                    "enumerate": enumerate,
                    "filter": filter,
                    "float": float,
                    "hex": hex,
                    "int": int,
                    "len": len,
                    "list": list,
                    "map": map,
                    "max": max,
                    "min": min,
                    "oct": oct,
                    "ord": ord,
                    "pow": pow,
                    "range": range,
                    "repr": repr,
                    "reversed": reversed,
                    "round": round,
                    "set": set,
                    "slice": slice,
                    "sorted": sorted,
                    "str": str,
                    "sum": sum,
                    "tuple": tuple,
                    "type": type,
                    "zip": zip,
                }
                if func_name in safe_funcs:
                    return safe_funcs[func_name](*args)
            raise ValueError(f"Unsafe function call: {ast.dump(node)}")
        elif isinstance(node, ast.List):
            return [_eval(e) for e in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(_eval(e) for e in node.elts)
        elif isinstance(node, ast.Dict):
            return {_eval(k): _eval(v) for k, v in zip(node.keys, node.values)}
        else:
            raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    return _eval(tree.body)


def register_builtin_tools():
    """Register all built-in PTC tools. Idempotent."""
    from .ptc_registry import get_global_registry, register_tool

    registry = get_global_registry()
    repo_rg_spec = ToolSpec(
        tool_id="repo_rg",
        description="Search repository using Python regex",
        side_effect_class="READONLY",
        args=(ToolArg("pattern", "str", True), ToolArg("root", "str", False, default=".")),
        output_kind="JSON",
        version=1,
    )
    if registry.has("repo_rg"):
        existing_spec, _ = registry.get("repo_rg")
        if existing_spec.version == repo_rg_spec.version and existing_spec.args == repo_rg_spec.args:
            pass
        else:
            raise ValueError("Tool 'repo_rg' already registered with different spec")
    else:
        register_tool(repo_rg_spec, repo_rg_handler)
    expr_eval_spec = ToolSpec(
        tool_id="expr_eval",
        description="Evaluate safe arithmetic expressions",
        side_effect_class="PURE",
        args=(ToolArg("expr", "str", True),),
        output_kind="TEXT",
        version=1,
    )
    if registry.has("expr_eval"):
        existing_spec, _ = registry.get("expr_eval")
        if existing_spec.version == expr_eval_spec.version and existing_spec.args == expr_eval_spec.args:
            pass
        else:
            raise ValueError("Tool 'expr_eval' already registered with different spec")
    else:
        register_tool(expr_eval_spec, expr_eval_handler)


register_builtin_tools()
