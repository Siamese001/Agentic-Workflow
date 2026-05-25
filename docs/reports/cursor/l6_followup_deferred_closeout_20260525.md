# L6 Follow-Up — Deferred Scope Closeout

**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.cursor/plans/l6-reorg-deferred-followup-f3a9c2.md)  
**Receipt:** [l6_followup_deferred_closeout_20260525.json](l6_followup_deferred_closeout_20260525.json)

## 1. Fresh ADG inventory refresh

| Item | Value |
|------|-------|
| Snapshot | `artifacts/adg/adg_indexed_05252026_0751.sqlite` (latest indexed, 2026-05-25 08:02) |
| Inventory | [l6_w6_gravity_edge_inventory_fresh.json](l6_w6_gravity_edge_inventory_fresh.json) |
| YAML | [architectural_exceptions.yaml](../../config/architectural_exceptions.yaml) regenerated |
| Reconcile | PASS — 43 dedup pairs, 86 raw rows |

Scripts now auto-select latest `adg_indexed_*.sqlite` by mtime.

**Note:** M1 module deletions will reduce edge counts on the **next** ADG indexer run; current snapshot predates deletions.

## 2. ADR-086 eval consolidation

| Wave | Result |
|------|--------|
| **M1** | 12 dead B-surface modules + 7 unit tests removed |
| **M2** | Canonical owner documented: `shadow_eval/gauntlet.py`; B `promotion_gauntlet.py` compat-only |
| **M3** | Deferred — `promotion_packet`, `shadow_eval_pipeline`, etc. need API merge plan |

[ADR-086](../../architecture/adr/ADR-086-l6-eval-surface-consolidation.md) → **Accepted**.

## 3. ADR-088 Category A `_shared`

| Item | Result |
|------|--------|
| Verdict | `permanent_exception_documented` |
| ADR | [ADR-088](../../architecture/adr/ADR-088-l6-category-a-shared-permanent-exception.md) |
| Scaffold | [agentic_core/_shared/types/README.md](../../agentic_core/_shared/types/README.md) |

Physical extraction remains a **future plan** (`l6-shared-types-split-*`).

## Proof

- `python tools/_oneoff/l6_followup_e2e_closeout_verify.py` → 24/24 PASS
- `pytest` shadow_eval + promotion_gauntlet → 310 passed
