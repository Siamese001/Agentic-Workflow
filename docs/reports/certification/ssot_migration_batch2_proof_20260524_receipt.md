# SSOT certification/chroma/archives migration — proof receipt

**Date:** 2026-05-24  
**Scope:** Close PARTIAL from batch-2 folder migration (`certification/` → `data/config/artifacts`, `archives/` → `artifacts/archives/`)

## Results

| Gate | Result |
|------|--------|
| `python tools/cert/compile_requirement_signoff.py` | exit 0 — 102 reqs, `trust_level=DEVELOPMENT_PROOF` (0 signed / 102 blocked — stale evidence, not path breakage) |
| `python ops_scripts/ci/verify_final_requirement_signoff_bundle.py` | exit 0 — `status=PASS`, `checks=119`, `failures=0` |
| `python ops_scripts/ci/check_fortknox_clean_bundle.py` | exit 0 — PASS |
| `python ops_scripts/ci/generate_mutation_rejection_report.py` | exit 0 — 40/40 scenarios, `overall_verdict=PASS` |
| `cert_paths` existence | `data/certification/requirements_source.json`, `artifacts/certification/integrated_runtime/` OK |
| `pytest tests/runtime/test_fort_knox_requirement_signoff.py` | PASS (included in 47 passed) |
| `pytest tests/_apps_contract/test_apps_rg_binding_import_ssot.py` | PASS (4/4) |

## Path repair (this turn)

- Fixed `verify_final_requirement_signoff_bundle.py` `REPO_ROOT` (`parents[2]`) + `cert_paths` imports.
- Fixed `generate_mutation_rejection_report.py` repo root, clean paths, compiler import from `tools/cert/`.
- Updated CI (`runtime-certification.yml`), hooks, Fort Knox skill, tests, `check_fortknox_clean_bundle.py` to `tools/cert/` + `ops_scripts/ci/` (removed dead `scripts/compile_*` references).
- Synced `.windsurf/scripts/post_write_cert_stage.py` to new layout.

## Artifacts touched by gates

- [final_requirement_signoff_report.json](artifacts/certification/final_requirement_signoff_report.json)
- [final_requirement_signoff_bundle_verification.json](artifacts/certification/final_requirement_signoff_bundle_verification.json)
- [fortknox_mutation_rejection_report.json](artifacts/certification/fortknox_mutation_rejection_report.json)

## Out of scope (not migration regressions)

- `check_signoff_freshness.py` — 617/617 assertions stale (~548h); requires evidence re-emission, not path fixes.
- `test_apps_e2e_requirements_source.py` — catalog now 45 rows incl. `APPS-DOM-*`; tests still expect 33 `APPS-REQ-*` only (pre-existing drift).

## STATUS

**PASS** for SSOT migration + Fort Knox compiler/verifier/mutation path seam.
