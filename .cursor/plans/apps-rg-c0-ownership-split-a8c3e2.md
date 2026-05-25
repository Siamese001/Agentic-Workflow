---
name: apps-rg-c0-ownership-split
status: completed
completed_at: 2026-05-22
scope_doc: docs/reports/apps_rg/apps_rg_c0_ownership_split_scope.md
receipt: docs/reports/apps_rg/apps_rg_c0_ownership_split_closeout_receipt.md
---

# apps_rg C0 ownership split

**Status:** Completed

See [apps_rg_c0_ownership_split_scope.md](../../docs/reports/apps_rg/apps_rg_c0_ownership_split_scope.md) for full scope and [apps_rg_c0_ownership_split_closeout_receipt.md](../../docs/reports/apps_rg/apps_rg_c0_ownership_split_closeout_receipt.md) for proof.
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
