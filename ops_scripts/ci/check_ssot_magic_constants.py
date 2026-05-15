#!/usr/bin/env python3
"""Gate AUDIT-1 — SSOT magic-constants ratchet.

Detects symbols whose last-component name (e.g. ``BATCH_SIZE``,
``ExecutionContext``) is defined in **three or more distinct layers**.
These represent SSOT violations — the same identifier carrying
potentially-different meaning across architectural boundaries.

Last-component extraction must happen Python-side because SQLite lacks
``reverse()``/regex required for "last segment after final dot".

Tier R (ratchet). Baseline locks current count of cross-3-layer
identifiers; new ones regress the build.

Out of scope: identifiers with layer_count < 3 (single-layer or
two-layer dups are caught by other ratchets), test-namespace files.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from collections import defaultdict
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


def _short_name(adg_name: str) -> str:
    """Return last dot-segment of an ADG name, stripping ``ADG::Symbol::`` prefix."""
    if "::" in adg_name:
        adg_name = adg_name.rsplit("::", 1)[-1]
    return adg_name.rsplit(".", 1)[-1] if "." in adg_name else adg_name


class SsotMagicConstantsGate(WiringGate):
    gate_id = "AUDIT_1_ssot_magic_constants"
    tier = "R"
    baseline_filename = "audit_ssot_magic_constants.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, adg_name, layer, resolved_path, entity_type
            FROM nodes
            WHERE entity_type IN ('symbol', 'class', 'function', 'constant')
              AND adg_name IS NOT NULL
              AND layer IS NOT NULL AND layer != ''
              AND resolved_path NOT LIKE 'tests/%'
              AND resolved_path NOT LIKE 'archives/%'
            """
        )
        # Bucket by short_name; collect distinct (layer, file)
        by_short: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"layers": set(), "files": set()})
        for _nid, adg_name, layer, path, _et in cur.fetchall():
            sn = _short_name(adg_name)
            if not sn or len(sn) < 3 or sn.startswith("_"):
                continue
            # Skip dunder/builtin-ish
            if sn.lower() in {"main", "init", "self", "x", "n", "i"}:
                continue
            by_short[sn]["layers"].add(layer)
            by_short[sn]["files"].add(path or "")

        violations: list[Violation] = []
        for sn, agg in by_short.items():
            layers = agg["layers"]
            if len(layers) < 3:
                continue
            files = agg["files"]
            if len(files) < 3:
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=sn,
                    rule="ssot_short_name_in_3_or_more_layers",
                    detail=f"layers={sorted(layers)} files={len(files)}",
                    extra={
                        "short_name": sn,
                        "layer_count": len(layers),
                        "layers": sorted(layers),
                        "file_count": len(files),
                        "sample_files": sorted(files)[:5],
                    },
                )
            )
        return violations


def main() -> int:
    gate = SsotMagicConstantsGate()
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
