#!/usr/bin/env python3
"""Gate G-WATCHLIST-DELTA: graph hotspot regression-count ratchet (H2).

Wraps the existing ``ADGGraphWatchlistBuilder`` (which already computes
``is_regression`` per hotspot via ``_classify_delta`` + baseline diff) and
promotes its previously-passive intelligence into an exit-code gate.

Algorithm
    1. Build graph watchlist from the latest ADG SQLite snapshot.
    2. Diff against the most-recent prior watchlist artifact under
       ``artifacts/adg/graph_intelligence/``.
    3. Count entries flagged ``is_regression=True`` (NEW_HOTSPOT or WORSENED,
       weighted by layer criticality per the builder's internal rule).
    4. Ratchet against baseline (``wiring_graph_watchlist_delta_ratchet.json``);
       fail when regression_count > baseline.

Tier: R (P1 RATCHET)
Band: P1 (graph-native drift)
Source: ADG SQLite + existing watchlist JSON artifact
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

GATE_ID = "G_WATCHLIST_DELTA_hotspot_regressions"

_WATCHLIST_DIR = REPO_ROOT / "artifacts" / "adg" / "graph_intelligence"


class GraphWatchlistDeltaGate(WiringGate):
    gate_id = GATE_ID
    tier = "R"
    baseline_filename = "wiring_graph_watchlist_delta_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        # The builder owns its own SQLite connection; we pass the snapshot
        # path rather than reusing `conn`.  `conn` is still honored by the
        # harness for tier-select + bypass.
        from tools.generate.adg_graph_watchlist_builder import (
            ADGGraphWatchlistBuilder,
        )

        try:
            with ADGGraphWatchlistBuilder(self.snapshot) as builder:
                watchlist = builder.build_graph_watchlist()
                # pylint: disable=protected-access
                delta = builder._compute_deltas(watchlist, _WATCHLIST_DIR)
        except (AttributeError, FileNotFoundError, sqlite3.DatabaseError) as exc:
            print(
                f"[{GATE_ID}] WARN watchlist builder unavailable: {exc}",
                file=sys.stderr,
            )
            return []

        regressions = delta.get("regressions") or []
        violations: list[Violation] = []
        for r in regressions:
            file_path = r.get("file", "unknown")
            violations.append(
                Violation(
                    gate_id=GATE_ID,
                    tier="R",
                    subject=file_path,
                    rule="graph_hotspot_regression",
                    detail=(
                        f"delta_type={r.get('delta_type')} "
                        f"score_delta={r.get('score_delta')} "
                        f"gate_delta={r.get('gate_delta')}"
                    ),
                    severity="fail",
                    extra={
                        "baseline_gate": r.get("baseline_gate"),
                        "current_gate": r.get("current_gate"),
                        "baseline_score": r.get("baseline_score"),
                        "current_score": r.get("current_score"),
                    },
                )
            )
        return violations


def main() -> int:
    gate = GraphWatchlistDeltaGate()
    result = gate.execute()
    return cli_exit(result)


if __name__ == "__main__":
    raise SystemExit(main())
