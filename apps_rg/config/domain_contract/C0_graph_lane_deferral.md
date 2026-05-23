# C0.3 graph lane deferral (apps_rg section spine)

**Status:** Deferred — core Graph RAG (C0.3) not on product section path for W4.

## Canonical NA reference

Spine dense/sparse retrieval via `c0_retrieve_apps_rg` stamps:

`ref:graph:NOT_APPLICABLE:graphrag_deferred_phase1`

Defined as `C0_GRAPH_LANE_NA_REF` in [`apps_rg/runtime/bindings/c0_binding.py`](../../runtime/bindings/c0_binding.py).

## What runs instead

| Lane | Section product path |
|------|----------------------|
| C0.2 dense/sparse | `c0_retrieve_apps_rg` when `grounding_required` |
| C0.3 graph RAG | **Skipped** — skills graph bindings in evidence room (`apps_rg_c03_skills_graph_used`) are not core Graph RAG |
| C0.5 FEC | Spine FEC from retrieve + evidence-room stratify (enabled sections) |

## STOP AS EVIDENCE GAP

When `L1PlanContract.grounding_required` is true and spine FEC `support_status` is
`WEAK`, `WEAK_WITH_CAVEATS`, `EMPTY`, `BLOCKED`, `CONFLICTED`, `UNKNOWN`, or
`NOT_APPLICABLE` without `support_target_met`, section lanes fail closed via
`StopAsEvidenceGapError` in [`section_c0_retrieve.py`](../../runtime/spine/section_c0_retrieve.py).

## Related

- Plan wave W4: [pa-exec-flowchart-gap-f2a8c3](../../../.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md)
- Gap: GAP-AR-C0-3 / GAP-SPINE-C0-SECTION
