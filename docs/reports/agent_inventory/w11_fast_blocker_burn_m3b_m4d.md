# W11 fast blocker burn — M3B, M4B, M4C, M4D

**Generated:** 2026-05-19  
**Wave:** W11-M3B / M4B / M4C / M4D  
**Status:** PARTIAL (120/122 targeted tests pass; 2 competencies contract assertions fail on stub lane output)

## Receipt

```
STATUS: PARTIAL
FILES_CHANGED:
- [narrative_judge_scorer.py](../../apps_eval/engines/narrative_judge_scorer.py)
- [rg_integrations_facade.py](../../apps_shared/adapters/rg_integrations_facade.py)
- [competencies_lane.py](../../apps_rg/runtime/sections/competencies_lane.py)
- [competencies_lane_execution.py](../../apps_rg/runtime/sections/competencies_lane_execution.py)
- [sections/*_pa.py](../../apps_rg/runtime/sections/) (7 PA modules + M4A helpers)
- [dispatch/*_pa.py](../../apps_rg/runtime/dispatch/) (compat re-exports)
- Lane imports: executive_summary, headline, ibm_bullets, unify_bullets, unify_narrative
- [test_w3_boundary_facades.py](../../tests/unit/apps_shared/adapters/test_w3_boundary_facades.py)
- [test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py)
- [apps_rg/integrations/](../../apps_rg/integrations/) (restored minimal SSOT for eval facade)
COMMANDS_RUN:
- git status --short -> large unrelated plan deletions in working tree; wave scope listed above
- python -m compileall agentic_core apps_rg apps_shared apps_eval -q -> exit 0
- git grep (Rg*/dispatch) -> apps_eval has zero direct apps_rg imports; lanes use sections PA
- _w11_fanin_scan.py / _w11_adg_expand.py / _w11_remaining_candidates_prep.py -> exit 0
TESTS_RUN:
- test_w3_boundary_facades.py -> 18 passed
- test_lane_pa_helper_parity.py -> 10 passed
- test_rg_* (5 modules) -> 42 passed
- test_apps_rg_deprecated_path_quarantine + canonical_runtime_hygiene + exit_uwg -> 42 passed
- test_competencies_canonical_lane_contract.py -> 8 passed, 2 failed (x2 cardinality 42≠41; X3_BLOCK≠MOCK_REVIEW)
ARTIFACTS_WRITTEN:
- [w11_fast_blocker_burn_m3b_m4d.md](w11_fast_blocker_burn_m3b_m4d.md)
- [w11_fast_blocker_burn_m3b_m4d.json](w11_fast_blocker_burn_m3b_m4d.json)
- Updated [w11_lane_dispatch_pa_map.md](w11_lane_dispatch_pa_map.md)
- Regenerated [w11_candidate_fanin_matrix.json](w11_candidate_fanin_matrix.json)
- Updated [w11_gated_archive_delete_plan.md](w11_gated_archive_delete_plan.md)
- Updated [w11_migration_checklist.md](w11_migration_checklist.md)
- Updated [l2-rationalization-waves-c8e4f1.md](../../.cursor/plans/l2-rationalization-waves-c8e4f1.md)
```

## M3B_RG_BOUNDARY

**migrated:**
- `apps_eval/engines/narrative_judge_scorer.py` → `apps_shared.adapters.rg_integrations_facade` (anti-overfitting, length budget, judge client)
- New facade: [rg_integrations_facade.py](../../apps_shared/adapters/rg_integrations_facade.py)
- Minimal `apps_rg/integrations/` restored (`anti_overfitting`, `length_budget`, `hops/_llm_client`) for lazy facade resolution
- W3 contract: `test_apps_eval_has_no_direct_apps_rg_imports` passes

**retained:**
- `apps_eval/engines/scenario_runner.py` → `RgResumeOrchestrator` via `rg_orchestrator_facade` (eval parity)
- `apps_eval/config/agent_spec_config.py` string target `apps_rg.reasoning.RgResumeOrchestrator` (spec only)
- Unit tests under `tests/unit/apps_rg/reasoning/` (legacy Rg* coverage intact)

**blockers:**
- Full Rg* retirement blocked by facades + eval scenario_runner + contract smoke strings
- `apps_rg/reasoning/*` remains **QUARANTINE_30D** — not archive-ready

## M4B_PA_EXTRACTION

**helpers_extracted:** (SSOT → `apps_rg/runtime/sections/`)
- `compile_headline_prompt` — headline_pa
- `compile_competencies_prompt` — competencies_pa
- `compile_ibm_bullets_prompt` — ibm_bullets_pa
- `compile_ibm_narrative_prompt` — ibm_narrative_pa
- `compile_unify_bullets_prompt` — unify_bullets_pa
- `compile_unify_narrative_prompt` — unify_narrative_pa
- `compile_executive_summary_prompt` — executive_summary_pa
- (M4A carryover) `attach_reasoning_to_prompt_trace`, `collect_employment_bullets`

**reexports_kept:** `apps_rg/runtime/dispatch/*_pa.py` thin re-exports (symbol identity preserved)

**parity_tests:** [test_lane_pa_helper_parity.py](../../tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) — 7 `compile_*` pairs + trace/bullets + lane execution surface

**blockers:**
- `competencies_dispatch`, `ibm_narrative_dispatch`, dispatch CLIs still hold full runtime execution (~1.5k+ lines)
- `exec_summary_graph_projection_w4b.py` still imports dispatch PA path (compat re-export OK)
- `ibm_narrative_dispatch` still imports `collect_employment_bullets` from dispatch package

## M4C_COMPETENCIES_SPLIT

**changed:**
- [competencies_lane_execution.py](../../apps_rg/runtime/sections/competencies_lane_execution.py) — canonical execution entry; default `trace_runtime_path=apps_rg.runtime.sections.competencies_lane`
- [competencies_lane.py](../../apps_rg/runtime/sections/competencies_lane.py) — delegates to execution module (no direct `competencies_dispatch` import)

**retained_compat:**
- `run_competencies_execution` body remains in [competencies_dispatch.py](../../apps_rg/runtime/sections/competencies_lane_api.py)
- Deprecated `python -m apps_rg.runtime.sections.competencies_lane_api` path unchanged

**tests:**
- `test_canonical_lane_records_trace_runtime_path` — **PASS**
- `test_competencies_lane_execution_import_surface` — **PASS**
- `test_canonical_lane_x2_gate_cardinality` / `test_canonical_lane_mock_judge_x3_review_code` — **FAIL** (stub lane produced 42 X2 gates with `x2_no_keyword_stuffing` fail → `X3_BLOCK`; not recursion; investigate fixture/stub baseline separately)

**blockers:**
- Full move of `run_competencies_execution` (~665+ lines + helpers) deferred — high coupling; M4C achieved import-surface split only

## M4D_FANIN_UPDATE

**fanin_before:** (post-M3A/M4A) `archived=1`, `delete_ready=0`, `archive_ready=0`, `migration_required=8`, `blocked=11`

**fanin_after:** `archived=1`, `delete_ready=0`, `archive_ready=0`, `migration_required=8`, `blocked=12` (matrix script; static grep refs on dispatch paths unchanged)

**archive_ready_candidates:** **0** (none meet DELETE_GATE + 30d quarantine)

**next_single_archive_target:** `agentic_core/L2_execution/reasoning/validation_orchestrator.py` — **ARCHIVE_CANDIDATE_AFTER_30D** (ADG import fan-in 0; CI baselines + quarantine clock remain blockers)

## UPDATED_COUNTS

| Metric | Count |
|--------|------:|
| archived | 1 |
| delete_ready | 0 |
| archive_ready | 0 |
| migration_required | 8 |
| blocked | 12 |

## BEHAVIOR_CHANGE

**RUNTIME_CHANGE:** No intentional product runtime behavior change. PA compile symbols re-homed with identical objects via dispatch re-exports. Competencies lane default trace path now `apps_rg.runtime.sections.competencies_lane` when invoked through canonical entry.

**NEXT_RECOMMENDED_ACTION:** W11-M5 or M3.5 — migrate remaining `apps_shared` / contract string refs off `Rg*`; then M4.7 extract `ibm_narrative_dispatch` / shrink `competencies_dispatch` execution body. Re-baseline competencies contract tests if stub X2 gate cardinality is intentionally 42.

## EXPLICIT_NON_CLAIMS

- no files deleted
- no archive moves
- no product runtime behavior changed (by design)
- no X2/X3 weakened
- no live apps_rg proof
