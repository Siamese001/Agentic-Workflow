"""
AST Canonical Scanner — CI enforcement for CanonicalJSON SSOT.

Scans Python source files for unauthorized direct json.dumps usage
in L2 execution paths.  Only agentic_core/utils/canonical_json.py and
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

# ---------------------------------------------------------------------------
# Exemptions — modules allowed to call json.dumps directly
# ---------------------------------------------------------------------------

_EXEMPT_SUFFIXES = (
    "agentic_core/utils/canonical_json.py",
    "agentic_core/utils/canonical_serializer_util.py",
    "agentic_core/determinism/digest_authority.py",
)

# Directories whose test files are excluded from the scan
_EXCLUDE_DIRS = {"tests", ".backup", "__pycache__", ".git"}

# Directories that are in scope for the enforcement scan
_SCAN_ROOTS = [
    Path("agentic_core/L2_execution"),
    Path("agentic_core/L0_routing"),
    Path("agentic_core/L1_cognition"),
    Path("agentic_core/L3_orchestration"),
    Path("agentic_core/L4_state"),
    Path("agentic_core/L5_safety"),
    Path("agentic_core/L6_observability"),
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
    except SyntaxError as exc:
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
                f"direct json.dumps — use CanonicalJSON.serialize_bytes() instead"
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
