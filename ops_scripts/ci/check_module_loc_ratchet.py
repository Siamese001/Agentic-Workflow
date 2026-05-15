#!/usr/bin/env python3
"""Gate M1 — module LOC ratchet (plan W3.3).

Counts production .py files whose non-blank line count exceeds MAX_LOC.
Reads files from disk (ADG span_end_line is not populated in current
snapshots, so disk read is authoritative and cheap).

Tier: R (ratchet).

MAX_LOC = 500. Thoughtworks fitness-function guidance puts the signal-
to-noise inflection around 400-600 LOC per file before cognitive load
and merge-conflict risk rise sharply.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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

_REPO_ROOT = Path(__file__).resolve().parents[2]

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
    "archives/",
)
MAX_LOC = 500


class ModuleLocRatchetGate(WiringGate):
    gate_id = "M1_module_loc_ratchet"
    tier = "R"
    baseline_filename = "wiring_module_loc_ratchet.json"

    def run(self, conn) -> list[Violation]:
        # Use ADG to get the layer per module (avoids re-layering on disk).
        layer_by_path: dict[str, str] = {
            row[0]: row[1]
            for row in conn.execute(
                """
                SELECT resolved_path, layer
                FROM nodes
                WHERE entity_type='module'
                  AND resolved_path IS NOT NULL
                """
            )
        }

        violations: list[Violation] = []
        for py in _REPO_ROOT.rglob("*.py"):
            rel = py.relative_to(_REPO_ROOT).as_posix()
            if not rel.startswith(PRODUCTION_ROOTS):
                continue
            if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            try:
                loc = _count_non_blank_lines(py)
            except OSError:
                continue
            if loc <= MAX_LOC:
                continue
            layer = layer_by_path.get(rel, "UNKNOWN")
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=rel,
                    rule="module_exceeds_loc_ceiling",
                    detail=f"layer={layer}; non_blank_loc={loc} > {MAX_LOC}",
                    extra={"loc": loc, "layer": layer, "ceiling": MAX_LOC},
                )
            )
        return violations


def _count_non_blank_lines(path: Path) -> int:
    n = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def main() -> int:
    gate = ModuleLocRatchetGate()
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
