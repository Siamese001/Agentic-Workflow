# Legacy dependency burndown — Phase D2

**Plan:** [apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md)  
**Date:** 2026-05-19  
**Status:** PARTIAL (helper extraction + `is` parity PASS; broad `-k` filter and 2 stub-runtime contract tests not clean)

## Goal

Reduce remaining **helper** fan-in on `competencies_dispatch` / `ibm_narrative_dispatch` after Phase D moved execution to `*_lane_execution`. No archive/delete, no X2/X3 weakening, no live proof.

## HELPER_FANIN_BEFORE

| Consumer | Symbols from dispatch |
|----------|---------------------|
| [headline_lane.py](apps_rg/runtime/sections/headline_lane.py) | `build_resume_support_blob`, `load_companion_context`, `load_base_resume` |
| [competencies_lane.py](apps_rg/runtime/sections/competencies_lane.py) | CLI defaults (`PROMPT_ID`, `TARGET_*`, `JD_TEXT_DEFAULT`, …) |
| [ibm_narrative_lane.py](apps_rg/runtime/sections/ibm_narrative_lane.py) | IBM CLI defaults + `REPO_ROOT` |
| [ibm_narrative_dispatch.py](apps_rg/runtime/sections/ibm_narrative_lane_api.py) | `collect_employment_bullets` via competencies_dispatch |
| [proof_pool_resolver.py](apps_rg/runtime/proof_pool_resolver.py) | lazy `collect_employment_bullets` from competencies_dispatch |
| [competencies_x2_diagnostics.py](apps_rg/runtime/competencies_x2_diagnostics.py) | `term_phrase` |
| [proof_pool_source_fact_validation.py](apps_rg/runtime/validators/proof_pool_source_fact_validation.py) | lazy `write_json` |

Dispatch size after Phase D: competencies **1574** LOC, ibm_narrative **647** LOC.

## HELPERS_EXTRACTED

| Module | Symbols |
|--------|---------|
| [lane_artifact_io.py](apps_rg/runtime/sections/lane_artifact_io.py) | `sha16`, `write_json` |
| [companion_lane_context.py](apps_rg/runtime/sections/companion_lane_context.py) | `COMPANION_LANES`, `load_companion_context`, `build_resume_support_blob`, `build_c0_proof_support_blob` |
| [competencies_term_phrase.py](apps_rg/runtime/sections/competencies_term_phrase.py) | `term_phrase` |
| [competencies_lane_defaults.py](apps_rg/runtime/sections/competencies_lane_defaults.py) | competencies lane CLI defaults + `REPO_ROOT` |
| [ibm_narrative_lane_defaults.py](apps_rg/runtime/sections/ibm_narrative_lane_defaults.py) | IBM narrative lane CLI defaults + `REPO_ROOT` |
| [ibm_narrative_metric_trim.py](apps_rg/runtime/sections/ibm_narrative_metric_trim.py) | `truncate_narrative_after_first_metric_hit`, `collapse_narrative_sentence_for_companion_metric_budget` |
| [competencies_x3.py](apps_rg/runtime/exit/competencies_x3.py) | `clarify_x3_for_competencies_live_provider_preflight` |
| [resume_employment_bullets.py](apps_rg/runtime/sections/resume_employment_bullets.py) | `collect_employment_bullets` (pre-existing SSOT; fan-in redirected) |

## REEXPORTS_KEPT

Both dispatch modules import from sections/exit SSOT and re-export the same objects. [test_lane_pa_helper_parity.py](tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py) asserts `dispatch.symbol is sections.symbol` for all extracted helpers.

## HELPER_FANIN_AFTER

| Consumer | Change |
|----------|--------|
| headline_lane | companion helpers → `companion_lane_context`; `load_base_resume` still from dispatch |
| competencies_lane / ibm_narrative_lane | defaults → `*_lane_defaults` |
| proof_pool_resolver | `collect_employment_bullets` → `resume_employment_bullets` |
| competencies_x2_diagnostics | `term_phrase` → `competencies_term_phrase` |
| proof_pool_source_fact_validation | `write_json` → `lane_artifact_io` |

`git grep` dispatch imports (apps_rg, tests, docs): **8** lines (mostly contract tests + one headline `load_base_resume`).

Dispatch size after D2: competencies **1476** LOC (−98), ibm_narrative **551** LOC (−96).

## BLOCKERS (risky — skipped)

- **Competencies repair stack** (`coerce_structured_*`, `collapse_duplicate_*`, `_fix_fact_id_typos`, `rebuild_claim_ledger_*`, …) — large, high blast radius; contract tests intentionally import from dispatch.
- **`load_base_resume`** — single headline fan-in; thin wrapper.
- **Per-lane duplicate `write_json`** in other lane files — out of D2 narrow scope (only dispatch + proof_pool validation seam).

## QUARANTINE_READINESS

- Execution: already on `*_lane_execution` (Phase D).
- Helpers: **reduced** production fan-in; dispatch remains compat surface for tests and lane_execution hydrate.
- **DELETE_GATE:** not met — archive Phase E still blocked.

## BEHAVIOR_CHANGE / RUNTIME_CHANGE

**false** — object identity preserved via re-exports; no gate/schema edits; no live proof run.

## Commands & tests

| Command | Result |
|---------|--------|
| `python -m compileall agentic_core apps_rg apps_shared apps_eval -q` | exit 0 |
| `git grep … competencies_dispatch\|ibm_narrative_dispatch` | 8 matches |
| `pytest tests/unit/apps_rg/runtime/sections/test_lane_pa_helper_parity.py` | 13 passed |
| `pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py tests/_apps_contract/test_apps_rg_canonical_runtime_hygiene.py` | 28 passed |
| `pytest tests/_apps_contract -k "competencies or ibm_narrative"` | 153 passed, **44 failed**, 2 errors (broad filter) |
| Scoped seam subset (canonical lane + x2 source facts + ibm slice + live gate + x2 proof quality) | 68 passed, 3 failed → **1 fixed** (offline stub test now targets `competencies_lane_execution`); 2 remain OFFLINE_CONTRACT_STUB X2/X3 on mock run |

## NEXT_ACTION

Phase E gated archive only after repair-helper fan-in zero or explicit policy; optional: neutral `load_base_resume` in `resume_resolution`.

## Orthogonal sessions

Unrelated to Executive Summary chat [17c779f9-1065-4362-9bdf-dae0471e23c9](../../../.cursor/projects/c-Git-Agentic-Workflow-FRESH/agent-transcripts/17c779f9-1065-4362-9bdf-dae0471e23c9/17c779f9-1065-4362-9bdf-dae0471e23c9.jsonl).
