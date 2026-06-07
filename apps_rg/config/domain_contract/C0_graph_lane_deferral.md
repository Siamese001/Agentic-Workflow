# C0.3 graph lane — apps_rg section spine (W10-AG unified bind)

**Status:** **LIVE** on grounded routes when `graph_traverse` policy is active (`live_wiring_deferred: false`).

## Canonical references

| State | FEC `graph_expansion_refs` |
|-------|---------------------------|
| Deferred (no policy / file-only) | `ref:graph:NOT_APPLICABLE:graphrag_deferred_phase1` (`C0_GRAPH_LANE_NA_REF`) |
| Unified spine (W10-AG) | `ref:graph:node:*`, `ref:graph:traverse:*`, or arsenal lineage refs from `augmented_skills_graph` |

Defined in [`apps_rg/runtime/bindings/c0_binding.py`](../../runtime/bindings/c0_binding.py).

## One pipeline (product path)

| Stage | Binding |
|-------|---------|
| L0 route | [`route_profiles.yaml`](route_profiles.yaml) → `GraphTraversePolicy` via [`l0_binding.py`](../../runtime/bindings/l0_binding.py) |
| C0.2 dense/sparse | `c0_retrieve_apps_rg` (apps_rg `grounding_required` always true on product lanes) |
| C0.3 graph | Core `maybe_run_graph_rag` → `run_graph_traverse` + [`apps_rg/integrations/c0_graph_adapter.py`](../../integrations/c0_graph_adapter.py) |
| C0.5 FEC | Spine FEC with non-NA `graph_expansion_refs` |
| Proof pool | Section lanes consume spine FEC / `c03_graphrag_bound` aligned to spine output |

## STOP AS EVIDENCE GAP

When spine FEC `support_status` is weak or
`NOT_APPLICABLE` without `support_target_met`, section lanes fail closed via
`StopAsEvidenceGapError` in [`section_c0_retrieve.py`](../../runtime/spine/section_c0_retrieve.py).

## Related

- Plan: [graph-skills-quality-enhancement-c4e8a1](../../../.claude/plans/graph-skills-quality-enhancement-c4e8a1.md) wave W10-AG
- Receipt: [graph_skills_quality_w10_ag_receipt.json](../../../docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json)
