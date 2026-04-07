"""
Manual execution trace instrumentation tool.
Adds ExecutionTrace context managers to agent classes.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("add_execution_trace", "add_execution_trace_digest")
record_execution_trace("add_execution_trace", "add_execution_trace_trace")


ROOT = Path(__file__).resolve().parents[2]


class ExecutionTraceInstrumenter(ast.NodeTransformer):
    """Adds ExecutionTrace instrumentation to agent classes."""

    def __init__(self) -> None:
        self.mutations: list[dict[str, Any]] = []
        self.trace_imported = False

    def _is_agent_class(self, node: ast.ClassDef) -> bool:
        """Check if this is an agent class."""
        return "Agent" in node.name

    def _find_execute_method(self, node: ast.ClassDef) -> ast.FunctionDef | None:
        """Find the main execution method in an agent class."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Common method names for agent execution
                if item.name in ("execute", "run", "process", "handle", "call", "__call__"):
                    return item
        return None

    def _wrap_method_with_trace(self, method: ast.FunctionDef) -> ast.FunctionDef:
        """Wrap a method with ExecutionTrace context manager."""
        # Create the trace context manager
        with_stmt = ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="ExecutionTrace", ctx=ast.Load()),
                            attr="__call__",
                            ctx=ast.Load(),
                        ),
                        args=[
                            ast.Call(
                                func=ast.Name(id="uuid4", ctx=ast.Load()),
                                args=[],
                                keywords=[],
                            ),
                            ast.Constant(value=f"agent_{method.name}"),
                        ],
                        keywords=[],
                    ),
                    optional_vars=ast.Name(id="trace", ctx=ast.Store()),
                ),
            ],
            body=method.body,
        )

        # Add trace.record calls at start and end
        start_record = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="trace", ctx=ast.Load()),
                    attr="record",
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Constant(value="start"),
                    ast.Dict(
                        keys=[ast.Constant(value="method"), ast.Constant(value="class")],
                        values=[
                            ast.Constant(value=method.name),
                            ast.Name(id="self.__class__.__name__", ctx=ast.Load()),
                        ],
                    ),
                ],
                keywords=[],
            ),
        )

        # Wrap existing method body in try/finally for completion record
        try_body = method.body
        finally_body = [
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="trace", ctx=ast.Load()),
                        attr="record",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Constant(value="complete"),
                        ast.Dict(
                            keys=[ast.Constant(value="method"), ast.Constant(value="class")],
                            values=[
                                ast.Constant(value=method.name),
                                ast.Name(id="self.__class__.__name__", ctx=ast.Load()),
                            ],
                        ),
                    ],
                    keywords=[],
                ),
            ),
        ]

        wrapped_body = [
            start_record,
            ast.Try(
                body=try_body,
                handlers=[],
                orelse=[],
                finalbody=finally_body,
            ),
        ]

        with_stmt.body = wrapped_body
        method.body = [with_stmt]

        return method

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        if self._is_agent_class(node):
            execute_method = self._find_execute_method(node)
            if execute_method:
                # Wrap the execution method with trace
                original_method = ast.unparse(execute_method)
                self._wrap_method_with_trace(execute_method)
                self.mutations.append(
                    {
                        "type": "method_wrapped",
                        "class": node.name,
                        "method": execute_method.name,
                        "line": execute_method.lineno,
                    },
                )
                self.trace_imported = True

        self.generic_visit(node)
        return node

    def add_trace_imports(self, tree: ast.Module) -> ast.Module:
        """Add necessary imports for ExecutionTrace."""
        if not self.trace_imported:
            return tree

        # Add imports at the top
        imports = [
            ast.ImportFrom(
                module="agentic_core.runtime.execution_trace",
                names=[ast.alias(name="ExecutionTrace", asname=None)],
                level=0,
            ),
            ast.ImportFrom(
                module="uuid",
                names=[ast.alias(name="uuid4", asname=None)],
                level=0,
            ),
        ]

        # Insert after existing imports and docstrings
        insert_idx = 0
        for i, node in enumerate(tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_idx = i + 1
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                # Docstring
                insert_idx = i + 1
            else:
                break

        for import_node in reversed(imports):
            tree.body.insert(insert_idx, import_node)

        return tree


def instrument_file(filepath: Path, dry_run: bool = True) -> dict[str, Any]:
    """Instrument a single Python file with execution trace."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except Exception as e:
        return {"status": "parse_error", "error": str(e), "mutations": 0}

    instrumenter = ExecutionTraceInstrumenter()
    new_tree = instrumenter.visit(tree)

    if not instrumenter.mutations:
        return {"status": "no_mutations", "mutations": 0}

    if instrumenter.trace_imported:
        new_tree = instrumenter.add_trace_imports(new_tree)

    ast.fix_missing_locations(new_tree)
    new_source = ast.unparse(new_tree)

    if not dry_run:
        filepath.write_text(new_source, encoding="utf-8")

    return {
        "status": "dry_run" if dry_run else "instrumented",
        "mutations": len(instrumenter.mutations),
        "details": instrumenter.mutations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Add execution trace to agent files")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("files", nargs="*", help="Specific files to instrument")
    args = parser.parse_args()

    if args.execute and args.dry_run:
        parser.error("Cannot specify both --execute and --dry-run")

    dry_run = not args.execute

    if args.files:
        # Instrument specific files
        file_paths = [Path(f) for f in args.files]
    else:
        # Auto-detect agent files
        print("Auto-detecting agent files...")
        # This would need to be implemented based on the query results
        print("Please specify files to instrument.")
        return

    print(f"\nFound {len(file_paths)} files to instrument\n{'=' * 60}")

    total_files = instrumented_files = total_mutations = 0

    for filepath in file_paths:
        if not filepath.exists():
            print(f"  SKIP (not found): {filepath}")
            continue

        total_files += 1
        result = instrument_file(filepath, dry_run)

        if result["status"] in ("instrumented", "dry_run") and result["mutations"] > 0:
            instrumented_files += 1
            total_mutations += result["mutations"]
            print(f"  {result['status']:12} {filepath} ({result['mutations']} mutations)")
            for detail in result["details"]:
                print(f"    L{detail['line']}: {detail['type']} - {detail['class']}.{detail['method']}")
        elif result["status"] == "parse_error":
            print(f"  ERROR: {filepath} - {result['error']}")

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Total files scanned:   {total_files}")
    print(f"  Files instrumented:    {instrumented_files}")
    print(f"  Total mutations:       {total_mutations}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'EXECUTED'}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\nRe-run with --execute to apply changes")


if __name__ == "__main__":
    main()
