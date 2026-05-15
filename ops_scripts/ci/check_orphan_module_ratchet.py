#!/usr/bin/env python3
"""Gate A1 — orphan module ratchet (plan wiring-ci / ADR-034).

Counts **production** modules that have **zero incoming ``imports`` edges**
(fan-in on imports == 0). Matches the orphan definition used by H1
(``check_w6_new_orphans_delta.py``), scoped with the same production-root
allowlist as gates E1/A3/M1.

Tier: **R** (ratchet) — CI fails only when the active orphan count **exceeds**
the sealed baseline in ``ops_scripts/ci/baselines/wiring_orphan_module_ratchet.json``.

Registry note (``adg_gates/unified_registry.py``): SQL plane gate
``v_dead_production_imports`` overlaps ADG-side orphan/import hygiene; this script
remains the canonical **wiring-CI ratchet** entry wired from
``run_contract_gates.py``.

Seed / refresh baseline (operators):

    python ops_scripts/ci/check_orphan_module_ratchet.py --seed
"""

from __future__ import annotations

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

PROD_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_PG", "L_SHARED")

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
EXCLUDE_PREFIXES = (
    "tests/",
    "tools/archive/",
    "tools/bench/",
    "tools/debug/",
    "tools/diag/",
    "archives/",
)

_ORPHAN_SQL = """
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


class OrphanModuleRatchetGate(WiringGate):
    gate_id = "A1_orphan_module_ratchet"
    tier = "R"
    baseline_filename = "wiring_orphan_module_ratchet.json"

    def run(self, conn) -> list[Violation]:
        violations: list[Violation] = []
        for path, layer in conn.execute(_ORPHAN_SQL):
            if not path.startswith(PRODUCTION_ROOTS):
                continue
            if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path,
                    rule="module_zero_import_fanin",
                    detail=f"{layer}: no incoming imports edges",
                    extra={"resolved_path": path, "layer": layer},
                )
            )
        return violations


def main() -> int:
    gate = OrphanModuleRatchetGate()
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
        print(
            f"[{gate.gate_id}] current={len(result.violations)} "
            f"baseline={result.baseline_count}"
        )
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
