"""CI gate L6-W4a: G29 Learning Firewall invariants.

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f  W4

- ``PromotionGauntlet.GATE_ID`` must equal ``\"G29\"``.
- No ``uwg_review_status=\"APPROVED\"`` string assignment outside
  ``agentic_core/runtime/uwg/`` (static substring scan; excludes comments-only
  lines heuristically).

Bypass: G29_FIREWALL_BYPASS=1
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UWG_DIR = REPO_ROOT / "agentic_core" / "runtime" / "uwg"
NEEDLE = 'uwg_review_status="APPROVED"'
NEEDLE_ALT = "uwg_review_status='APPROVED'"


def run() -> int:
    if os.environ.get("G29_FIREWALL_BYPASS") == "1":
        print("[L6-W4a] G29_FIREWALL_BYPASS=1 — skipping gate", flush=True)
        return 0

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet

    if PromotionGauntlet.GATE_ID != "G29":
        print(
            f"[L6-W4a] FAIL — PromotionGauntlet.GATE_ID={PromotionGauntlet.GATE_ID!r} "
            "expected 'G29'",
            flush=True,
        )
        return 1

    violations: list[str] = []
    for root in (REPO_ROOT / "apps_rg", REPO_ROOT / "agentic_core", REPO_ROOT / "tests"):
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            try:
                rel = py.relative_to(REPO_ROOT)
            except ValueError:
                continue
            if UWG_DIR in py.parents or str(rel).replace("\\", "/").startswith(
                "agentic_core/runtime/uwg/"
            ):
                continue
            try:
                lines = py.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for idx, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if NEEDLE in line or NEEDLE_ALT in line:
                    violations.append(f"{rel}:{idx}")

    if violations:
        print(
            f"[L6-W4a] FAIL — uwg_review_status APPROVED outside UWG ({len(violations)}):",
            flush=True,
        )
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W4a] PASS — G29 id + UWG APPROVED placement OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
