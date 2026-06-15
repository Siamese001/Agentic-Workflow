"""CI gate L6-W4d: L6_learning must not import UWG / L4 writer modules.

Flags ``from agentic_core.runtime.uwg`` / ``import`` lines and ``l4_writer`` /
``L4Writer`` tokens in ``agentic_core/L6_system_learning/future_run_promotion/**/*.py`` (excluding comments).

Bypass: L6_L4_WRITE_BYPASS=1
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
L6_DIR = REPO_ROOT / "agentic_core" / "L6_system_learning" / "future_run_promotion"
_BAD_FRAGMENTS = (
    "from agentic_core.runtime.uwg",
    "import agentic_core.runtime.uwg",
    "l4_writer",
    "L4Writer",
)


def run() -> int:
    if os.environ.get("L6_L4_WRITE_BYPASS") == "1":
        print("[L6-W4d] L6_L4_WRITE_BYPASS=1 — skipping gate", flush=True)
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
                low = line.lower()
                for frag in _BAD_FRAGMENTS:
                    if frag.lower() in low:
                        violations.append(f"{rel}:{idx}  matched {frag!r}")

    if violations:
        print(f"[L6-W4d] FAIL — {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W4d] PASS — no UWG/L4 writer coupling in L6_learning", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
