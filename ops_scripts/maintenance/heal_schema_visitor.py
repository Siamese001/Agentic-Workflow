"""AST visitor utilities for inspecting heal-method schema conformance."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class HealMethodIssue:
    message: str
    lineno: int


@dataclass(slots=True)
class HealMethodRecord:
    class_name: str
    method_name: str
    lineno: int
    parameters: list[str] = field(default_factory=list)
    issues: list[HealMethodIssue] = field(default_factory=list)


class HealSchemaVisitor(ast.NodeVisitor):
    """Collect class-level heal method definitions and basic signature issues."""

    def __init__(self) -> None:
        self._class_stack: list[str] = []
        self.records: list[HealMethodRecord] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._maybe_record(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._maybe_record(node)

    def _maybe_record(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if not self._class_stack or node.name != "heal":
            self.generic_visit(node)
            return

        params = [arg.arg for arg in node.args.args]
        record = HealMethodRecord(
            class_name=self._class_stack[-1],
            method_name=node.name,
            lineno=node.lineno,
            parameters=params,
        )

        if not params or params[0] != "self":
            record.issues.append(
                HealMethodIssue("heal() should declare self as the first parameter", node.lineno)
            )
        if len(params) < 2:
            record.issues.append(
                HealMethodIssue("heal() should accept at least one payload parameter", node.lineno)
            )
        if not node.returns:
            record.issues.append(
                HealMethodIssue("heal() is missing an explicit return annotation", node.lineno)
            )

        self.records.append(record)
        self.generic_visit(node)


def analyze_source(source: str) -> list[HealMethodRecord]:
    tree = ast.parse(source)
    visitor = HealSchemaVisitor()
    visitor.visit(tree)
    return visitor.records


def analyze_file(path: Path) -> list[HealMethodRecord]:
    source = path.read_text(encoding="utf-8", errors="replace")
    return analyze_source(source)
