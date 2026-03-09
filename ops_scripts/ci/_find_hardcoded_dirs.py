"""AST-backed scanner: find all hardcoded directory-exclusion sets.

Looks for assignments where a set/frozenset/list literal contains strings
that overlap with known SSOT exclusion directories (archives, healing_backups,
__pycache__, .git, .venv, etc.) — signalling that the code is duplicating SSOT
instead of importing from it.

Reports every file + line where this pattern exists, along with which SSOT
constant should be used instead.

Usage: python ops_scripts/ci/_find_hardcoded_dirs.py
"""

from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── SSOT: canonical sets that should NOT be re-defined elsewhere ─────────────
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# Union of all directory names that are owned by SSOT
SSOT_DIR_NAMES: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)

# Minimum overlap: a literal set with >= this many SSOT-owned names is a violation
MIN_OVERLAP = 2

# Files / dirs that ARE the SSOT source — skip them
SSOT_PATHS = {
    "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
    "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
    "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
}

# Directories to skip entirely
SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

SCAN_ROOTS = [
    ROOT / "ops_scripts",
    ROOT / "agentic_core",
    ROOT / "tests",
    ROOT / "apps_rg",
    ROOT / "apps_lic",
    ROOT / "apps_shared",
]


def _excluded(path: pathlib.Path) -> bool:
    return bool(set(path.parts) & SKIP_DIRS)


def _string_literals_in_node(node: ast.AST) -> list[str]:
    """Extract all string constants from a Set/List/Tuple/frozenset-call node."""
    strings: list[str] = []
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                strings.append(elt.value)
    elif isinstance(node, ast.Call):
        # frozenset({...}) or set([...])
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("frozenset", "set"):
            for arg in node.args:
                strings.extend(_string_literals_in_node(arg))
    return strings


def scan_file(path: pathlib.Path) -> list[tuple[int, str, list[str], str]]:
    """Return list of (lineno, varname_or_context, overlapping_strings, suggestion)."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []

    findings: list[tuple[int, str, list[str], str]] = []

    for node in ast.walk(tree):
        # Case 1: assignment  X = {..."archives"...}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                name = target.id if isinstance(target, ast.Name) else "<expr>"
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                # Determine which SSOT constant covers the overlap
                suggestion = _suggest_ssot(overlap)
                findings.append((node.lineno, name, overlap, suggestion))

        # Case 2: augmented assign  X |= {...}
        elif isinstance(node, ast.AugAssign):
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                name = node.target.id if isinstance(node.target, ast.Name) else "<expr>"
                suggestion = _suggest_ssot(overlap)
                findings.append((node.lineno, name, overlap, suggestion))

        # Case 3: bare set/frozenset literal passed to a function
        elif isinstance(node, ast.Call):
            for arg in node.args:
                strings = _string_literals_in_node(arg)
                overlap = [s for s in strings if s in SSOT_DIR_NAMES]
                if len(overlap) >= MIN_OVERLAP:
                    fname = ""
                    if isinstance(node.func, ast.Name):
                        fname = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        fname = node.func.attr
                    suggestion = _suggest_ssot(overlap)
                    findings.append((node.lineno, f"arg to {fname}()", overlap, suggestion))

    return findings


def _suggest_ssot(overlap: list[str]) -> str:
    in_global = sum(1 for s in overlap if s in GLOBAL_EXCLUDED_DIRS)
    in_sovereign = sum(1 for s in overlap if s in SOVEREIGN_EXCLUDED_FOLDERS)
    in_discovery = sum(1 for s in overlap if s in DISCOVERY_EXCLUDED_TERRITORIES)
    parts = []
    if in_global:
        parts.append("GLOBAL_EXCLUDED_DIRS")
    if in_sovereign:
        parts.append("SOVEREIGN_EXCLUDED_FOLDERS")
    if in_discovery:
        parts.append("DISCOVERY_EXCLUDED_TERRITORIES")
    return " | ".join(parts) if parts else "SSOT constant"


def main() -> int:
    total = 0
    results: list[tuple[str, int, str, list[str], str]] = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if _excluded(py_file):
                continue
            rel = str(py_file.relative_to(ROOT)).replace("\\", "/")
            if rel in SSOT_PATHS:
                continue
            findings = scan_file(py_file)
            for lineno, varname, overlap, suggestion in findings:
                results.append((rel, lineno, varname, overlap, suggestion))
                total += 1

    print("=" * 70)
    print("AST HARDCODED-DIRECTORY AUDIT")
    print(f"SSOT owns {len(SSOT_DIR_NAMES)} directory names")
    print(f"Minimum overlap threshold: {MIN_OVERLAP}")
    print(f"Total violations found: {total}")
    print("=" * 70)

    for rel, lineno, varname, overlap, suggestion in results:
        print(f"\n  FILE : {rel}:{lineno}")
        print(f"  VAR  : {varname}")
        print(f"  DUPS : {overlap}")
        print(f"  USE  : {suggestion}")

    if total == 0:
        print("\nPASS: no hardcoded directory sets found outside SSOT.")
    else:
        print(f"\nFAIL: {total} location(s) must import from SSOT instead of hardcoding.")

    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
