"""
file: agentic_core/L0_routing/scripts/architectural_audit.py
description: AST-based static analysis tool to detect inheritance drift.
directory: agentic_core/L0_routing/scripts
"""

import ast
import os
import sys

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "drift", "p0_governance")
_emit_snapshots_state("p0", "drift", "state_snapshot")

# Configuration: strict definition of the drift
TARGET_VIOLATION = "L2Agent"
REQUIRED_BASE = "SovereignBaseAgent"

# Exclusions based on SSOT knowledge of valid base classes
EXCLUSIONS: set[str] = {
    "L2Agent",  # The class itself cannot violate
    "SovereignBaseAgent",  # The target base
    "MockL2Agent",  # Test mocks
    "ExecutionCanonBaseAgent",  # Likely a valid L2 base
}


class DriftDetector(ast.NodeVisitor):
    """
    Parses python source to find classes inheriting from TARGET_VIOLATION.
    Uses AST to bypass regex limitations (aliasing, formatting).
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.violations: list[dict] = []
        self.imports: dict[str, str] = {}  # alias -> original_name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports to detect aliasing e.g. 'from x import L2Agent as Base'"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "DriftDetector.visit_ImportFrom")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not node.module:
            return
        for alias in node.names:
            if alias.name == TARGET_VIOLATION:
                # Store the local name used in this file
                local_name = alias.asname if alias.asname else alias.name
                self.imports[local_name] = TARGET_VIOLATION

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Inspect class inheritance signatures."""
        if node.name in EXCLUSIONS:
            return

        for base in node.bases:
            detected_name = None

            # Case 1: Direct Name (class X(L2Agent))
            if isinstance(base, ast.Name):
                if base.id == TARGET_VIOLATION:
                    detected_name = base.id
                elif base.id in self.imports and self.imports[base.id] == TARGET_VIOLATION:
                    detected_name = f"{base.id} (alias of {TARGET_VIOLATION})"

            # Case 2: Attribute (class X(module.L2Agent))
            elif isinstance(base, ast.Attribute):
                if base.attr == TARGET_VIOLATION:
                    # Handle nested attributes like a.b.c.L2Agent
                    parts = []
                    current = base
                    while isinstance(current, ast.Attribute):
                        parts.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        parts.append(current.id)
                        parts.reverse()
                        detected_name = ".".join(parts)

            if detected_name:
                self.violations.append(
                    {
                        "file": self.filename,
                        "class": node.name,
                        "line": node.lineno,
                        "detected": detected_name,
                    },
                )


def scan_repository(root_path: str = ".") -> int:
    """
    Recursively scans the repo for violations.
    Returns exit code: 0 if success, 1 if violations OR parse errors found.
    """
    all_violations = []
    parse_errors = []

    # SSOT: Respect the ignore_dirs from blueprint if possible, but hardcode for standalone safety
    ignored_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    # guardian: allow-path-string
    print(f"Scanning root: {os.path.abspath(root_path)}")

    for root, dirs, files in os.walk(root_path):
        # In-place filtering of directories to skip
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        for f in files:
            if not f.endswith(".py"):
                continue

            # guardian: allow-path-string
            full_path = os.path.join(root, f)
            try:
                # Force UTF-8 to avoid CP1252 errors on Windows
                with open(full_path, encoding="utf-8") as source:
                    content = source.read()

                tree = ast.parse(content, filename=full_path)
                checker = DriftDetector(full_path)
                checker.visit(tree)
                all_violations.extend(checker.violations)
            except UnicodeDecodeError:
                parse_errors.append(f"{full_path} [ENCODING ERROR]")
            except SyntaxError as e:
                parse_errors.append(f"{full_path} [SYNTAX ERROR: line {e.lineno}]")
            # guardian: allow-silent-swallow
            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                parse_errors.append(f"{full_path} [UNKNOWN ERROR: {str(e)}]")

    # REPORTING
    exit_code = 0

    if parse_errors:
        print(f"\n[CRITICAL] FAILED TO PARSE {len(parse_errors)} FILES:")
        print("-" * 100)
        for err in parse_errors:
            print(f"[SKIP] {err}")
        print("-" * 100)

        # Immediate Fail if critical agents are skipped
        if any("ToolsmithAgent" in e for e in parse_errors):
            print("\n!!! ALARM: ToolsmithAgent was skipped! Audit is INVALID. !!!")

        exit_code = 1

    if all_violations:
        print(f"\n[FAIL] Found {len(all_violations)} Architectural Violations:")
        print(f"{'File':<60} | {'Class':<30} | {'Line':<5}")
        print("-" * 100)
        for v in all_violations:
            print(f"{v['file']:<60} | {v['class']:<30} | {v['line']:<5}")
        exit_code = 1
    elif not parse_errors:
        print("\n[SUCCESS] Architecture is compliant. No orphaned L2Agents found and 0 parse errors.")

    return exit_code


if __name__ == "__main__":
    # Determine project root based on SSOT markers if running from subdir
    # guardian: allow-path-string
    current_dir = os.getcwd()
    print(f"Starting AST Audit for {TARGET_VIOLATION}...")

    sys.exit(scan_repository(current_dir))
