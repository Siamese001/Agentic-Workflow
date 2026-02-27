"""CI guard: no wall-clock usage in determinism-critical paths.

REQ-111/REQ-114: Determinism requires all IDs and timings to derive from
semantic clocks, not OS wall-clock (datetime.now, time.time, etc.).

Scans DETERMINISM_ROOTS for wall-clock API calls; exits non-zero on violation.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DETERMINISM_ROOTS = [
    "agentic_core/L0_routing",
    "agentic_core/L2_execution/determinism",
    "agentic_core/mixins",
    "system_learning/engines",
]

ALLOWED_PATHS = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "agentic_core/L2_execution/audit/hash_chain_audit_log.py",
    "agentic_core/L0_routing/enforcement/governance_contracts.py",
    "agentic_core/mixins/tracing_mixin.py",
}

WALL_CLOCK_CALLS = {
    ("time", "time"),
    ("time", "perf_counter"),
    ("time", "monotonic"),
    ("datetime", "now"),
    ("datetime", "utcnow"),
}


def _is_wall_clock(node: ast.Call) -> bool:
    """Return True if node is a known wall-clock API call."""
    func = node.func
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            pair = (func.value.id, func.attr)
            return pair in WALL_CLOCK_CALLS
    return False


def main() -> int:
    violations: list[str] = []
    for root in DETERMINISM_ROOTS:
        root_path = REPO_ROOT / root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in ALLOWED_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and _is_wall_clock(node):
                    violations.append(f"{rel}:{node.lineno}: wall-clock call '{ast.unparse(node.func)}'")
    if violations:
        print(f"FAIL: {len(violations)} wall-clock usage(s) in determinism paths:")
        for v in violations:
            print(f"  {v}")
        return 1
    print("OK: no wall-clock usage in determinism paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
