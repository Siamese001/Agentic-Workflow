"""CI gate L6-W4c: L6_learning must not call X3 emit helpers.

Scans ``agentic_core/L6_system_learning/future_run_promotion/**/*.py`` for ``emit_x3`` or ``X3Disposition(``.

Bypass: L6_X3_EMIT_BYPASS=1
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
L6_DIR = REPO_ROOT / "agentic_core" / "L6_system_learning" / "future_run_promotion"
TOKENS = ("emit_x3", "X3Disposition(")


def run() -> int:
    if os.environ.get("L6_X3_EMIT_BYPASS") == "1":
        print("[L6-W4c] L6_X3_EMIT_BYPASS=1 — skipping gate", flush=True)
        return 0

    violations: list[str] = []
    if L6_DIR.is_dir():
        for py in sorted(L6_DIR.rglob("*.py")):
            try:
                lines = py.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            rel = py.relative_to(REPO_ROOT)
            for idx, line in enumerate(lines, 1):
                if line.strip().startswith("#"):
                    continue
                for tok in TOKENS:
                    if tok in line:
                        violations.append(f"{rel}:{idx}  contains {tok!r}")

    if violations:
        print(f"[L6-W4c] FAIL — {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W4c] PASS — no X3 emit surface in L6_learning", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
