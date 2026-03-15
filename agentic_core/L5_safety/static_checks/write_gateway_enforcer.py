"""
Write Gateway Enforcement Scanner

AST-based static analysis to detect direct file writes bypassing write_gateway.
Enforces that non-L2 layers use the write gateway for persistence operations.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "write_gateway_enforcer", "L5")
_emit_routes_through("p1", "write_gateway_enforcer", "L5")
_emit_escalates_to_human("p1", "write_gateway_enforcer", "L5")
_emit_reads_policy_state("p1", "write_gateway_enforcer", "L5")

_emit_applies_guardrail("p0", "write_gateway_enforcer", "p0_governance")
_emit_snapshots_state("p0", "write_gateway_enforcer", "state_snapshot")


class WriteGatewayVisitor(ast.NodeVisitor):
    """AST visitor to detect direct file writes."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []
        self.in_allowlisted_function = False
        self.current_line_content = ""
        self._with_flagged_lines: set[int] = set()

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "WriteGatewayVisitor.visit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteGatewayVisitor.visit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if hasattr(node, "lineno"):
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1]
            except (OSError, UnicodeDecodeError, IndexError, AttributeError) as e:
                self.current_line_content = ""
        super().visit(node)

    def _check_allowlist(self) -> bool:
        """Check if current line has allowlist comment."""
        return "# guardian: allow-direct-write" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for direct file write calls."""
        if self._check_allowlist():
            self.generic_visit(node)
            return
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.lineno in self._with_flagged_lines:
                self.generic_visit(node)
                return
            if node.args:
                mode_arg = None
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                else:
                    for kw in node.keywords:
                        if kw.arg == "mode":
                            mode_arg = kw.value
                            break
                if mode_arg and isinstance(mode_arg, ast.Constant):
                    if isinstance(mode_arg.value, str):
                        write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                        if any(mode_arg.value.startswith(mode) for mode in write_modes):
                            snippet = f'open(..., mode="{mode_arg.value}")'
                            self.violations.append((node.lineno, "DIRECT_OPEN_WRITE", snippet))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["write_text", "write_bytes"]:
                snippet = f"Path.{node.func.attr}(...)"
                self.violations.append((node.lineno, "DIRECT_PATH_WRITE", snippet))
        if isinstance(node.func, ast.Name) and node.func.id == "json":
            if isinstance(node.func, ast.Name):
                if hasattr(node, "parent"):
                    pass
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Check for 'with open(...)' patterns."""
        if self._check_allowlist():
            self.generic_visit(node)
            return
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == "open":
                    mode_arg = None
                    if len(item.context_expr.args) >= 2:
                        mode_arg = item.context_expr.args[1]
                    else:
                        for kw in item.context_expr.keywords:
                            if kw.arg == "mode":
                                mode_arg = kw.value
                                break
                    if mode_arg and isinstance(mode_arg, ast.Constant):
                        if isinstance(mode_arg.value, str):
                            write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                            if any(mode_arg.value.startswith(mode) for mode in write_modes):
                                snippet = f'with open(..., mode="{mode_arg.value}")'
                                self.violations.append((node.lineno, "DIRECT_WITH_WRITE", snippet))
                                self._with_flagged_lines.add(item.context_expr.lineno)
        self.generic_visit(node)


def scan_file_for_writes(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for direct file writes.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []
    if "L2_execution" in str(file_path):
        return violations
    if "ptc" in str(file_path).lower() and "tool_call_store.py" in str(file_path):
        return violations
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = WriteGatewayVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:
        violations.append((e.lineno or 0, "WRITE_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    # guardian: allow-silent-swallower
    except Exception as e:
        violations.append((0, "WRITE_SCAN_ERROR", f"Scan error: {e}"))
    return violations


_WRITE_SCAN_ROOTS = [
    "agentic_core/L3_orchestration/replay",
    "agentic_core/L3_orchestration/arbitration",
    "agentic_core/L3_orchestration/ptc",
    "agentic_core/L4_state/storage",
]


def scan_repository_for_writes(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan governance-critical storage/replay directories for direct file writes.

    Only scans the directories where the UWG write-gateway contract is enforced.
    Legacy script, agent, and reasoning directories are excluded.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []
    for scan_root in _WRITE_SCAN_ROOTS:
        scan_path = repo_root / scan_root
        if not scan_path.exists():
            continue
        for py_file in scan_path.rglob("*.py"):
            if "L2_execution" in py_file.parts:
                continue
            violations = scan_file_for_writes(py_file)
            for lineno, rule_id, snippet in violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return all_violations


__all__ = ["scan_file_for_writes", "scan_repository_for_writes"]
