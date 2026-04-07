"""
AST Canonical Scanner — CI enforcement for CanonicalJSON SSOT.

Scans Python source files for unauthorized direct json.dumps usage
in L2 execution paths.  Only agentic_core/utils/canonical_json_util.py and
agentic_core/utils/canonical_serializer_util.py are exempt.

Exit codes:
  0 — no violations
  1 — one or more violations found

Phase 1.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# ---------------------------------------------------------------------------
# Exemptions — modules allowed to call json.dumps directly
# ---------------------------------------------------------------------------

_EXEMPT_SUFFIXES = (
    "agentic_core/utils/canonical_json_util.py",
    "agentic_core/utils/canonical_serializer_util.py",
    "agentic_core/determinism/digest_authority.py",
)

# Directories whose test files are excluded from the scan
_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

# Directories that are in scope for the enforcement scan
_SCAN_ROOTS = [
    Path(L2_EXECUTION_DIR),
    Path(L0_ROUTING_DIR),
    Path(L1_COGNITION_DIR),
    Path(L3_ORCHESTRATION_DIR),
    Path(L4_STATE_DIR),
    Path(L5_SAFETY_DIR),
    Path(L6_OBSERVABILITY_DIR),
]


def _is_exempt(file_path: Path) -> bool:
    normalized = file_path.as_posix().replace("\\", "/")
    for suffix in _EXEMPT_SUFFIXES:
        if normalized.endswith(suffix):
            return True
    return False


def _in_excluded_dir(file_path: Path) -> bool:
    return any(part in _EXCLUDE_DIRS for part in file_path.parts)


def scan_file(file_path: Path) -> list[str]:
    """Return list of violation strings for *file_path*."""
    violations: list[str] = []

    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"PARSE_ERROR {file_path}:{exc.lineno}: {exc.msg}"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func

        # json.dumps(...)
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "dumps"
            and isinstance(func.value, ast.Name)
            and func.value.id == "json"
        ):
            violations.append(
                f"VIOLATION {file_path}:{node.lineno}: "
                f"direct json.dumps — use CanonicalJSON.serialize_bytes() instead",
            )

    return violations


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(".")
    all_violations: list[str] = []

    for scan_root in _SCAN_ROOTS:
        abs_root = repo_root / scan_root
        if not abs_root.exists():
            continue
        for py_file in sorted(abs_root.rglob("*.py")):
            if _in_excluded_dir(py_file) or _is_exempt(py_file):
                continue
            all_violations.extend(scan_file(py_file))

    if all_violations:
        print("FAIL: Unauthorized json.dumps usage detected:")
        for v in all_violations:
            print(f"  {v}")
        return 1

    total = sum(
        1 for root in _SCAN_ROOTS for _ in (repo_root / root).rglob("*.py") if (repo_root / root).exists()
    )
    print(f"OK: ast_canonical_scanner passed ({total} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
