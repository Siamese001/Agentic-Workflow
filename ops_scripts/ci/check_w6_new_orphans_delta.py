#!/usr/bin/env python3
"""Gate H1 — new-orphan delta (plan W6.1).

Compares the current snapshot's orphan set (production modules with no
incoming module-or-symbol ``imports`` fan-in) against the prior snapshot's
orphan set.
Any module that is an orphan NOW but was NOT an orphan in the prior
snapshot is a new orphan — flagged.

Tier: R (ratchet, but with implicit zero baseline because every
post-commit delta should normalize to zero new orphans).
"""

from __future__ import annotations

# W4 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md
# §6 + agentic_core/adg/artifact/consumer_mode.py).
# Tracks orphan-set delta across snapshots — hygiene signal, not a verdict.
__adg_consumer_mode__ = "risk"

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
_MODULE_QUERY = """
    SELECT n.resolved_path, n.layer
    FROM nodes n
    WHERE n.entity_type = 'module'
      AND n.resolved_path IS NOT NULL
      AND n.layer IN ({layers})
""".format(layers=",".join(f"'{layer}'" for layer in PROD_LAYERS))
_IMPORTED_MODULE_PATH_QUERY = """
    SELECT DISTINCT imported.resolved_path
    FROM edges e
    JOIN nodes imported ON imported.id = e.dst_id
    JOIN nodes importer ON importer.id = e.src_id
    WHERE e.relation_type = 'imports'
      AND imported.resolved_path IS NOT NULL
      AND imported.resolved_path != ''
      AND COALESCE(importer.resolved_path, '') != imported.resolved_path
"""


def _orphan_set(conn: sqlite3.Connection) -> dict[str, str]:
    modules = {p: layer for p, layer in conn.execute(_MODULE_QUERY)}
    imported_paths = {p for (p,) in conn.execute(_IMPORTED_MODULE_PATH_QUERY)}
    return {p: layer for p, layer in modules.items() if p not in imported_paths}


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
