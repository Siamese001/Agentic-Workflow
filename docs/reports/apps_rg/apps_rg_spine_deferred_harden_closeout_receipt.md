# apps_rg spine deferred harden — closeout receipt

**Plan:** [apps-rg-spine-deferred-harden-c8f1a2](../../.cursor/plans/apps-rg-spine-deferred-harden-c8f1a2.md)  
**Parent:** [pa-exec-flowchart-gap-f2a8c3](../../.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md) (COMPLETED)  
**Date:** 2026-05-23  
**Proof classification:** HARNESS (mocked C0; receipt span coverage; not live LLM all-lanes)

## Delivered

| ID | Item | Evidence |
|----|------|----------|
| H1 | Span coverage validator + receipt | [spine_span_emit.py](../../apps_rg/runtime/spine/spine_span_emit.py) — `validate_spine_span_coverage`, `emit_spine_span_coverage_receipt` |
| H2 | U0/L1/L0 emit on front receipts | [front_contracts.py](../../apps_rg/runtime/spine/front_contracts.py) |
| H3 | C0 emit on FEC artifacts | [c0_fec_compose.py](../../apps_rg/runtime/spine/c0_fec_compose.py) |
| H4 | L6 emit + coverage at exhaust | [section_runtime_exhaust_spine_receipt.py](../../apps_rg/runtime/section_runtime_exhaust_spine_receipt.py) |
| H5 | Edge-case tests | [test_apps_rg_spine_harden_edge_cases.py](../../tests/_apps_contract/test_apps_rg_spine_harden_edge_cases.py) |
| H6 | E2E 8-layer span assert | [test_apps_rg_one_pipeline_e2e.py](../../tests/_apps_contract/test_apps_rg_one_pipeline_e2e.py) |
| H7 | W9 section contracts | [test_pa_section_contracts_w9.py](../../tests/_apps_contract/test_pa_section_contracts_w9.py) PASS |

## W4–W7 (2026-05-23)

| Wave | Deliverable |
|------|-------------|
| W4 | OTEL dual-write flags on span events; [check_apps_rg_spine_span_emit_sites.py](../../ops_scripts/ci/check_apps_rg_spine_span_emit_sites.py) |
| W5 | [c0_graph_lane_receipt.py](../../apps_rg/runtime/spine/c0_graph_lane_receipt.py) → `c0_graph_lane_receipt.json` |
| W6 | [l6_eval_before_learn_receipt.py](../../apps_rg/runtime/spine/l6_eval_before_learn_receipt.py) → `l6_eval_before_learn_receipt.json` |
| W7 | [live_section_spine_smoke_all_lanes.py](../../ops_scripts/apps_rg/live_section_spine_smoke_all_lanes.py) (BLOCKED/DRY_RUN/PASS) |

Tests: [test_apps_rg_spine_waves_w4_w7.py](../../tests/_apps_contract/test_apps_rg_spine_waves_w4_w7.py) (9) + [test_apps_rg_spine_harden_edge_cases.py](../../tests/_apps_contract/test_apps_rg_spine_harden_edge_cases.py) (29) + [test_apps_rg_one_pipeline_e2e.py](../../tests/_apps_contract/test_apps_rg_one_pipeline_e2e.py) (4) = **42/42** harness pytest (2026-05-23).

## Still deferred (honest)

- Core C0.3 Graph RAG engine (not apps_rg skills-graph binding)
- Human eval labels + promotion gauntlet execution
- Live provider run all 7 lanes without `APPS_RG_LIVE_SMOKE_DRY_RUN`

## Notion

- Page: `36927693-f55c-8137-84d6-d937ade72c87` (slug `apps-rg-spine-deferred-harden-c8f1a2`)
