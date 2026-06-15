"""CI gate L6-W2b: only ``PackageDrivenL6Binding`` ends with ``Binding`` in L6_learning.

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f  W6

Bypass: PACKAGE_DRIVEN_L6_ONLY_BYPASS=1
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
L6_DIR = REPO_ROOT / "agentic_core" / "L6_system_learning" / "future_run_promotion"


def run() -> int:
    if os.environ.get("PACKAGE_DRIVEN_L6_ONLY_BYPASS") == "1":
        print("[L6-W2b] PACKAGE_DRIVEN_L6_ONLY_BYPASS=1 — skipping gate", flush=True)
        return 0

    binding_classes: list[tuple[str, str, int]] = []
    if not L6_DIR.is_dir():
        print("[L6-W2b] SKIP — L6_learning directory missing", flush=True)
        return 0

    for py in sorted(L6_DIR.glob("*.py")):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Binding"):
                binding_classes.append((py.name, node.name, node.lineno))

    allowed = {("package_driven_l6_binding.py", "PackageDrivenL6Binding")}
    seen = {(p, n) for p, n, _ in binding_classes}
    extra = seen - allowed
    if extra:
        print("[L6-W2b] FAIL — unexpected *Binding classes:", flush=True)
        for p, n, ln in binding_classes:
            if (p, n) in extra:
                print(f"  {p}:{ln}  class {n}", flush=True)
        return 1

    if ("package_driven_l6_binding.py", "PackageDrivenL6Binding") not in seen:
        print(
            "[L6-W2b] FAIL — PackageDrivenL6Binding missing from agentic_core/L6_system_learning/future_run_promotion",
            flush=True,
        )
        return 1

    print("[L6-W2b] PASS — single PackageDrivenL6Binding surface", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
