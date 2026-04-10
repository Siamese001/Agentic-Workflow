"""CI guard for REQ-111 and REQ-114: Check for uuid4 and wall-clock usage.

Scans L0-L5 non-mixin files for:
- uuid.uuid4() usage (REQ-111)
- datetime.now(), time.time(), time.sleep() usage (REQ-114)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("check_determinism_violations", "check_determinism_violations_digest")
record_execution_trace("check_determinism_violations", "check_determinism_violations_trace")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
]
EXCLUDE_PATTERNS = ["mixin.py", "test_", "_test.py", "tests/"]
UUID4_PATTERNS = {"uuid.uuid4", "uuid4()"}
WALLCLOCK_PATTERNS = {"time.time", "time.sleep", "datetime.now", "datetime.utcnow", "time.monotonic"}


def should_exclude_file(path: Path) -> bool:
    """Check if file should be excluded from scanning."""
    rel_path = path.relative_to(REPO_ROOT).as_posix()
    for pattern in EXCLUDE_PATTERNS:
        if pattern in rel_path:
            return True
    return False


def check_uuid4_usage(tree: ast.AST, file_path: str) -> list[str]:
    """Check for uuid4 usage in AST."""
    violations = []

    class Uuid4Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "uuid"
                    and (node.func.attr == "uuid4")
                ):
                    violations.append(f"{file_path}:{node.lineno}: uuid.uuid4() call")
            elif isinstance(node.func, ast.Name) and node.func.id == "uuid4":
                violations.append(f"{file_path}:{node.lineno}: uuid4() call")
            self.generic_visit(node)

    Uuid4Visitor().visit(tree)
    return violations


def check_wallclock_usage(tree: ast.AST, file_path: str) -> list[str]:
    """Check for wall-clock usage in AST."""
    violations = []

    class WallclockVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    obj_name = node.func.value.id
                    func_name = node.func.attr
                    if obj_name == "time" and func_name in {"time", "sleep", "monotonic"}:
                        violations.append(f"{file_path}:{node.lineno}: time.{func_name}() call")
                    elif obj_name == "datetime" and func_name in {"now", "utcnow"}:
                        violations.append(f"{file_path}:{node.lineno}: datetime.{func_name}() call")
            self.generic_visit(node)

    WallclockVisitor().visit(tree)
    return violations


def main() -> int:
    """Main entry point."""
    violations: list[str] = []
    for root in SCAN_ROOTS:
        root_path = REPO_ROOT / root
        if not root_path.exists():
            continue
        for py_file in root_path.rglob("*.py"):
            if should_exclude_file(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
            except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
                continue
            rel_path = py_file.relative_to(REPO_ROOT).as_posix()
            violations.extend(check_uuid4_usage(tree, rel_path))
            violations.extend(check_wallclock_usage(tree, rel_path))
    if violations:
        print(f"FAIL: {len(violations)} determinism violation(s) found:")
        for violation in violations:
            print(f"  {violation}")
        return 1
    print("OK: no determinism violations found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
