"""GAP-001 P0 CI Gate: Exit L4 Boundary Hardening Enforcement.

Blocks direct filesystem durable writes in apps_rg/runtime/bindings/exit_binding.py.
Verifies that Exit only produces inert CommitRequest candidates.

Gap: GAP-001 (Exit direct filesystem writes)
Classification: MISSION_CRITICAL_RUNTIME_BLOCKER
Status after fix: CLOSED

Enforcement: Fail-closed when APPS_RG_EXIT_NO_DIRECT_WRITES_FAIL_CLOSED=1
Bypass: APPS_RG_EXIT_NO_DIRECT_WRITES_BYPASS=1 (logged)
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any

# Gate metadata
GATE_ID = "GAP001-EXIT-NO-DIRECT-WRITES"
GATE_NAME = "GAP-001 apps_rg Exit L4 Boundary Hardening"
VIOLATION_FILE = Path("artifacts/ci/gap001_exit_direct_writes.json")


class ExitBindingASTScanner(ast.NodeVisitor):
    """AST scanner to detect forbidden filesystem write operations."""

    FORBIDDEN_PATTERNS = {
        "write_text",
        "write_bytes",
        "mkdir",
        "makedirs",
        "shutil.copy",
        "shutil.copy2",
        "shutil.move",
    }

    ALLOWED_CONTEXTS = {
        # _build_docx_commit_candidate is allowed to use doc.save() to BytesIO
        "_build_docx_commit_candidate": {"save"},
    }

    def __init__(self) -> None:
        self.violations: list[dict[str, Any]] = []
        self.current_function: str | None = None
        self.function_violations: dict[str, list[str]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context."""
        prev_function = self.current_function
        self.current_function = node.name
        self.function_violations[node.name] = []

        # Visit function body
        self.generic_visit(node)

        # Report violations for this function
        if self.function_violations[node.name]:
            for pattern in self.function_violations[node.name]:
                self.violations.append({
                    "function": node.name,
                    "line": node.lineno,
                    "pattern": pattern,
                    "severity": "ERROR",
                })

        self.current_function = prev_function

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        """Detect forbidden function calls."""
        # Get the function name being called
        func_name = self._get_func_name(node.func)

        if func_name:
            # Check for forbidden patterns
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in func_name:
                    # Check if this is in an allowed context
                    if not self._is_allowed_pattern(func_name):
                        if self.current_function:
                            self.function_violations[self.current_function].append(func_name)
                        else:
                            self.violations.append({
                                "function": "<module>",
                                "line": node.lineno,
                                "pattern": func_name,
                                "severity": "ERROR",
                            })

        self.generic_visit(node)

    def _get_func_name(self, node: ast.expr) -> str | None:
        """Extract function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return None

    def _is_allowed_pattern(self, func_name: str) -> bool:
        """Check if pattern is allowed in current context."""
        if not self.current_function:
            return False

        # Check allowed contexts
        if self.current_function in self.ALLOWED_CONTEXTS:
            allowed_patterns = self.ALLOWED_CONTEXTS[self.current_function]
            for pattern in allowed_patterns:
                if pattern in func_name:
                    return True

        return False


def scan_exit_binding_for_writes(exit_binding_path: Path) -> dict[str, Any]:
    """Scan exit_binding.py for forbidden write operations."""
    if not exit_binding_path.exists():
        return {
            "gate_id": GATE_ID,
            "status": "ERROR",
            "message": f"exit_binding.py not found at {exit_binding_path}",
            "violations": [],
        }

    source = exit_binding_path.read_text(encoding="utf-8")

    # Check for GAP-001 status marker in source
    gap001_closed = "gap_001_status" in source and '"CLOSED"' in source

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "gate_id": GATE_ID,
            "status": "ERROR",
            "message": f"Syntax error in exit_binding.py: {e}",
            "violations": [],
        }

    scanner = ExitBindingASTScanner()
    scanner.visit(tree)

    # Also check for legacy function signatures that indicate writes
    # Note: json.dumps (with 's') is string serialization — OK
    #       json.dump (without 's') is file write — VIOLATION
    legacy_patterns = [
        "def _write_artifact(",
        "output_dir.mkdir",
        "path.write_text",
        "json.dump(",  # Only matches file-write, not json.dumps
    ]

    for pattern in legacy_patterns:
        if pattern in source:
            scanner.violations.append({
                "function": "<source>",
                "line": 0,
                "pattern": pattern,
                "severity": "ERROR",
            })

    status = "PASS" if not scanner.violations else "FAIL"

    return {
        "gate_id": GATE_ID,
        "status": status,
        "gap001_closed_marker": gap001_closed,
        "violations": scanner.violations,
        "violation_count": len(scanner.violations),
        "file_scanned": str(exit_binding_path),
    }


def main() -> int:
    """Run GAP-001 CI gate."""
    # Check bypass
    if os.environ.get("APPS_RG_EXIT_NO_DIRECT_WRITES_BYPASS") == "1":
        print(f"[{GATE_ID}] BYPASS ACTIVE — skipping GAP-001 enforcement")
        return 0

    # Check fail-closed mode
    fail_closed = os.environ.get("APPS_RG_EXIT_NO_DIRECT_WRITES_FAIL_CLOSED") == "1"

    # Find exit_binding.py
    repo_root = Path(__file__).parent.parent.parent
    exit_binding_path = repo_root / "apps_rg" / "runtime" / "bindings" / "exit_binding.py"

    result = scan_exit_binding_for_writes(exit_binding_path)

    # Ensure output directory exists
    VIOLATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write result
    VIOLATION_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Print summary
    print(f"[{GATE_ID}] {GATE_NAME}")
    print(f"  File: {result['file_scanned']}")
    print(f"  Status: {result['status']}")
    print(f"  GAP-001 Closed Marker: {result.get('gap001_closed_marker', False)}")
    print(f"  Violations: {result['violation_count']}")

    for v in result['violations']:
        print(f"    - {v['severity']}: {v['function']} line {v['line']} ({v['pattern']})")

    # Determine exit code
    if result['status'] == "PASS":
        print(f"\n[{GATE_ID}] ✅ GAP-001 ENFORCED — Exit performs no direct filesystem writes")
        return 0
    elif fail_closed:
        print(f"\n[{GATE_ID}] ❌ GAP-001 VIOLATION — Direct writes detected, fail-closed active")
        return 1
    else:
        print(f"\n[{GATE_ID}] ⚠️  GAP-001 ADVISORY — Direct writes detected (advisory mode)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
