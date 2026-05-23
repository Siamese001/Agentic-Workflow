# Spine unification — open scope & edge-case hardening (2026-05-23)

Plan: [apps-rg-spine-only-unification-d8f4a2](../../.cursor/plans/apps-rg-spine-only-unification-d8f4a2.md)

## Completed in this tranche

| Item | Evidence |
|------|----------|
| W2 single entry | [apps_rg_spine_run.py](../../apps_rg/runtime/spine/apps_rg_spine_run.py), [section_cli_runners.py](../../apps_rg/runtime/spine/section_cli_runners.py) |
| W3 bridge deletion | Removed `section_*_bridge.py`, `proof_pool_lane_integration.py`; logic in `spine/` + `c0/section_proof_loader.py` |
| W4 Exit authority | [section_x3_finalize.py](../../apps_rg/runtime/spine/section_x3_finalize.py) + all section lanes |
| W6 inventory | [one_spine_inventory.py](../../apps_rg/runtime/one_spine_inventory.py) `two_paths_found: false` |
| CI gate | `python ops_scripts/ci/check_apps_rg_single_spine.py` → 0 ERROR findings |
| Edge hardening (2026-05-23) | FEC dual-filename alias, competencies proof_bundle→x3 ordering, duplicate FEC emit removed, spine input validation |

## Open scope (not done)

### P0 — proof / quality (other plans)

| ID | Scope | Owner plan |
|----|--------|------------|
| OS-TRACK-C | Executive summary unanimous `X3_ALLOW` (judge soft-fail remains) | [apps-rg-proof-pool-c0-ssot-a7f3e2](../../.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md) |
| OS-LIVE-ES | Post-spine live Brown & Brown exec-summary proof artifact | Re-run `python -m apps_rg --section executive_summary` |

### P1 — spine plan waves

| ID | Wave | Gap |
|----|------|-----|
| OS-W5 | W5 | Full résumé still uses integrated R4 only — no L3 multi-section loop + assembly + package X1D in `apps_rg_spine_run` |
| OS-W5-ASM | W5 | `final_resume_assembler` not invoked from spine entry for whole-run |
| OS-W5-PKG | W5 | `resume_package_disposition` lane rollup may still exist |
| OS-W7 | W7 | `agentic_core` prerequisite gate + judge YAML migration (author-gate required) |
| OS-W3-C03 | W3 | `c03_graphrag_bound.py` still on disk (not product-path forbidden; not deleted) |
| OS-W3-MIRROR | W3/W6 | `section_runtime_exhaust_spine_receipt.py`, `section_l2_spine_receipt.py`, `section_one_spine_no_two_path.py` still present |
| OS-W2-AG2 | W2 DoD | Section runs do not yet call `run_ag2_retrieval_and_prompt` end-to-end — lanes still use proof-pool→FEC compose path inside section modules |

### P2 — hygiene

| ID | Item |
|----|------|
| OS-DOCS | [open_scope_closeout_20260523.md](open_scope_closeout_20260523.md) stale (still says W2 in progress) |
| OS-TERM | [section_spine_terminology.py](../../apps_rg/runtime/section_spine_terminology.py) still lists bridge module names in enums |
| OS-REPORTS | Historical `docs/reports/apps_rg/one_spine_*` bridge PASS language |
| OS-PYTEST-WIN | Contract pytest collection `WinError 1920` on some Windows hosts — gate script is SSOT |

## Edge cases hardened (2026-05-23)

1. **FEC filename drift** — Spine writes `final_evidence_contract.json` plus legacy alias `final_evidence_contract_bridge.json`; certification checks spine name first.
2. **Duplicate FEC emit** — Removed second `emit_spine_c0_fec_artifacts` call in `wire_spine_c0_fec_for_section`.
3. **Competencies x3 / proof bundle** — `proof_eligible` fields merged into `x3_disposition.json` before Exit receipts.
4. **Spine entry validation** — `run_apps_rg_spine` fails fast on missing `target_company`/`target_role` or empty `section_id` when `scope=section`.
5. **X3 refresh API** — `persist_section_x3_mirror` + `refresh_section_exit_after_x3_change` for post-clarify mutations.

## Recommended next commands

```powershell
python ops_scripts/ci/check_apps_rg_single_spine.py
python -m pytest tests/unit/apps_rg/test_section_x3_finalize.py -q -o addopts=
```
