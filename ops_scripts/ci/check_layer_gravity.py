#!/usr/bin/env python3
"""Gate L1 — layer gravity ratchet (plan wiring-ci / ADR-034).

Uses the same **forbidden reach** matrix as structural conformance SC-1
(``tools/generate/validation/gates.py`` ``_GRAVITY_FORBIDDEN``): directed
edges (imports, reads_from, controls_flow, flows_to) whose source/target
layers violate upward/downward gravity, minus sites exempted via the shared
guardian SSOT filter.

Tier: **R** (ratchet). CI fails only when the active count **exceeds** the
sealed baseline in ``ops_scripts/ci/baselines/wiring_layer_gravity_ratchet.json``.

Seed / refresh baseline (operators):

    python ops_scripts/ci/check_layer_gravity.py --seed

References:
    ADR-034 docs/architecture/adr/ADR-034-wiring-ci-gate-plane-and-uwg-allowlist.md
    tools/generate/validation/gates.py (_query_sc1_gravity)
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

# Mirrors tools/generate/validation/gates.py::_GRAVITY_FORBIDDEN — keep in sync.
_GRAVITY_FORBIDDEN: dict[str, set[str]] = {
    "L0": {"L1", "L2", "L3", "L6"},
    "L1": {"L2", "L3", "L6"},
    "L2": {"L0", "L1", "L6"},
    "L6": {"L2"},
}


class LayerGravityRatchetGate(WiringGate):
    gate_id = "L1_layer_gravity"
    tier = "R"
    baseline_filename = "wiring_layer_gravity_ratchet.json"

    def run(self, conn) -> list[Violation]:
        from tools.adg.core.guardian_filter import is_layer_violation_exempted  # noqa: PLC0415

        rows = conn.execute(
            """
            SELECT e.source_file, e.line_no, n_src.layer, n_dst.layer, e.relation_type
            FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE e.relation_type IN ('imports', 'reads_from', 'controls_flow', 'flows_to')
              AND n_src.layer IS NOT NULL AND n_src.layer != ''
              AND n_dst.layer IS NOT NULL AND n_dst.layer != ''
              AND n_src.layer != n_dst.layer
            """
        ).fetchall()

        violations: list[Violation] = []
        for src_file, line_no, src_layer, dst_layer, rel_type in rows:
            forbidden = _GRAVITY_FORBIDDEN.get(src_layer, set())
            if dst_layer not in forbidden:
                continue
            if is_layer_violation_exempted(src_file, line_no, repo_root=REPO_ROOT):
                continue
            path_key = src_file or ""
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{path_key}:{line_no or 0}",
                    rule="layer_gravity_violation",
                    detail=f"{src_layer}->{dst_layer} via {rel_type}",
                    extra={
                        "source_file": path_key,
                        "line_no": line_no or 0,
                        "src_layer": src_layer,
                        "dst_layer": dst_layer,
                        "relation_type": rel_type,
                    },
                )
            )
        violations.sort(key=lambda v: (v.subject, v.detail))
        return violations


def main() -> int:
    gate = LayerGravityRatchetGate()
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
    raise SystemExit(main())
