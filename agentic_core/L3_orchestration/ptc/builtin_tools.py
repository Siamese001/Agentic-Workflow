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

from .ptc_registry import register_tool
from .tool_contract import ToolArg, ToolSpec


def repo_rg_handler(args: dict[str, Any]) -> str:
    """Search repository using Python (no external rg dependency).

    Args:
        args: Tool arguments

    Returns:
        JSON string with search results
    """
    pattern = args["pattern"]
    root = Path(args.get("root", "."))

    # Compile regex pattern
    try:
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    except re.error as e:
        return f'{{"error": "Invalid regex: {e}"}}'

    # Search files
    results = []

    # Walk directory
    for file_path in root.rglob("*"):
        # Skip directories and common non-text files
        if file_path.is_dir():
            continue

        # Skip binary files and common non-text extensions
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

        # Skip hidden files and directories
        if any(part.startswith(".") for part in file_path.parts):
            continue

        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Search for pattern
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
            # Skip files that can't be read
            continue

    # Sort results deterministically
    results.sort(key=lambda r: (r["file"], r["line"]))

    # Return JSON
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

    # Only allow safe expressions
    # Disallow imports, function definitions, etc.
    unsafe_patterns = [
        r"import\s+",
        r"from\s+.*\s+import",
        r"exec\s*\(",
        r"eval\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"__import__",
        r"globals\s*\(",
        r"locals\s*\(",
        r"vars\s*\(",
        r"dir\s*\(",
        r"getattr\s*\(",
        r"setattr\s*\(",
        r"delattr\s*\(",
        r"hasattr\s*\(",
        r"callable\s*\(",
        r"isinstance\s*\(",
        r"issubclass\s*\(",
        r"type\s*\(",
        r"super\s*\(",
        r"lambda\s+",
        r"def\s+",
        r"class\s+",
        r"@\w+",
        r"return\s+",
        r"yield\s+",
        r"raise\s+",
        r"try\s*:",
        r"except\s+",
        r"finally\s*:",
        r"with\s+",
        r"async\s+",
        r"await\s+",
    ]

    for pattern in unsafe_patterns:
        if re.search(pattern, expr):
            return "Error: Expression contains unsafe operations"

    try:
        # Parse to ensure it's a valid expression
        ast.parse(expr, mode="eval")

        # Evaluate using our simple deterministic parser
        result = _evaluate_expression(expr)
        return str(result)

    except SyntaxError as e:
        return f"Error: Invalid syntax: {e}"
    except Exception as e:  # guardian: allow-silent-swallower
        return "Error: " + str(e)


def _evaluate_expression(expr: str) -> Any:
    """Evaluate a simple arithmetic expression safely.

    Args:
        expr: Expression string

    Returns:
        Evaluated result
    """
    import operator

    # Define safe operators
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

    # Parse the expression
    tree = ast.parse(expr, mode="eval")

    # Evaluate recursively
    def _eval(node):
        if isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python >= 3.8
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8
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
            # Allow specific safe built-in functions
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                args = [_eval(arg) for arg in node.args]

                # Safe built-ins
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


# Register built-in tools
def register_builtin_tools() -> None:
    """Register all built-in tools in the global registry."""

    # repo_rg tool
    repo_rg_spec = ToolSpec(
        tool_id="repo_rg",
        description="Search repository using Python regex",
        side_effect_class="READONLY",
        args=(
            ToolArg("pattern", "str", True),
            ToolArg("root", "str", False, default="."),
        ),
        output_kind="JSON",
        version=1,
    )
    register_tool(repo_rg_spec, repo_rg_handler)

    # expr_eval tool
    expr_eval_spec = ToolSpec(
        tool_id="expr_eval",
        description="Evaluate safe arithmetic expressions",
        side_effect_class="PURE",
        args=(ToolArg("expr", "str", True),),
        output_kind="TEXT",
        version=1,
    )
    register_tool(expr_eval_spec, expr_eval_handler)


# Auto-register when module is imported
register_builtin_tools()
