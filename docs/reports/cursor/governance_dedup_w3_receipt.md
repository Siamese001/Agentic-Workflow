# W3 Receipt — governance-dedup-closeout-e8a4c2

**Wave:** W3 — Plan sprawl archive  
**Date:** 2026-05-26  
**Status:** PASS

## W3.1 — Plan inventory CSV

| Artifact | Purpose |
|----------|---------|
| [plan_sprawl_inventory_20260526.csv](plan_sprawl_inventory_20260526.csv) | Classify each top-level `.cursor/plans/*.md` as ACTIVE / ARCHIVE / KEEP |
| [plan_sprawl_w3_archive.py](../../tools/cursor/plan_sprawl_w3_archive.py) | Inventory + move script (re-runnable) |

**Before:** 87 top-level plan `.md` files  
**After:** 11 top-level (9 slug plans + README + template)

## W3.2 — Archive moves

| Destination | Count |
|-------------|-------|
| [.cursor/plans/_archive/2026-05/](../../.cursor/plans/_archive/2026-05/) | 76 plans moved |

**Remaining active top-level plans:**

- [governance-dedup-closeout-e8a4c2.md](../../.cursor/plans/governance-dedup-closeout-e8a4c2.md)
- [agent-capability-spine-harvest-e8f4a2.md](../../.cursor/plans/agent-capability-spine-harvest-e8f4a2.md)
- [agent-inventory-deferred-followup-c2a8f1.md](../../.cursor/plans/agent-inventory-deferred-followup-c2a8f1.md)
- [apps-rg-pa-w10-5-section-signal-hardening-c4f2a1.md](../../.cursor/plans/apps-rg-pa-w10-5-section-signal-hardening-c4f2a1.md)
- [exec-summary-failed-run-persistence-notion-e7c4b2.md](../../.cursor/plans/exec-summary-failed-run-persistence-notion-e7c4b2.md)
- [graph-skills-deferred-followup-d7f2a8.md](../../.cursor/plans/graph-skills-deferred-followup-d7f2a8.md)
- [phase2-gtm-presales-remaining-f7a2c9.md](../../.cursor/plans/phase2-gtm-presales-remaining-f7a2c9.md)
- [qwen3-32b-vllm-upgrade-d7a3f1.md](../../.cursor/plans/qwen3-32b-vllm-upgrade-d7a3f1.md)
- [windsurf-tree-deletion-ci-parity-b8e4f1.md](../../.cursor/plans/windsurf-tree-deletion-ci-parity-b8e4f1.md)
- [README.md](../../.cursor/plans/README.md)
- [CURSOR_RUNTIME_SEAM_TEMPLATE.md](../../.cursor/plans/CURSOR_RUNTIME_SEAM_TEMPLATE.md)

## Acceptance gate

```bash
python tools/cursor/plan_sprawl_w3_archive.py          # idempotent if already archived
python .cursor/scripts/check_cursor_optimized_config.py
```

**Result:** `active_plan_files_count`: **11** (target ≤ 20) — **PASS**

## Marker

```
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=3 note="76 plans archived to _archive/2026-05, 11 top-level remaining"
```

## Next wave

**W4** — Windsurf `always_on` demotion map + tier budget receipt.
