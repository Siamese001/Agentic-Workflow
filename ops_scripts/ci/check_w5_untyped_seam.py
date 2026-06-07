#!/usr/bin/env python3
"""Gate F1 — untyped cross-layer seam (plan W5.4).

Cross-layer ``imports`` edges whose target symbol has an empty
``type_surface`` column. Typed seams are a Thoughtworks fitness-
function principle: cross-layer boundaries without contract surfaces
invite silent breakage.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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


class UntypedSeamGate(WiringGate):
    gate_id = "F1_untyped_seam_ratchet"
    tier = "R"
    baseline_filename = "wiring_untyped_seam_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT
                src.resolved_path AS src_path,
                src.layer         AS src_layer,
                dst.resolved_path AS dst_path,
                dst.layer         AS dst_layer,
                COALESCE(dst.type_surface, '') AS dst_type_surface
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND src.layer IN ('L0','L1','L2','L3','L4','L5','L6')
              AND dst.layer IN ('L0','L1','L2','L3','L4','L5','L6')
              AND src.layer <> dst.layer
              AND (dst.type_surface IS NULL OR dst.type_surface = '')
              AND src.resolved_path IS NOT NULL
              AND dst.resolved_path IS NOT NULL
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for src_path, src_layer, dst_path, dst_layer, _ts in tqdm(rows, desc="F1_untyped_seam", unit="edge"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{src_path} -> {dst_path}",
                    rule="cross_layer_import_empty_type_surface",
                    detail=f"{src_layer}->{dst_layer}; dst has no type surface",
                    extra={
                        "src_path": src_path,
                        "src_layer": src_layer,
                        "dst_path": dst_path,
                        "dst_layer": dst_layer,
                    },
                )
            )
        return violations


def main() -> int:
    gate = UntypedSeamGate()
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
