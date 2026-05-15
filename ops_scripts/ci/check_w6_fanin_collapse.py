#!/usr/bin/env python3
"""Gate H2 — fan-in collapse on high-centrality nodes (plan W6.2).

For the top-50 nodes by ``betweenness_approx`` in
``mv_hotspot_centrality`` (current snapshot), compare ``fan_in``
against the same node's fan_in in the prior snapshot. A drop > 30%
signals a sudden collapse — either legitimate decommissioning or,
more commonly, accidental breakage at an architectural chokepoint.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_snapshot_diff import connect_prior  # noqa: E402
from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

COLLAPSE_FRACTION = 0.30
TOP_N = 50


class FaninCollapseGate(WiringGate):
    gate_id = "H2_fanin_collapse_ratchet"
    tier = "R"
    baseline_filename = "wiring_fanin_collapse_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        prior_conn = connect_prior()
        if prior_conn is None:
            return []
        try:
            top_now = list(
                conn.execute(
                    """
                    SELECT resolved_path, layer, fan_in
                    FROM mv_hotspot_centrality
                    WHERE resolved_path IS NOT NULL
                    ORDER BY betweenness_approx DESC
                    LIMIT ?
                    """,
                    (TOP_N,),
                )
            )
            prior_fanin: dict[str, int] = {
                path: fanin
                for path, fanin in prior_conn.execute(
                    """
                    SELECT resolved_path, fan_in
                    FROM mv_hotspot_centrality
                    WHERE resolved_path IS NOT NULL
                    """
                )
            }
        finally:
            prior_conn.close()

        violations: list[Violation] = []
        for path, layer, now in tqdm(top_now, desc="H2_fanin_collapse", unit="node"):
            before = prior_fanin.get(path)
            if before is None or before <= 0:
                continue
            drop = (before - now) / before
            if drop < COLLAPSE_FRACTION:
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path,
                    rule="hotspot_fan_in_collapse",
                    detail=f"{layer}: fan_in {before}->{now} ({drop:.0%} drop)",
                    extra={
                        "resolved_path": path,
                        "layer": layer,
                        "fan_in_prior": before,
                        "fan_in_current": now,
                        "drop_fraction": round(drop, 4),
                    },
                )
            )
        return violations


def main() -> int:
    gate = FaninCollapseGate()
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
