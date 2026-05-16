# apps_rg R4 modular section-lane migration — closeout receipt

**Date:** 2026-05-16  
**Scope:** apps_rg R4 integrated recipe (modular section lanes vs monolithic envelope).

## Original problem

Offline and modular **section** grain already existed (per-lane dispatch, subprocess proofs, deterministic assembly paths), but the **canonical R4 product path** still used **monolithic full-resume** generation: one tailor-existing CPA plus `run_apps_rg_l2_envelope` for body copy. Operators could confuse the offline orchestrator with the governed R4 CLI spine.

## Final state

| Item | Value |
|------|--------|
| Default R4 generation mode | `modular_section_lanes` (when `APPS_RG_R4_GENERATION_MODE` is unset) |
| Rollback | `legacy_full_resume` via explicit `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` |
| SSOT / canonical proven route | Modular section lanes (`r4_generation_route`) |
| `runtime_generation_grain` | `section_lane` |
| `runtime_merge_grain` | `full_resume` |
| `artifact_grain` | `full_resume` |

## Proof runs

Recorded run directories (repo-relative):

- `artifacts/apps_rg/runs/cli_e6a9b9d74b09`
- `artifacts/apps_rg/runs/cli_b22cad324e30`

## Proof highlights (both runs)

- Exit 0 on successful product completes; disposition `X3D` at integrated manifest level.
- `outcome_authorized=true` (and/or equivalent `REAL_RESUME` outcome evidence in output manifest).
- `outputs/generated_resume.json` present.
- `outputs/resume.docx` present.
- `apps_rg_output_manifest.json`: `docx_verified=true`.
- Modular path: `final_schema_valid=true` (rg_output schema validation receipt).
- Seven section lanes with `generation_status=REAL_LLM`, `MOCKED` lane count **0**.
- No `section_lane=full_resume`; no full-resume provider lane in modular rollup.
- No `run_apps_rg_l2_envelope` on the modular generation path.
- No silent fallback markers in audited runtime artifacts.

## Final hardening (recipe PASS semantics)

- **Policy ID:** `apps_rg.modular_lane_recipe_policy.v1`
- **Fatal lanes block recipe PASS:** any lane classified as fatal in `recipe_lane_policy.fatal_lane_failures` forces recipe-level `FAIL` (no PASS with fatal lane set).
- **Judge / provider degradation:** `X3_REVIEW_JUDGE_PROVIDER_BLOCKED` (and related non-deterministic review codes under policy) may be **`DEGRADED_ALLOWED`** only when **`REAL_LLM` + `provider_call_attempted` + `lane_x2_pass`** for that lane row.
- **Final `rg_output` schema** remains **required** for `ok_for_recipe_context` / product handoff: `final_schema_valid` and merged structured resume predicates unchanged (not weakened).

## Tests

Latest targeted modular / contract pytest slice: **71 passed, 0 failed** (with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and scoped test list as used in migration verification).

## Rollback

Set:

```text
APPS_RG_R4_GENERATION_MODE=legacy_full_resume
```

Contract tests that stub the envelope may pin this in fixtures; product default remains modular until unset.

## Boundaries (unchanged commitments)

- **agentic_core:** not modified for this migration.
- **Schema:** not weakened; validators and merge discipline unchanged in intent.
- **Content:** no synthetic bullets policy preserved in merge/build paths (e.g. compact early-career handling without fabricated bullets).
- **DOCX:** no DOCX export treated as success before final schema validation / recipe gates consistent with existing modular recipe ordering.

## References (code SSOT)

- `apps_rg/l2_recipe/r4_generation_route.py` — grains, proof run id, execution style.
- `apps_rg/l2_recipe/r4_generation_mode.py` — default vs explicit legacy.
- `apps_rg/l2_recipe/modular_lane_recipe_policy.v1` — `apps_rg/l2_recipe/modular_lane_recipe_policy.py`.
- `apps_rg/l2_recipe/modular_resume_generation.py` — policy summary, `section_provider_calls.phase1.v2`.

---

*Closeout receipt: narrative + pointers only; filesystem SSOT for manifests remains under `artifacts/apps_rg/runs/<run_id>`.*
