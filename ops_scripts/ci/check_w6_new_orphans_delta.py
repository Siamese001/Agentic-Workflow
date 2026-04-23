#!/usr/bin/env python3
"""Gate H1 — new-orphan delta (plan W6.1).

Compares the current snapshot's orphan set (production modules with
``fan_in=0`` on ``imports``) against the prior snapshot's orphan set.
Any module that is an orphan NOW but was NOT an orphan in the prior
snapshot is a new orphan — flagged.

Tier: R (ratchet, but with implicit zero baseline because every
post-commit delta should normalize to zero new orphans).
"""

from __future__ import annotations

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

PROD_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_PG", "L_SHARED")
_ORPHAN_QUERY = """
    SELECT n.resolved_path, n.layer
    FROM nodes n
    WHERE n.entity_type = 'module'
      AND n.resolved_path IS NOT NULL
      AND n.layer IN ({layers})
      AND NOT EXISTS (
          SELECT 1 FROM edges e
          WHERE e.dst_id = n.id AND e.relation_type = 'imports'
      )
""".format(layers=",".join(f"'{layer}'" for layer in PROD_LAYERS))


def _orphan_set(conn: sqlite3.Connection) -> dict[str, str]:
    return {p: layer for p, layer in conn.execute(_ORPHAN_QUERY)}


class NewOrphansDeltaGate(WiringGate):
    gate_id = "H1_new_orphans_delta_ratchet"
    tier = "R"
    baseline_filename = "wiring_new_orphans_delta_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        prior_conn = connect_prior()
        if prior_conn is None:
            return []
        try:
            prior = _orphan_set(prior_conn)
        finally:
            prior_conn.close()
        current = _orphan_set(conn)
        new_orphans = [(p, layer) for p, layer in current.items() if p not in prior]
        violations: list[Violation] = []
        for path, layer in tqdm(new_orphans, desc="H1_new_orphans", unit="mod"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path,
                    rule="new_orphan_vs_prior_snapshot",
                    detail=f"{layer}: became orphan since prior snapshot",
                    extra={"resolved_path": path, "layer": layer},
                )
            )
        return violations


def main() -> int:
    gate = NewOrphansDeltaGate()
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
