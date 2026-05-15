"""CI gate L6-W2: no duplicate apps_rg L6 runtime engine module.

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f  W2.P3

- ``apps_rg/runtime/l6_shadow_learning.py`` must not exist.
- apps_rg/runtime must not define canonical-duplicate engine types
  (``L6ShadowLearningProducer``, ``RuntimeExhaustBundle``, ``ProposalPacket``).

Bypass: APPS_RG_L6_ENGINE_BYPASS=1
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "apps_rg" / "runtime"
FORBIDDEN_MODULE = RUNTIME / "l6_shadow_learning.py"
_FORBIDDEN_CLASS_NAMES = frozenset({
    "L6ShadowLearningProducer",
    "RuntimeExhaustBundle",
    "ProposalPacket",
})


def _scan_classes(path: Path) -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, OSError):
        return out
    rel = str(path.relative_to(REPO_ROOT))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in _FORBIDDEN_CLASS_NAMES:
            out.append((rel, node.lineno, node.name))
    return out


def run() -> int:
    if os.environ.get("APPS_RG_L6_ENGINE_BYPASS") == "1":
        print("[L6-W2] APPS_RG_L6_ENGINE_BYPASS=1 — skipping gate", flush=True)
        return 0

    violations: list[str] = []
    if FORBIDDEN_MODULE.exists():
        violations.append(f"Forbidden module exists: {FORBIDDEN_MODULE.relative_to(REPO_ROOT)}")

    if RUNTIME.exists():
        for py in sorted(RUNTIME.rglob("*.py")):
            if "schemas" in py.parts:
                continue
            for rel, lineno, name in _scan_classes(py):
                violations.append(f"{rel}:{lineno}  forbidden class {name!r}")

    if violations:
        print(f"[L6-W2] FAIL — {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W2] PASS — no duplicate apps_rg L6 engine surface", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
