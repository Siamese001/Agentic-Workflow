"""CI gate L6-W4b: L6_learning must not reference X3Disposition (mutation vector).

Static scan of ``agentic_core/L6_system_learning/future_run_promotion/**/*.py`` for ``X3Disposition`` token
outside comments (line-based heuristic).

Bypass: L6_MUTATION_FAIL_CLOSED=1 is advisory mirror; bypass: L6_MUTATION_BYPASS=1
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
L6_DIR = REPO_ROOT / "agentic_core" / "L6_system_learning" / "future_run_promotion"
TOKEN = "X3Disposition"


def run() -> int:
    if os.environ.get("L6_MUTATION_BYPASS") == "1":
        print("[L6-W4b] L6_MUTATION_BYPASS=1 — skipping gate", flush=True)
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
                if TOKEN in line and not line.strip().startswith("#"):
                    violations.append(f"{rel}:{idx}")

    if violations:
        print(f"[L6-W4b] FAIL — {TOKEN} referenced ({len(violations)}):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print(f"[L6-W4b] PASS — no {TOKEN} in L6_learning", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
