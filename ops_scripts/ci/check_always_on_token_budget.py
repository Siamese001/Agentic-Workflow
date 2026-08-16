"""CI gate — Codex always-on instruction budget.

Measures and enforces the retired Tier-1 compatibility surface:
- historical ``.codex/rules/*.mdc`` files with ``alwaysApply: true`` if any remain
- ``AGENTS.md``

Reports separately (not summed into Tier-1 fail threshold):
- ``.codex/rules/*.md`` with ``trigger: always_on`` (legacy mirror)

The default check is read-only. Pass ``--write-inventory`` only when an operator
explicitly wants to refresh ``docs/reports/cursor/governance_tier_inventory.json``.

Threshold: 51,200 bytes (~12,800 tokens). Bypass: ``ALWAYS_ON_BUDGET_BYPASS=1``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from governance_tier_measurement import (
    THRESHOLD_BYTES,
    claude_always_on_total,
    scan_windsurf_always_on_md,
    tier1_cursor_total,
    write_inventory,
)

# Re-baselined always-on budget for the real Claude Code surface (root AGENTS.md + every
# .codex/rules/*.md, which the native loader injects each session). The historical
# THRESHOLD_BYTES (51,200) was set for the retired 4-file .mdc design and is blind to the
# real bundle; this is the enforced ceiling per plan always-on-rule-surface-cut-c7f3a1. 84 KiB.
REAL_SURFACE_THRESHOLD = 86_016


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-inventory",
        action="store_true",
        help="Refresh the versioned governance inventory instead of running read-only.",
    )
    parser.add_argument(
        "--inventory-wave",
        default=os.environ.get("GOVERNANCE_INVENTORY_WAVE", "W0"),
        help="Wave label written only with --write-inventory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if os.environ.get("ALWAYS_ON_BUDGET_BYPASS") == "1":
        print(
            "[always-on-budget] BYPASS via ALWAYS_ON_BUDGET_BYPASS=1",
            file=sys.stderr,
        )
        return 0

    tier1_total, tier1_rows = tier1_cursor_total()
    windsurf_rows = scan_windsurf_always_on_md()
    windsurf_total = sum(r.bytes for r in windsurf_rows)

    if args.write_inventory:
        inventory_path = write_inventory(wave=args.inventory_wave)
        print(f"[always-on-budget] inventory refreshed: {inventory_path}")
    else:
        print("[always-on-budget] inventory not written (pass --write-inventory to refresh it)")

    print("tier_1_legacy_compat (historical alwaysApply .mdc + AGENTS.md):")
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

    # --- Real Claude Code always-on surface (plan always-on-rule-surface-cut-c7f3a1) -------
    # The native loader globs AGENTS.md + EVERY .codex/rules/*.md into the per-session
    # bundle. The retired Tier-1 measurement above is blind to it (no .mdc files;
    # no .md carries `trigger: always_on`). Measure + report the honest surface here.
    # ADVISORY by default to honour the coupling (an honest+enforcing gate on an
    # untrimmed 189 KB surface would self-inflict a red gate). Flip to enforcing with
    # ALWAYS_ON_CLAUDE_RULES_ENFORCE=1 once the trim brings it under threshold (W5).
    real_total, real_rows = claude_always_on_total()
    print(
        "\nclaude_code_always_on_surface (AGENTS.md + ALL .codex/rules/*.md — the real injected bundle):"
    )
    print(f"  files: {len(real_rows)}")
    print(
        f"  CLAUDE_RULES_REAL_TOTAL: {real_total:,} bytes (~{real_total // 4:,} tokens)"
    )
    print(
        f"  Re-baselined threshold: {REAL_SURFACE_THRESHOLD:,} bytes "
        f"(~{REAL_SURFACE_THRESHOLD // 4:,} tokens)"
    )
    if real_total > REAL_SURFACE_THRESHOLD:
        delta = real_total - REAL_SURFACE_THRESHOLD
        pct = delta / REAL_SURFACE_THRESHOLD * 100
        print(
            f"\n[always-on-budget] FAIL: real always-on surface {delta:,} bytes over "
            f"the re-baselined ceiling ({pct:.1f}% over)",
            file=sys.stderr,
        )
        print(
            "Demote .codex/rules/*.md reference rules to pointer stubs (detail lives in "
            "skills; enforcement in hooks/CI); compress the floor.",
            file=sys.stderr,
        )
        print("Bypass: ALWAYS_ON_BUDGET_BYPASS=1", file=sys.stderr)
        return 1
    print(
        f"\n[always-on-budget] PASS real surface "
        f"({REAL_SURFACE_THRESHOLD - real_total:,} bytes headroom under the re-baselined ceiling)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
