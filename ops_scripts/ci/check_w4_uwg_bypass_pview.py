#!/usr/bin/env python3
"""Gate C1 — UWG write-path bypass (plan W4.1).

Block gate that mirrors ``v_p0_write_bypass_uwg`` — any row is a
P0 violation (durable write escaping the Universal Write Gateway).
Complements S2_uwg_bypass_ratchet (which is a RATCHET overlay on the
same underlying edges with a named allowlist contract).

Tier: B (block).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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
)


class UwgBypassPViewGate(WiringGate):
    gate_id = "C1_uwg_bypass_pview"
    tier = "B"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT writer_file, writer_layer, write_symbol, write_line, violation_type
                FROM v_p0_write_bypass_uwg
                """
            )
        )
        violations: list[Violation] = []
        for writer_file, writer_layer, write_symbol, write_line, vtype in tqdm(
            rows, desc="C1_uwg_bypass", unit="row"
        ):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{writer_file}:{write_line}",
                    rule="write_bypasses_uwg",
                    detail=f"{writer_layer}: {write_symbol} — {vtype}",
                    extra={
                        "writer_file": writer_file,
                        "writer_layer": writer_layer,
                        "write_symbol": write_symbol,
                        "write_line": write_line,
                    },
                )
            )
        return violations


def main() -> int:
    return cli_exit(UwgBypassPViewGate().execute())


if __name__ == "__main__":
    sys.exit(main())
