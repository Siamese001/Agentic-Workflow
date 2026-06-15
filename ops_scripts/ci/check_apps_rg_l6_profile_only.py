"""CI gate L6-W2c: apps_rg must not import core L6 engine classes directly.

AST-scan ``apps_rg/**/*.py`` for ``from agentic_core.L6_system_learning.future_run_promotion import`` that
names engine-tier symbols (CompletedRunEvaluator, RCASynthesizer,
FutureRunProposalBuilder, PromotionGauntlet).

Profile-driven wiring must not hard-import these engines from app code.

Bypass: APPS_RG_L6_PROFILE_ONLY_BYPASS=1
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG = REPO_ROOT / "apps_rg"
_FORBIDDEN_NAMES = frozenset({
    "CompletedRunEvaluator",
    "RCASynthesizer",
    "FutureRunProposalBuilder",
    "PromotionGauntlet",
})


def _check_file(path: Path) -> list[str]:
    out: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, OSError):
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "agentic_core.L6_system_learning.future_run_promotion":
            continue
        for alias in node.names:
            if alias.name in _FORBIDDEN_NAMES:
                rel = path.relative_to(REPO_ROOT)
                out.append(f"{rel}:{node.lineno}  imports {alias.name!r}")
    return out


def run() -> int:
    if os.environ.get("APPS_RG_L6_PROFILE_ONLY_BYPASS") == "1":
        print("[L6-W2c] APPS_RG_L6_PROFILE_ONLY_BYPASS=1 — skipping gate", flush=True)
        return 0

    violations: list[str] = []
    if APPS_RG.is_dir():
        for py in sorted(APPS_RG.rglob("*.py")):
            violations.extend(_check_file(py))

    if violations:
        print(f"[L6-W2c] FAIL — {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W2c] PASS — no direct L6 engine imports from apps_rg", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
