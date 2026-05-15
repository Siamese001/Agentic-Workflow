#!/usr/bin/env python3
"""KPI H3 — anti-pattern velocity per 1k LOC (plan W6.5).

Ratio of P1/P2/P3 antipattern edges per 1,000 production LOC. A
rising ratio signals drift — the codebase is accumulating bad
patterns faster than it is removing them.

Tier: K (KPI). Emits JSONL row per run to
``artifacts/cursor/kpi_ap_velocity.jsonl``.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    LOG_DIR,
    Violation,
    WiringGate,
    cli_exit,
)

KPI_SINK = LOG_DIR / "kpi_ap_velocity.jsonl"

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rfp/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)

AP_RELATIONS = (
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "return_none_swallow",
    "global_state_mutation",
)


def _production_loc() -> int:
    total = 0
    files = list(REPO_ROOT.rglob("*.py"))
    for py in tqdm(files, desc="H3_ap_loc_scan", unit="file", leave=False):
        rel = py.relative_to(REPO_ROOT).as_posix()
        if not rel.startswith(PRODUCTION_ROOTS):
            continue
        if rel.startswith(("tests/", "tools/archive/", "archives/")):
            continue
        try:
            with py.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.strip():
                        total += 1
        except OSError:
            continue
    return total


class ApVelocityKpiGate(WiringGate):
    gate_id = "H3_ap_velocity_kpi"
    tier = "K"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        counts: dict[str, int] = {}
        for rel in tqdm(AP_RELATIONS, desc="H3_ap_velocity", unit="ap"):
            (cnt,) = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,)).fetchone()
            counts[rel] = cnt

        loc = _production_loc()
        total_ap = sum(counts.values())
        per_kloc = (total_ap / (loc / 1000.0)) if loc > 0 else 0.0

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with KPI_SINK.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "production_loc": loc,
                        "ap_total": total_ap,
                        "ap_per_kloc": round(per_kloc, 2),
                        "by_relation": counts,
                    }
                )
                + "\n"
            )
        return []  # K-tier


def main() -> int:
    return cli_exit(ApVelocityKpiGate().execute())


if __name__ == "__main__":
    sys.exit(main())
