"""CI gate — Anthropic two-tier Tier-1 budget (repo-native SSOT).

Measures and enforces:
- ``.claude/rules/*.mdc`` with ``alwaysApply: true``
- ``AGENTS.md``

Reports separately (not summed into Tier-1 fail threshold):
- ``.claude/rules/*.md`` with ``trigger: always_on`` (legacy mirror)

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
    claude_always_on_total,
    scan_windsurf_always_on_md,
    tier1_cursor_total,
    write_inventory,
)

# Re-baselined always-on budget for the real Claude Code surface (root CLAUDE.md + every
# .claude/rules/*.md, which the native loader injects each session). The legacy
# THRESHOLD_BYTES (51,200) was set for the retired 4-file .mdc design and is blind to the
# real bundle; this is the enforced ceiling per plan always-on-rule-surface-cut-c7f3a1. 84 KiB.
REAL_SURFACE_THRESHOLD = 86_016


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

    # --- Real Claude Code always-on surface (plan always-on-rule-surface-cut-c7f3a1) -------
    # The native loader globs CLAUDE.md + EVERY .claude/rules/*.md into the per-session
    # bundle. The legacy Tier-1 measurement above is blind to it (no .mdc files;
    # no .md carries `trigger: always_on`). Measure + report the honest surface here.
    # ADVISORY by default to honour the coupling (an honest+enforcing gate on an
    # untrimmed 189 KB surface would self-inflict a red gate). Flip to enforcing with
    # ALWAYS_ON_CLAUDE_RULES_ENFORCE=1 once the trim brings it under threshold (W5).
    real_total, real_rows = claude_always_on_total()
    print(
        "\nclaude_code_always_on_surface (CLAUDE.md + ALL .claude/rules/*.md — the real injected bundle):"
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
            "Demote .claude/rules/*.md reference rules to pointer stubs (detail lives in "
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
