# P0 Last-Mile Hardening — Wave 01 Report

**Date**: 2026-03-15
**ADG Before**: `adg_indexed_03152026_2154.sqlite`
**ADG After**: `adg_indexed_03152026_2203.sqlite`

## Modules Changed (8)

| Module | Layer | Dims Targeted | Dims Added |
|---|---|---:|---|
| `tests/guardian/conftest.py` | test | 7 | all 7 P0 |
| `tests/sovereign_hardening/conftest.py` | test | 7 | all 7 P0 |
| `tests/unit_min_deps/conftest.py` | test | 7 | all 7 P0 |
| `agentic_core/L0_routing/config/ssot_tier_constants.py` | L0 | 6 | records, applies, signs, snapshots, replay, digest |
| `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | L5 | 6 | records, applies, signs, snapshots, replay, digest |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | L5 | 6 | records, applies, signs, snapshots, replay, digest |
| `agentic_core/runtime/lifecycle_trace_contract.py` | runtime | 2 | applies_guardrail, snapshots_state |
| `agentic_core/L0_routing/config/path_constants.py` | L0 | 2 | emits_replay_key, emits_determinism_digest |

## Before/After Module Counts

| Dimension | Before | After | Gain | Status |
|---|---:|---:|---:|---|
| `records_execution_trace` | 3,005 | 3,011 | +6 | 100.0% |
| `applies_guardrail` | 3,004 | 3,011 | +7 | 100.0% |
| `reads_policy_state` | 3,008 | 3,011 | +3 | 100.0% |
| `emits_replay_key` | 3,004 | 3,011 | +7 | 100.0% |
| `emits_determinism_digest` | 3,004 | 3,011 | +7 | 100.0% |
| `signs_execution_trace` | 3,005 | 3,011 | +6 | 100.0% |
| `snapshots_state` | 3,004 | 3,011 | +7 | 100.0% |

## Remaining Uncovered Modules

**ZERO** — all 7 dimensions at 3,011/3,011.

## Regression Check

- 19/19 scanner contract tests pass
- No previously-covered modules lost coverage
- ADG drift: +186 edges, -18 edges (net +168)
- Total edges: 323,009 (from 6,293 modules)

## Determinism Validation

- No duplicate replay_key or digest emission detected
- No non-UWG writes introduced
- Trace signing binds to emitted traces (unchanged)
- Policy reads precede guardrail application (call order preserved)
- Snapshot calls bound to stateful modules only
