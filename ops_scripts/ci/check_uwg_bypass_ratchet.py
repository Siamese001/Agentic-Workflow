#!/usr/bin/env python3
"""Gate S2 — UWG-bypass ratchet (plan W4.2).

Counts `writes_to` edges where the source module is NOT on the
UWG-approved writer allowlist. Constitutional Rule §22/ADG-surfaces
"Write" requires state mutations to flow through the Unified Write
Gateway (`write_gateway.py`) or its sanctioned proxies.

Tier: R (ratchet).

The allowlist captures today's approved write sources. Any new source
module performing `writes_to` above the baseline must either (a) route
through UWG, or (b) be explicitly added to the allowlist with an ADR
justifying the exception.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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

# Modules explicitly permitted to perform writes_to without UWG proxy.
# Extend via ADR — do not edit casually.
UWG_APPROVED_WRITERS = frozenset(
    {
        "agentic_core/L2_execution/utils/write_gateway.py",
        "agentic_core/L4_state/enforcement/promotion_write_gateway.py",
        "agentic_core/L5_safety/validators/static_checks/write_gateway_enforcer.py",
        "agentic_core/interfaces/write_gateway.py",
        "agentic_core/interfaces/write_gateway_shim.py",
    }
)

EXCLUDE_LAYERS = ("L_TEST", "L_TOOLS", "L_UNKNOWN")
EXCLUDE_PREFIXES = ("apps_eval_legacy/original_tree/",)


class UwgBypassRatchetGate(WiringGate):
    gate_id = "S2_uwg_bypass_ratchet"
    tier = "R"
    baseline_filename = "wiring_uwg_bypass_ratchet.json"

    def run(self, conn) -> list[Violation]:
        rows = conn.execute(
            """
            SELECT e.source_file, e.line_no, src.resolved_path, src.layer, e.symbol
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'writes_to'
              AND src.resolved_path IS NOT NULL
            """
        ).fetchall()

        violations: list[Violation] = []
        for source_file, line_no, src_path, layer, symbol in rows:
            if layer in EXCLUDE_LAYERS:
                continue
            if src_path.startswith(EXCLUDE_PREFIXES):
                continue
            if src_path in UWG_APPROVED_WRITERS:
                continue
            loc = f"{source_file}:{line_no}" if source_file else f"{src_path}:?"
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=loc,
                    rule="write_outside_uwg",
                    detail=f"layer={layer}; symbol={symbol}; module={src_path}",
                    extra={"layer": layer, "module": src_path, "symbol": symbol},
                )
            )
        return violations


def main() -> int:
    gate = UwgBypassRatchetGate()
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
