# Spine unification — open scope & edge-case hardening (2026-05-23)

Plan: [apps-rg-spine-only-unification-d8f4a2](../../.cursor/plans/apps-rg-spine-only-unification-d8f4a2.md)  
Notion: [Plans row](https://www.notion.so/36927693f55c8190b30bde1f6534e2a7) (`page_id=36927693-f55c-8190-b30b-de1f6534e2a7`)

## Completed in this tranche

| Item | Evidence |
|------|----------|
| W1 CI ratchet | [check_apps_rg_single_spine.py](../../ops_scripts/ci/check_apps_rg_single_spine.py) → 0 ERROR findings |
| W2 single entry | [apps_rg_spine_run.py](../../apps_rg/runtime/spine/apps_rg_spine_run.py), [section_cli_runners.py](../../apps_rg/runtime/spine/section_cli_runners.py) |
| W3 bridge deletion | Removed `section_*_bridge.py`, `proof_pool_lane_integration.py`; logic in `spine/` + [section_proof_loader.py](../../apps_rg/runtime/c0/section_proof_loader.py) |
| W4 Exit authority | [section_x3_finalize.py](../../apps_rg/runtime/spine/section_x3_finalize.py) + all section lanes |
| W6 inventory | [one_spine_inventory.py](../../apps_rg/runtime/one_spine_inventory.py) `two_paths_found: false` |
| Git on `main` | Commit `3e7ab52413` (2026-05-23) — spine W2–W6 |
| Edge hardening | FEC dual-filename alias, competencies proof_bundle→x3 ordering, spine input validation, duplicate FEC emit removed |
| Live E2E (section) | `python -m apps_rg --section executive_summary` → [exec_summary_20260523_171726](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_171726); spine contract filenames present; `CLI_PATH_STATUS=PASS` |

## Post-commit wiring fixes (local — commit pending)

| Fix | File(s) |
|-----|---------|
| Section runner kwargs filtered by signature | [apps_rg_spine_run.py](../../apps_rg/runtime/spine/apps_rg_spine_run.py) |
| `ExitEvalPipeline()` (no `app_name=` kwarg) | [section_x3_finalize.py](../../apps_rg/runtime/spine/section_x3_finalize.py) |
| Exit after `sealed_l2_artifact.json` | [section_l2_lane_integration.py](../../apps_rg/runtime/section_l2_lane_integration.py), `finalize_section_spine_exit_after_sealed_l2` |
| Negative-control test uses deleted bridge import | [test_apps_rg_no_second_pipeline.py](../../tests/_apps_contract/test_apps_rg_no_second_pipeline.py) |

## Open scope (not done)

### P0 — proof / quality (other plans)

| ID | Scope | Owner plan |
|----|--------|------------|
| OS-TRACK-C | Executive summary unanimous `X3_ALLOW` (judge soft-fail remains) | [apps-rg-proof-pool-c0-ssot-a7f3e2](../../.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md) |
| OS-LIVE-ES-BB | Brown & Brown live exec-summary post-spine | Re-run with targeting SSOT JD/brief |

### P1 — spine plan waves

| ID | Wave | Gap |
|----|------|-----|
| OS-W5 | W5 | Full résumé still uses integrated R4 only — no L3 multi-section loop + assembly + package X1D in `apps_rg_spine_run` |
| OS-W5-ASM | W5 | `final_resume_assembler` not invoked from spine entry for whole-run |
| OS-W5-PKG | W5 | `resume_package_disposition` lane rollup may still exist |
| OS-W7 | W7 | `agentic_core` prerequisite gate + judge YAML migration (author-gate required) |
| OS-W2-AG2 | W2 DoD | Section runs do not yet call `run_ag2_retrieval_and_prompt` end-to-end — lanes still use proof-pool→FEC compose path inside section modules |
| OS-E2E-WIRING | — | Commit post-`3e7ab52413` spine wiring fixes (see table above) |
| OS-E2E-ALL-LANES | — | Live smoke for six remaining `--section` lanes on spine |

### P2 — hygiene

| ID | Item |
|----|------|
| OS-W3-C03 | `c03_graphrag_bound.py` still on disk (not product-path forbidden; not deleted) |
| OS-W3-MIRROR | `section_runtime_exhaust_spine_receipt.py`, `section_l2_spine_receipt.py`, `section_one_spine_no_two_path.py` still present |
| OS-TERM | [section_spine_terminology.py](../../apps_rg/runtime/section_spine_terminology.py) still lists bridge module names in enums |
| OS-REPORTS | Historical `docs/reports/apps_rg/one_spine_*` bridge PASS language |
| OS-PYTEST-WIN | Contract pytest collection `WinError 1920` on some Windows hosts — gate script is SSOT |
| OS-TEST-STUB | `test_subprocess_cli_emits_exec_summary_artifacts_and_x3_shape` env forbids offline stub — update test harness |

## Edge cases hardened (2026-05-23)

1. **FEC filename drift** — Spine writes `final_evidence_contract.json` plus legacy alias `final_evidence_contract_bridge.json`; certification checks spine name first.
2. **Duplicate FEC emit** — Removed second `emit_spine_c0_fec_artifacts` call in `wire_spine_c0_fec_for_section`.
3. **Competencies x3 / proof bundle** — `proof_eligible` fields merged into `x3_disposition.json` before Exit receipts.
4. **Spine entry validation** — `run_apps_rg_spine` fails fast on missing `target_company`/`target_role` or empty `section_id` when `scope=section`.
5. **X3 refresh API** — `persist_section_x3_mirror` + `refresh_section_exit_after_x3_change` for post-clarify mutations.
6. **Sealed-L2-before-exit** — Product-visible ExitEvalPipeline runs only after `finalize_section_l2_after_output`.

## Recommended next commands

```powershell
python ops_scripts/ci/check_apps_rg_single_spine.py
python -m pytest tests/_apps_contract/test_apps_rg_no_second_pipeline.py tests/unit/apps_rg/test_section_x3_finalize.py -q -o addopts= --ignore=lib64 --ignore=lib
python -m apps_rg --section executive_summary --target-company "CI-Probe-Co" --target-role "Software Engineer" --jd tests/_fixtures/ci-probe-jd.txt --manual-brief tests/_fixtures/ci-probe-briefing.txt --allow-non-allow-exit-zero
```
