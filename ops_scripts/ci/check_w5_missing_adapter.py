#!/usr/bin/env python3
"""Gate F3 — missing adapter for declared Protocol / abstract class (plan W5.6).

Flags class nodes whose ``adg_name`` matches common Protocol/abstract
patterns (``*Protocol``, ``*ABC``, ``*Interface``) and that have zero
``implements`` consumers. An abstract type without a concrete adapter
is a contract nobody satisfies.

Tier: W (warn).
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


class MissingAdapterGate(WiringGate):
    gate_id = "F3_missing_adapter_warn"
    tier = "W"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT
                n.adg_name,
                n.resolved_path,
                n.layer
            FROM nodes n
            WHERE n.entity_type = 'class'
              AND (
                  n.adg_name LIKE '%Protocol'
                  OR n.adg_name LIKE '%ABC'
                  OR n.adg_name LIKE '%Interface'
                  OR n.adg_name LIKE 'I_%'
                  OR n.adg_name LIKE 'Abstract%'
              )
              AND n.resolved_path IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM edges ie
                  WHERE ie.dst_id = n.id AND ie.relation_type = 'implements'
              )
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for adg_name, resolved_path, layer in tqdm(rows, desc="F3_missing_adapter", unit="cls"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{resolved_path}::{adg_name}",
                    rule="protocol_without_implementation",
                    severity="warn",
                    detail=f"{layer}: abstract class {adg_name} has 0 implementers",
                    extra={"adg_name": adg_name, "resolved_path": resolved_path, "layer": layer},
                )
            )
        return violations


def main() -> int:
    return cli_exit(MissingAdapterGate().execute())


if __name__ == "__main__":
    sys.exit(main())
