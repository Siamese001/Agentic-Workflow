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


def python_eval_handler(args: dict[str, Any]) -> str:
    """Evaluate Python expression safely.

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

        # Evaluate in restricted namespace
        safe_globals = {
            "__builtins__": {
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
        }

        # Use ast.literal_eval for simple expressions, eval for complex ones
        try:
            import ast

            # Try literal_eval first (safer)
            result = ast.literal_eval(expr)
        except (ValueError, SyntaxError):
            # Fall back to restricted eval for expressions like ranges, comprehensions
            # ruff: noqa: S307 - Using restricted eval with safe globals
            result = eval(expr, safe_globals, {})
        return str(result)

    except SyntaxError as e:
        return f"Error: Invalid syntax: {e}"
    except Exception as e:  # guardian: allow-silent-swallower
        return "Error: " + str(e)


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

    # python_eval tool
    python_eval_spec = ToolSpec(
        tool_id="python_eval",
        description="Evaluate safe Python expression",
        side_effect_class="PURE",
        args=(ToolArg("expr", "str", True),),
        output_kind="TEXT",
        version=1,
    )
    register_tool(python_eval_spec, python_eval_handler)


# Auto-register when module is imported
register_builtin_tools()
