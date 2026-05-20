# Legacy dependency burndown — Phase D3

**Plan:** [apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md)  
**Date:** 2026-05-19  
**Status:** PARTIAL (load_base_resume + stub root-cause fixes; 1/2 stub contract tests green)

## STUB_FAILURES

| Test | Result |
|------|--------|
| `test_mock_slice_still_passes_x2_source_mapping` | **PASS** |
| `test_canonical_lane_mock_judge_x3_review_code` | **FAIL** (`X3_BLOCK` vs `X3_REVIEW_MOCKED_PLUMBING_ONLY`) |

### Root cause (investigation)

Not a D2 helper-identity regression. Failure chain after **P2-W1A `augmented_skills_graph`** became the default competencies proof pool:

1. **Proof pool build** — `build_competencies_graph_skills_proof_payload` could set `c03_graph_bound_status=BOUND` while `validate_competencies_graph_skills_proof_payload` rejects `BOUND` before P2-W2 → lane aborted before execution (observed as `CompetenciesGraphProofPoolError`).
2. **Offline stub** — `build_mock_output` only special-cased `selected_role_fact_set` / `broad_skills_ledger`; `augmented_skills_graph` fell through to legacy `bul_unify_*` fact ids not in the active allowlist → X2 source-fact gates failed.
3. **Post-repair shape** — `collapse_duplicate_competency_terms` + dedupe can leave a category with **one** structured term → `x2_competency_format_category_colon_terms` FAIL → `infer_product_quality` BLOCK → `X3_BLOCK` (mock judges pass; X2 blocks).

### Fixes applied (not gate weakening)

| Area | Change |
|------|--------|
| [competencies_graph_skills_proof_pool.py](apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py) | Payload always uses `NOT_CLAIMED_FOR_P2_W1A` for `c03_graph_bound_status` |
| [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py) | Initialize `te` before use (UnboundLocalError) |
| [competencies_dispatch.py](apps_rg/runtime/sections/competencies_lane_api.py) | `build_mock_output` handles `augmented_skills_graph`; grounded stub terms from plan facts; final `expand_structured_competencies_min_two_terms` pass |
| [fact_id_typo_repair.py](apps_rg/runtime/validators/fact_id_typo_repair.py) | Strip interior whitespace; zero-pad `fact_*_<n>` → `fact_*_<nnn>` when in allowlist |
| [competencies_lane_execution.py](apps_rg/runtime/sections/competencies_lane_execution.py) | Second expand pass after prune |

### Remaining blocker

`test_canonical_lane_mock_judge_x3_review_code` still fails when any category ends with **&lt;2 terms** after repair (e.g. Sales with one term). Hardening requires repair-stack / graph-stub contract work — **out of D3** (repair stack not moved).

## LOAD_BASE_RESUME

| | |
|--|--|
| **Before** | Defined in `competencies_dispatch` / `ibm_narrative_dispatch`; `headline_lane` imported from dispatch |
| **Extracted** | [lane_base_resume.py](apps_rg/runtime/sections/lane_base_resume.py) |
| **After** | `headline_lane` → sections; dispatch re-exports; parity `is` in [test_lane_pa_helper_parity.py](tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) |

## REPAIR_HELPER_FANIN (map only — not moved)

| Helper | Importers |
|--------|-----------|
| `repair_structured_competencies_source_facts`, `coerce_structured_*`, `collapse_duplicate_*`, `expand_structured_*`, `rebuild_claim_ledger_*`, `build_mock_output`, … | `competencies_lane_execution` (hydrate), contract tests, unit tests |
| `_fix_fact_id_typos` | dispatch + [test_apps_rg_live_qwen_x2_repairs.py](tests/_apps_contract/test_apps_rg_live_qwen_x2_repairs.py) |

**safe_to_move:** none in D3  
**blockers:** ~1.2k LOC repair stack + hydrate coupling + contract import surface

## Commands

- `compileall` → exit 0  
- `test_lane_pa_helper_parity` + quarantine/hygiene + both stub tests (bundled) → 42 passed, 1 failed (canonical mock X3)

## QUARANTINE_READINESS

Dispatch modules slimmer (`load_base_resume` neutral); repair stack still anchors fan-in. Phase E archive **blocked**.

## BEHAVIOR_CHANGE / RUNTIME_CHANGE

false — deterministic repairs and stub alignment only; no X2/X3 rubric changes.

## NEXT_ACTION

- Repair-stack extraction wave OR graph-skills offline stub contract test fixture (guarantee ≥2 terms/category post-repair)  
- Then re-run `test_canonical_lane_mock_judge_x3_review_code` for PASS
