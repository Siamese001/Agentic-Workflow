#!/usr/bin/env python3
"""Gate AUDIT-5 — env-var location ratchet.

Flags modules outside ``*/config/*`` or ``*_config.py`` that read
process environment via ``os.environ`` / ``os.getenv``. Env-reads in
production code outside the config layer scatter configuration into
implementation modules and break replay/test isolation.

Detection is **edge-based**: a module is flagged only when it has an
outgoing edge whose dst node represents ``os.environ``, ``os.getenv``,
``getenv``, or ``environ`` — eliminating the false positives that arise
from mere identifier-name pattern matching.

Tier R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
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

MAINLINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5")


class EnvVarInConfigLayerGate(WiringGate):
    gate_id = "AUDIT_5_env_var_in_config_layer"
    tier = "R"
    baseline_filename = "audit_env_var_in_config_layer.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        mainline_placeholders = ",".join("?" * len(MAINLINE_LAYERS))
        cur.execute(
            f"""
            SELECT DISTINCT src.resolved_path, src.layer, dst.adg_name
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE src.entity_type = 'module'
              AND src.layer IN ({mainline_placeholders})
              AND src.resolved_path NOT LIKE '%/config/%'
              AND src.resolved_path NOT LIKE '%_config.py'
              AND src.resolved_path NOT LIKE 'tests/%'
              AND src.resolved_path NOT LIKE 'archives/%'
              AND (
                dst.adg_name LIKE '%os.environ%'
                OR dst.adg_name LIKE '%os.getenv%'
                OR dst.adg_name = 'getenv'
                OR dst.adg_name = 'environ'
              )
            ORDER BY src.layer, src.resolved_path
            """,
            MAINLINE_LAYERS,
        )
        violations: list[Violation] = []
        for src_path, src_layer, env_target in cur.fetchall():
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=src_path,
                    rule="env_var_read_outside_config_layer",
                    detail=f"layer={src_layer} reads={env_target}",
                    extra={
                        "src_path": src_path,
                        "src_layer": src_layer,
                        "env_target": env_target,
                    },
                )
            )
        return violations


def main() -> int:
    gate = EnvVarInConfigLayerGate()
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
