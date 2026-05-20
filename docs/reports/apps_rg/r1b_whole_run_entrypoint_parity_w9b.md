# W9b — apps_rg whole-run entrypoint R1A/R1B preflight parity

**Wave:** W9b  
**Status:** PASS  
**Date:** 2026-05-18

## Goal

Prove that every canonical apps_rg **whole-run** production/runtime entrypoint executes the same cache preflight order as the W9 CLI shim: **R1A exact → R1B semantic (`ROLE_TARGET_RUN`) → normal generation** on miss/inadmissible.

Section lanes and `orchestrate_full_resume` remain out of scope.

## SSOT module

`apps_rg/cache/whole_run_entrypoint_preflight.py` centralizes:

- `run_whole_run_cache_preflight()` — R1A then R1B (when `SEMANTIC_CACHE_D2_ENABLED`)
- `build_cache_hit_dispatch_result()` — production short-circuit dict (`generation_skipped`, `exit_bypassed: false`)
- `maybe_ingest_r1b_post_exit()` — W8 post-Exit ingest after successful pipeline runs
- `build_entrypoint_audit_matrix()` — static audit rows

## Entrypoint audit matrix

| Entrypoint | R1A | R1B | Order | Hit behavior | Miss behavior | Exit handoff | Status |
|---|---|---|---|---|---|---|---|
| `agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run` | yes | yes | R1A→R1B→gen | via canonical dispatch return | pipeline | inherited terminal packet | wired_w9b |
| `apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives` | yes | yes | R1A→R1B→gen | early return cache hit dict | `run_integrated_r4_deterministic_pipeline` | `exit_review_required` on R1B hit | wired_w9b |
| `apps_rg.runtime.dispatch.apps_rg_dispatch.apps_rg_dispatch` | yes | yes | inherited | via `dispatch_apps_rg_run` | via `dispatch_apps_rg_run` | inherited | wired_w9b |
| `apps_rg.__main__._run_with_args` | yes | yes | R1A→R1B→gen | `SystemExit(0)` | pipeline + post-Exit ingest | receipt `r1b_whole_run_preflight_hit.json` | wired_w9 |
| `apps_rg.runtime.internal.lane_batch` | no | no | gen only | N/A | offline lanes | N/A | out_of_scope |

## Wiring changes

1. **`canonical_dispatch.run_canonical_apps_rg_from_cli_primitives`** — calls `run_whole_run_cache_preflight` before `run_integrated_r4_deterministic_pipeline`; on hit returns `build_cache_hit_dispatch_result`; after successful run calls `maybe_ingest_r1b_post_exit`.
2. **`apps_rg.__main__._run_with_args`** — refactored to use the same SSOT preflight module (CLI behavior preserved).

## Proof fixtures (production entrypoint)

| Fixture | Path |
|---|---|
| Accepted hit | `artifacts/apps_rg/r1b_semantic_cache/w9b_fixtures/production_entrypoint_accepted_hit.json` |
| Miss fallthrough | `artifacts/apps_rg/r1b_semantic_cache/w9b_fixtures/production_entrypoint_miss_fallthrough.json` |
| Rejected candidate | `artifacts/apps_rg/r1b_semantic_cache/w9b_fixtures/production_entrypoint_rejected_candidate.json` |
| Audit matrix | `artifacts/apps_rg/r1b_semantic_cache/w9b_fixtures/entrypoint_audit_matrix.json` |

Emitter: `python tools/apps_rg/emit_r1b_w9b_fixtures.py`

## Proof claims

| Claim | Evidence |
|---|---|
| R1A before R1B (CLI) | `test_main_r1a_before_r1b_order` |
| R1A before R1B (production) | `test_canonical_dispatch_invokes_preflight_before_pipeline` |
| Production R1B hit skips pipeline | `test_canonical_dispatch_r1b_hit_skips_pipeline` |
| Accepted W9 fixture hit | `test_production_preflight_accepted_hit`, W9b fixture |
| W8 rejected never hit | `production_entrypoint_rejected_candidate.json` |
| Miss fallthrough | `test_production_preflight_miss_fallthrough` |
| Exit not bypassed | `exit_bypassed: false` on hit dispatch result |
| Child chunks parent-bound | W9 `child_chunk_inspection` (unchanged) |
| C0 fact_vectors not used | `c0_fact_vectors_consulted: false` |
| `agentic_core` untouched | `git diff HEAD -- agentic_core` empty |

## Non-claims

- No UWG durable persistence for R1B records.
- No section-level R1B lookup.
- No weakening of X2/X3 gates.
