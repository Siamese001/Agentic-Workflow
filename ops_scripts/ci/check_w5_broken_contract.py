#!/usr/bin/env python3
"""Gate F2 — broken-contract consumer (plan W5.5).

Flags ``imports`` edges whose target module has zero ``exports``
edges — i.e. the importer references a symbol the target module
does not publicly expose. Signals contract drift after a refactor.

Tier: R (ratchet).
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


class BrokenContractGate(WiringGate):
    gate_id = "F2_broken_contract_ratchet"
    tier = "R"
    baseline_filename = "wiring_broken_contract_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT DISTINCT
                src.resolved_path AS src_path,
                src.layer         AS src_layer,
                dst.resolved_path AS dst_path,
                dst.layer         AS dst_layer
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND dst.entity_type = 'module'
              AND src.resolved_path IS NOT NULL
              AND dst.resolved_path IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM edges xe
                  WHERE xe.src_id = dst.id AND xe.relation_type = 'exports'
              )
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for src_path, src_layer, dst_path, dst_layer in tqdm(rows, desc="F2_broken_contract", unit="edge"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{src_path} -> {dst_path}",
                    rule="import_target_has_no_exports",
                    detail=f"{src_layer}->{dst_layer}; target publishes 0 exports",
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
    gate = BrokenContractGate()
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
