#!/usr/bin/env python3
"""Gate H4 — MV staleness via total-edge delta (plan W6.6).

Blocks if the total ``edges`` count of the current snapshot differs
from the prior snapshot by more than ``DELTA_THRESHOLD`` (default 5%).
A rapid edge-count swing is a strong signal that either a large
refactor landed without a matching MV refresh, or that the snapshot
generator is ingesting incomplete data.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_snapshot_diff import connect_prior  # noqa: E402
from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

DELTA_THRESHOLD = 0.05


class MvStalenessGate(WiringGate):
    gate_id = "H4_mv_staleness_ratchet"
    tier = "R"
    baseline_filename = "wiring_mv_staleness_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        prior_conn = connect_prior()
        if prior_conn is None:
            return []
        try:
            (current,) = conn.execute("SELECT COUNT(*) FROM edges").fetchone()
            (prior,) = prior_conn.execute("SELECT COUNT(*) FROM edges").fetchone()
        finally:
            prior_conn.close()

        if prior <= 0:
            return []
        delta = abs(current - prior) / prior
        if delta < DELTA_THRESHOLD:
            return []
        direction = "grew" if current > prior else "shrank"
        return [
            Violation(
                gate_id=self.gate_id,
                tier=self.tier,
                subject="edges_total",
                rule="mv_edge_count_delta_exceeded",
                detail=f"edges {direction} {prior}->{current} ({delta:.1%} > {DELTA_THRESHOLD:.0%})",
                extra={
                    "edges_prior": prior,
                    "edges_current": current,
                    "delta_fraction": round(delta, 4),
                    "threshold": DELTA_THRESHOLD,
                },
            )
        ]


def main() -> int:
    gate = MvStalenessGate()
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
