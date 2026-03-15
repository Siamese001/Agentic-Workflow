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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

from .tool_contract import ToolArg, ToolSpec


def repo_rg_handler(args: dict[str, Any]) -> str:
    """Search repository using Python (no external rg dependency).

    Args:
        args: Tool arguments

    Returns:
        JSON string with search results
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "repo_rg_handler", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "repo_rg_handler", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "repo_rg_handler")
    pattern = args["pattern"]
    root = Path(args.get("root", "."))
    try:
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    except re.error as e:
        return f'{{"error": "Invalid regex: {e}"}}'
    results = []
    for file_path in root.rglob("*"):
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
            for match in regex.finditer(content):
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
                    }
                )
        except (UnicodeDecodeError, PermissionError):
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
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e}")
    except Exception as e:
        raise ValueError(str(e))


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
