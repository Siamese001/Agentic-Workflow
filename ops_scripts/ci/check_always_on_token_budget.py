"""CI gate — Anthropic two-tier Tier-1 budget (Cursor-native SSOT).

Measures and enforces:
- ``.cursor/rules/*.mdc`` with ``alwaysApply: true``
- ``AGENTS.md``

Reports separately (not summed into Tier-1 fail threshold):
- ``.cursor/rules/*.md`` with ``trigger: always_on`` (legacy mirror)

Writes: ``docs/reports/cursor/governance_tier_inventory.json``

Threshold: 51,200 bytes (~12,800 tokens). Bypass: ``ALWAYS_ON_BUDGET_BYPASS=1``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from governance_tier_measurement import (
    THRESHOLD_BYTES,
    build_inventory,
    scan_windsurf_always_on_md,
    tier1_cursor_total,
    write_inventory,
)


def main() -> int:
    if os.environ.get("ALWAYS_ON_BUDGET_BYPASS") == "1":
        print(
            "[always-on-budget] BYPASS via ALWAYS_ON_BUDGET_BYPASS=1",
            file=sys.stderr,
        )
        return 0

    tier1_total, tier1_rows = tier1_cursor_total()
    windsurf_rows = scan_windsurf_always_on_md()
    windsurf_total = sum(r.bytes for r in windsurf_rows)

    inventory_path = write_inventory(wave=os.environ.get("GOVERNANCE_INVENTORY_WAVE", "W0"))
    print(f"[always-on-budget] inventory: {inventory_path}")

    print("tier_1_cursor_native (alwaysApply .mdc + AGENTS.md):")
    for row in tier1_rows:
        print(f"  {row.bytes:>6}  {row.rel_path}")
    print(
        f"\nTIER_1_TOTAL: {tier1_total:,} bytes (~{tier1_total // 4:,} tokens)"
    )
    print(f"Threshold: {THRESHOLD_BYTES:,} bytes ({THRESHOLD_BYTES // 4:,} tokens)")

    print("\nwindsurf_legacy_always_on (reported separately, not in Tier-1 sum):")
    print(f"  files: {len(windsurf_rows)}")
    for row in windsurf_rows:
        print(f"  {row.bytes:>6}  {row.rel_path}")
    print(f"  WINDSURF_ALWAYS_ON_TOTAL: {windsurf_total:,} bytes (~{windsurf_total // 4:,} tokens)")

    if tier1_total > THRESHOLD_BYTES:
        delta = tier1_total - THRESHOLD_BYTES
        pct = delta / THRESHOLD_BYTES * 100
        print(
            f"\n[always-on-budget] FAIL: Tier-1 {delta:,} bytes over ({pct:.1f}% over)",
            file=sys.stderr,
        )
        print(
            "Demote alwaysApply rules or compress AGENTS.md; move prose to skills.",
            file=sys.stderr,
        )
        print("Bypass: ALWAYS_ON_BUDGET_BYPASS=1", file=sys.stderr)
        return 1

    print(
        f"\n[always-on-budget] PASS Tier-1 ({THRESHOLD_BYTES - tier1_total:,} bytes headroom)"
    )
    if windsurf_total > THRESHOLD_BYTES:
        print(
            f"[always-on-budget] WARN: windsurf legacy always_on alone is "
            f"{windsurf_total:,} bytes (mirror; W1 will demote per Option A)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
