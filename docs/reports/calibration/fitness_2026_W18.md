# Runtime Coverage Fitness Report

- **Generated:** 2026-04-29 01:02:10 UTC
- **Lookback:** 7 days
- **Declared REQs:** 6
- **Overall:** FAIL

## Fitness Functions

| Function | Target | Observed | Verdict |
|---|---|---|:---:|
| behavioral_coverage_per_app | ≥ 0.85 | min=1.0 | ✅ |
| layer_emission_breadth | ≥ 7 | 3 | ❌ |
| static_runtime_coverage | ≥ 0.7 | 0.0 | ❌ |
| req_freshness_p50_days | ≤ 7.0 | 0.0 (p90=0.0) | ✅ |
| orphan_ingest_count | == 0 | 200 | ❌ |

## Behavioral Coverage by App

| App | Coverage |
|---|---:|
| `apps_rg` | 100.0% |

## Missing Layers

Layers with **zero** runtime exemplars in the freshness window:

- `C0_RETRIEVAL_PLAN`
- `L1_REASONING`
- `L2_EXECUTION`
- `L3_ORCHESTRATION`
- `L5_POLICY`
- `PA_BOM_RESOLUTION`
- `U0_INPUT`
