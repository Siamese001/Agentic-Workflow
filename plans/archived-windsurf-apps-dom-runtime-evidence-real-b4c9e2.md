---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-dom-runtime-evidence-real-b4c9e2.md'
original_relative_path: 'apps-dom-runtime-evidence-real-b4c9e2.md'
source_sha256: fcc52bdb9b23f0db103ea58fa1b1d1cb0762c84962536a61010719524f676f01
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# APPS-DOM Runtime Evidence · Real Closure

**Slug:** `apps-dom-runtime-evidence-real-b4c9e2`
**Status:** Completed (2026-05-03)
**Parent:** `apps-runtime-domain-enforcement-a7e9d4` (completed) + `apps-dom-runtime-harness-followup-f2a7b3` (completed)
**Author-Gate link:** `dec_19dedd3f565173b7f` (heuristic_split precedent)

## AI Summary

The parent plan landed 45/45 SIGNED_OFF with `trust_level=INTEGRITY_PROOF`, but three fixture
fields were documented as synthesized: pass-path `dim_scores`, `route_contract` replay hashes,
and `AppSpecificEvaluator` returned `passed=False` (empty `AppDomainStore` at CI time). This
plan closes all three gaps + a fourth (pipeline's own `exit.app_specific_eval` emit path)
without weakening certification. After W4 completes, the harness produces **fully real** OTEL
evidence where every byte in the fixture is a deterministic function of committed on-disk
artifacts + the real Exit pipeline; the pipeline's own emit path replaces post-hoc enrichment.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1 | Patch `normalize_to_packet` to populate `packet.app_id/task_class/rubric_ref/threshold_profile_ref` from receipts | ~5k | receipts carry these fields top-level or under `route_contract`; packet defaults to `""` preserved | Draft | Pipeline emits `exit.app_specific_eval` span on its own when receipts bind; existing 976 tests pass |
| W2 | W2.P1 | Build `tools/cert/apps_e2e/_harness_store_loader.py` — reads app YAMLs into `InMemoryAppDomainStore` | ~12k | Records are frozen dataclasses; `put_eval_rubric` / `put_threshold_profile` / `put_grader_roster` accept instances; `score_dimensions` already covered by `ScoreDimension` shape | Draft | Loader constructs all 8 apps' records without raising; `evaluator.evaluate(...)` returns `bound=True AND fail_reasons=[]` for a pass-path run_context |
| W3 | W3.P1 | Harness invokes `map_l2_receipt_to_dim_scores` when the app has a `rubric_output_map.yaml` | ~8k | Mapper is fail-soft; missing YAML → skip and fall back to prior scoring; scoring with mapper output is deterministic | Draft | dim_scores come from mapper where YAML exists; harness fixtures show `"dim_scores_source": "mapper"` when applicable |
| W4 | W4.P1 | Real SHA256-bound `policy_hash` / `blueprint_hash` / `prompt_hash` from on-disk artifacts + verify compiler + final report | ~5k | Every app has `config/cert_route_registry.yaml` + `config/domain_contract/eval_rubrics.yaml`; prompt artifact optional | Draft | All harness fixtures carry `sha256://<16hex>` hashes; compiler re-run: 45/45 SIGNED_OFF, `trust_level=INTEGRITY_PROOF`; 976 tests pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Preflight packet binding | `agentic_core/L3_orchestration/exit_eval/v6/preflight.py` (modify ~10 LOC in `normalize_to_packet`) + 1 new test in `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_pipeline.py` | Additive only; must not change behavior when fields are absent (backward compat). Fields live at top-level OR under `route_contract`. | ~5k | Draft |
| W2.P1 | Harness store loader | `tools/cert/apps_e2e/_harness_store_loader.py` (new, ~120 LOC) | Each YAML's `score_dimensions` items must map cleanly to `ScoreDimension` dataclass. `grader_roster` YAML shape may differ per app — loader must fail-soft with a warning and skip misshapen fields. | ~12k | Draft |
| W3.P1 | Mapper-driven dim_scores | `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (modify `_build_pass_run_context`) | Mapper takes an L2 receipt shape. Need to synthesize a receipt that populates the keys the mapper's YAML extractors read. Fallback for apps without `rubric_output_map.yaml`. | ~8k | Draft |
| W4.P1 | Real hashes + verify | `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (modify `_build_receipts`) + end-to-end verification | Must keep deterministic ordering for reproducibility; short-circuit when config file absent. | ~5k | Draft |

## ADG_GRAPH_LAYER_EVIDENCE

- **MV `mv_dependency_cone_risk`** — confirms `v6/preflight.py` edit is bounded; downstream consumers are only `pipeline.py` + tests.
- **MV `mv_chokepoint_bridges`** — `normalize_to_packet` IS the chokepoint between receipts and packet; single chokepoint modified additively.
- **Semantic edge `flows_to`** — receipts → normalize_to_packet → packet.app_id → app_specific_evaluator.evaluate() → app_eval.bound → pipeline span emit. Closed chain proved end-to-end by W1.P1.
- **P-view `v_p2_runtime_harness_ready`** (future) — flips from "evaluator bound without records" to "evaluator bound WITH records AND passed=True".

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surfaces | Impact |
|---|---|---|---|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/preflight.py` | L3 | high (~15 via pipeline.py chokepoint) | CENTRAL_DEPENDENCY | Execution, Observability | low — additive field population; no behavior change when fields absent |
| `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` | tools | 1 (compiler evidence producer) | ORCHESTRATOR | Observability | low — harness-local changes |
| `tools/cert/apps_e2e/_harness_store_loader.py` | tools | 0 (new) | ORCHESTRATOR | State | low — isolated harness helper |

No L0/L5 boundary crossing. Layer multiplier 1.0. Blast radius bounded to L3 preflight + tools/.

## Files In Scope

- `agentic_core/L3_orchestration/exit_eval/v6/preflight.py` (modify)
- `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_pipeline.py` (extend)
- `tools/cert/apps_e2e/_harness_store_loader.py` (new)
- `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (modify)

4 files. T2 plan.

## Non-Goals

- No changes to the v6 pipeline's X1/X2/X3 logic.
- No touching the 8 FEC producers or the cert/__init__.py registrations.
- No changes to compiler or CI gate logic; regression is "same compiler, better evidence".
- No changes to runtime `AppDomainStore` singleton or production app-boot init paths.
- No new APPS-DOM-* requirement rows.

## Gap Register

| Gap | Owner | Resolution |
|---|---|---|
| Apps without `rubric_output_map.yaml` (check existence) | W3.P1 | Fall back to prior score synthesis; log `dim_scores_source: "synthetic_fallback"` on fixture |
| Grader roster YAML shape variance across apps | W2.P1 | Loader fail-soft per app; skip that app's grader_roster put if parse fails; log reason in loader output |
| Pipeline emit vs post-hoc enrichment divergence | W1.P1 + W4.P1 | Harness stops post-hoc enriching once pipeline emits the span natively; verification step confirms span comes from pipeline, not harness |

## Verification Plan (W4.P1)

1. Run `python tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` — all 8 apps captured.
2. Inspect one fixture: confirm `policy_hash` starts with `sha256://` and 16hex, `dim_scores_source == "mapper"` where `rubric_output_map.yaml` exists, `app_specific_eval.bound == True`, and `app_specific_eval.passed == True` (real PASS via loaded store + real mapper scores).
3. Run merger + compiler → confirm `signed_off=45 / blocked=0`, `trust_level=INTEGRITY_PROOF`.
4. Run full v6 + apps_contract test suites — confirm 976 tests still pass.
5. Emit `DECISION_OUTCOME: decision_id=dec_19dedd3f565173b7f, execution_completed=1, tests_passed=1, promote_to_pattern=1, notes="evidence gaps closed"`.

## AG_QUEUE_SEED

(none — no Author-Gate decisions expected; scope is additive wiring.)
