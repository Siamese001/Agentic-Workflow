#!/usr/bin/env python3
"""Gate B2 — layer-skip ratchet (plan W3.1).

Flags ``imports`` edges where src and dst live on production layers
L0..L6 and the absolute ordinal distance is > 1 (i.e. the edge skips
at least one intermediate layer). Gravity direction is handled by
SC-1 structural conformance — this gate focuses purely on *skip
distance*, a hygiene signal that surfaces when modules reach across
the cognitive/execution/state spine without going through the layers
in between.

Tier: R (ratchet). Baseline locks current count; any *new* skip edge
regresses the build.

Out of scope:
  - L_APP / L_PG / L_TOOLS / L_TEST / L_SHARED (these are domain
    namespaces, not chain layers, and have their own gates such as
    L2_lpg_drift_ratchet).
  - ``imports`` edges where either end is an un-layered module
    (``UNKNOWN`` or NULL layer).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

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

SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")


def _ordinal(layer: str) -> int | None:
    if layer not in SPINE_LAYERS:
        return None
    try:
        return int(layer[1:])
    except ValueError:
        return None


class LayerSkipGate(WiringGate):
    gate_id = "B2_layer_skip_ratchet"
    tier = "R"
    baseline_filename = "wiring_layer_skip_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT src.resolved_path, src.layer,
                   dst.resolved_path, dst.layer
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND src.layer IN ('L0','L1','L2','L3','L4','L5','L6')
              AND dst.layer IN ('L0','L1','L2','L3','L4','L5','L6')
              AND src.resolved_path IS NOT NULL
              AND dst.resolved_path IS NOT NULL
        """
        violations: list[Violation] = []
        rows = list(conn.execute(query))
        for src_path, src_layer, dst_path, dst_layer in tqdm(rows, desc="B2_layer_skip", unit="edge"):
            a = _ordinal(src_layer)
            b = _ordinal(dst_layer)
            if a is None or b is None:
                continue
            skip = abs(a - b)
            if skip <= 1:
                continue
            subject = f"{src_path} -> {dst_path}"
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=subject,
                    rule="layer_skip_distance_gt_1",
                    detail=f"{src_layer}->{dst_layer} skip={skip}",
                    extra={
                        "src_path": src_path,
                        "src_layer": src_layer,
                        "dst_path": dst_path,
                        "dst_layer": dst_layer,
                        "skip_distance": skip,
                    },
                )
            )
        return violations


def main() -> int:
    gate = LayerSkipGate()
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
