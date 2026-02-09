#!/usr/bin/env python3
"""
V15 P0.2 — Adapter Prohibition AST Scanner.

Scans all Python files under agentic_core/ for imports of AdapterBase
or class definitions inheriting from AdapterBase/HealingAdapter.
Files under archives/ are excluded.

Exit code 0 = no violations.
Exit code 1 = violations found.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SCAN_ROOTS = [Path("agentic_core")]
EXCLUDED_PREFIXES = (
    "archives",
    "archives/deprecated",
)
# v15-exception annotated files are allowed
EXCEPTION_MARKER = "v15-exception:"

PROHIBITED_NAMES = frozenset({"AdapterBase", "HealingAdapter", "AdapterBaseAdapter"})


def _is_excluded(path: Path) -> bool:
    parts = path.as_posix()
    return any(parts.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def scan_file(filepath: Path) -> list[str]:
    """Scan a single Python file for AdapterBase usage. Returns violation messages."""
    violations: list[str] = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return violations

    # Check for v15-exception annotation
    if EXCEPTION_MARKER in source:
        return violations

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        # Check imports: from X import AdapterBase / import AdapterBase
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in PROHIBITED_NAMES:
                    violations.append(
                        f"{filepath}:{node.lineno}: imports prohibited name '{alias.name}'",
                    )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name_parts = alias.name.split(".")
                if any(part in PROHIBITED_NAMES for part in name_parts):
                    violations.append(
                        f"{filepath}:{node.lineno}: imports prohibited module '{alias.name}'",
                    )
        # Check class inheritance: class Foo(AdapterBase) or class Foo(HealingAdapter)
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name and base_name in PROHIBITED_NAMES:
                    violations.append(
                        f"{filepath}:{node.lineno}: class '{node.name}' "
                        f"inherits from prohibited '{base_name}'",
                    )
    return violations


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    all_violations: list[str] = []

    for scan_root in SCAN_ROOTS:
        root = project_root / scan_root
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            rel = py_file.relative_to(project_root)
            if _is_excluded(rel):
                continue
            all_violations.extend(scan_file(py_file))

    if all_violations:
        print(f"FAIL: {len(all_violations)} AdapterBase prohibition violation(s):")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print("PASS: No AdapterBase prohibition violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
