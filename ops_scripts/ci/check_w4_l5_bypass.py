#!/usr/bin/env python3
"""Gate C2 — L5 guardrail bypass (plan W4.2).

Block gate reading ``mv_gateway_bypass_paths``. Each row is a provider /
capability invocation from a production layer that did not traverse an
L5 gateway.

Tier: B (block).
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
)


class L5BypassGate(WiringGate):
    gate_id = "C2_l5_bypass_pview"
    tier = "B"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT src_file, src_layer, provider_symbol, line_no, bypass_type
                FROM mv_gateway_bypass_paths
                """
            )
        )
        violations: list[Violation] = []
        for src_file, src_layer, provider_symbol, line_no, btype in tqdm(
            rows, desc="C2_l5_bypass", unit="row"
        ):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{src_file}:{line_no}",
                    rule="provider_bypasses_l5_gateway",
                    detail=f"{src_layer}: {provider_symbol} — {btype}",
                    extra={
                        "src_file": src_file,
                        "src_layer": src_layer,
                        "provider_symbol": provider_symbol,
                        "line_no": line_no,
                        "bypass_type": btype,
                    },
                )
            )
        return violations


def main() -> int:
    return cli_exit(L5BypassGate().execute())


if __name__ == "__main__":
    sys.exit(main())
