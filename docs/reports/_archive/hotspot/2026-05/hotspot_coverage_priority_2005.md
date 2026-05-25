# Hotspot × Coverage Priority — Report

**Snapshot**: `artifacts\adg\adg_indexed_05242026_2005.sqlite`  
**Commit SHA**: `ee3001638c8894973b45414ba0071c02485a5f3b`  
**Total nodes scored**: 4291

## Coverage data presence

- **Measured**: 0 (have `coverage_pct` from `coverage.py`)
- **Absent**: 4291 (no coverage data ingested)
- **Average measured coverage**: —

> ⚠️ **No coverage data was ingested into this snapshot.** Every row's `coverage_band` is `ABSENT`, so all high-risk modules land in `P1_URGENT` regardless of actual test coverage. To get meaningful priority bands, run pytest with `--cov` first, then regenerate ADG.

## Priority distribution

| Band | Count | Meaning |
|---|---:|---|
| `P1_URGENT` | 1644 | High risk + ABSENT/MINIMAL coverage — urgent test gap |
| `P4_LOW` | 813 | Medium risk — review during routine refactoring |
| `P5_NOOP` | 1834 | Low or zero risk — probably acceptable as-is |

## Risk × Coverage matrix

| Risk \ Coverage | FULL | GOOD | PARTIAL | MINIMAL | ABSENT |
|---|---:|---:|---:|---:|---:|
| **CRITICAL** | 0 | 0 | 0 | 0 | 467 |
| **HIGH** | 0 | 0 | 0 | 0 | 1177 |
| **MEDIUM** | 0 | 0 | 0 | 0 | 813 |
| **LOW** | 0 | 0 | 0 | 0 | 1834 |

## Per-layer breakdown

| Layer | P1 | P2 | P3 | P4 | P5 | Total |
|---|---:|---:|---:|---:|---:|---:|
| `L_APP` | 322 | 0 | 0 | 275 | 652 | 1249 |
| `L5` | 317 | 0 | 0 | 73 | 143 | 533 |
| `L2` | 147 | 0 | 0 | 35 | 87 | 269 |
| `L_SL` | 138 | 0 | 0 | 30 | 128 | 296 |
| `L_SHARED` | 124 | 0 | 0 | 28 | 112 | 264 |
| `L_TOOLS` | 96 | 0 | 0 | 22 | 37 | 155 |
| `L3` | 90 | 0 | 0 | 50 | 84 | 224 |
| `L1` | 84 | 0 | 0 | 41 | 58 | 183 |
| `L4` | 80 | 0 | 0 | 41 | 45 | 166 |
| `L_RUNTIME` | 78 | 0 | 0 | 46 | 164 | 288 |
| `L0` | 56 | 0 | 0 | 53 | 66 | 175 |
| `L6` | 48 | 0 | 0 | 38 | 32 | 118 |
| `L_PG` | 35 | 0 | 0 | 23 | 106 | 164 |
| `L_UNKNOWN` | 25 | 0 | 0 | 47 | 117 | 189 |
| `L_INFRA` | 4 | 0 | 0 | 11 | 3 | 18 |

## Top 15 P1_URGENT (high risk, no coverage)

| Rank | File | Layer | Crit | Fan-in | Fan-out | Violations | Cov % | Mocks |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `agentic_core/L5_safety/contracts/registry.py` | `L5` | 810.0 | 0 | 810 | 0 | — | 0 |
| 2 | `apps_rg/runtime/sections/executive_summary_lane.py` | `L_APP` | 232.0 | 0 | 148 | 28 | — | 0 |
| 3 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | `L5` | 217.0 | 0 | 157 | 20 | — | 0 |
| 4 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | `L5` | 199.0 | 0 | 127 | 24 | — | 0 |
| 5 | `agentic_core/L5_safety/utils/location_healer_util.py` | `L5` | 193.0 | 0 | 142 | 17 | — | 0 |
| 6 | `agentic_core/adg/extraction/static_scanner.py` | `L_TOOLS` | 188.0 | 0 | 158 | 10 | — | 0 |
| 7 | `agentic_core/L6_observability/shadow_eval/__init__.py` | `L6` | 161.0 | 0 | 161 | 0 | — | 0 |
| 8 | `apps_rg/runtime/sections/unify_bullets_lane.py` | `L_APP` | 151.0 | 0 | 70 | 27 | — | 0 |
| 9 | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` | `L5` | 144.0 | 0 | 108 | 12 | — | 0 |
| 10 | `agentic_core/L0_routing/c0_retrieval/__init__.py` | `L0` | 143.0 | 0 | 143 | 0 | — | 0 |
| 11 | `agentic_core/L5_safety/utils/cst_transformers_types_util.py` | `L5` | 143.0 | 0 | 143 | 0 | — | 0 |
| 12 | `agentic_core/L5_safety/reasoning/location_validator.py` | `L5` | 141.0 | 0 | 126 | 5 | — | 0 |
| 13 | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | `L5` | 140.0 | 0 | 116 | 8 | — | 0 |
| 14 | `apps_rg/runtime/sections/ibm_bullets_lane.py` | `L_APP` | 140.0 | 0 | 68 | 24 | — | 0 |
| 15 | `apps_eval/engines/scenario_runner.py` | `L_APP` | 139.0 | 0 | 118 | 7 | — | 0 |

## How to read

- **Risk** is derived from `mv_path_criticality_rollup.criticality_score`
  (fan_in × fan_out × violation_count × cross_layer_edges) banded by P50/P75/P95 percentile within this snapshot.
- **Coverage** is the line-coverage % from `coverage.py` (intersected with executable-line AST set, capped at 100%).
- **Priority** is `risk × coverage_weakness` — see top of this report.
- **Mocks** is the number of `unittest.mock` instantiations in any test file targeting this module. High mock count means the existing tests may not exercise the real code path.

Source MV: `mv_hotspot_coverage_risk` (Phase F).
