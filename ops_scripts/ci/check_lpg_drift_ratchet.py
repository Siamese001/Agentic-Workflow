#!/usr/bin/env python3
"""Gate L2 — L_PG (Prompt Governance / knowledge plane) drift ratchet (plan W3.2).

L_PG modules (agentic_core/knowledge/**, agentic_core/prompt_governance/**,
...) are the retrieval + governance internals. They should be reached
primarily through their package __init__.py from the canonical L0 ingress.
Imports into L_PG internals from non-L_PG production layers are a drift
signal — the caller is coupling to internals instead of using the public
contract.

Tier: R (ratchet). Seed today's state; block any new drift edges.

Fail condition for each drift edge:
    src.layer IN {L0..L6, L_APP, L_OPS, L_RUNTIME, L_SHARED}
    dst.layer == 'L_PG'
    dst.resolved_path does NOT end in '/__init__.py'

Excluded sources:
    - L_PG itself (intra-plane imports are fine)
    - L_TEST, L_TOOLS (tests and tools are allowed to poke internals)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

ALLOWED_SRC_LAYERS = {
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_OPS",
    "L_RUNTIME",
    "L_SHARED",
    "L_SL",
    "L_INFRA",
}


class LpgDriftRatchetGate(WiringGate):
    gate_id = "L2_lpg_drift_ratchet"
    tier = "R"
    baseline_filename = "wiring_lpg_drift_ratchet.json"

    def run(self, conn) -> list[Violation]:
        rows = conn.execute(
            """
            SELECT DISTINCT
                src.resolved_path, src.layer,
                dst.resolved_path
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND dst.layer = 'L_PG'
              AND src.layer != 'L_PG'
              AND src.resolved_path IS NOT NULL
              AND dst.resolved_path IS NOT NULL
              AND src.resolved_path != dst.resolved_path
            """
        ).fetchall()

        violations: list[Violation] = []
        for src_path, src_layer, dst_path in rows:
            if src_layer not in ALLOWED_SRC_LAYERS:
                continue
            if dst_path.endswith("/__init__.py"):
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{src_path}->{dst_path}",
                    rule="lpg_internal_reached_from_outside",
                    detail=(
                        f"{src_layer}:{src_path} imports L_PG internal "
                        f"{dst_path}; use the package public contract "
                        "(__init__.py) instead"
                    ),
                    extra={
                        "src_path": src_path,
                        "src_layer": src_layer,
                        "dst_path": dst_path,
                    },
                )
            )
        return violations


def main() -> int:
    gate = LpgDriftRatchetGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
