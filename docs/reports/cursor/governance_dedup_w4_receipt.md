# W4 Receipt — governance-dedup-closeout-e8a4c2

**Wave:** W4 — Windsurf `always_on` demotion  
**Date:** 2026-05-26  
**Status:** PASS

## W4.1 — Demotion map + physical flip

| Artifact | Purpose |
|----------|---------|
| [windsurf_always_on_demotion_map_20260526.md](windsurf_always_on_demotion_map_20260526.md) | 13-rule map → `.cursor/rules/*.mdc` on-demand SSOT |
| [windsurf_always_on_demote_w4.py](../../tools/cursor/windsurf_always_on_demote_w4.py) | Demotion automation (`always_on` → `model_decision`) |

**Before:** 13 Windsurf `trigger: always_on` files, **47,493 B**  
**After:** **0** always_on files, **0 B** (reported separately from Tier-1)

## Budget gate (before / after)

```bash
python ops_scripts/ci/check_always_on_token_budget.py
```

| Surface | Before | After |
|---------|--------|-------|
| Tier-1 Cursor | 19,674 B — PASS | 19,674 B — PASS |
| Windsurf legacy always_on | 47,493 B (13 files) | **0 B (0 files)** |

## Marker

```
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=4 note="13 windsurf always_on demoted to model_decision; tier-1 unchanged PASS"
```

## Next wave

**W5** — Closeout manifest + audit link-back + Notion Completed.
