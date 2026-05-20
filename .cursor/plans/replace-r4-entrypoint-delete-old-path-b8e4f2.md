---
plan_id: replace-r4-entrypoint-delete-old-path-b8e4f2
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Replace R4 Entrypoint — Delete Old Path (Chat Closeout)

Retrospective plan for the apps_rg shadow-entrypoint burndown and route-neutral single-action spine replacement (2026-05-20). R4 becomes `route_family` data only; whole-run generation requires R1A/R1B cache preflight evidence before invoking the spine.

> **Receipts:** [replace_r4_entrypoint_delete_old_path_closeout_receipt.md](docs/reports/apps_rg/replace_r4_entrypoint_delete_old_path_closeout_receipt.md) · [hard_delete_residual_shadow_module_paths_closeout_receipt.md](docs/reports/apps_rg/hard_delete_residual_shadow_module_paths_closeout_receipt.md) · [delete_remaining_legacy_ops_shadow_surfaces_closeout_receipt.md](docs/reports/apps_rg/delete_remaining_legacy_ops_shadow_surfaces_closeout_receipt.md) · [prove_r4_entrypoint_deletion_validity_audit_receipt.md](docs/reports/apps_rg/prove_r4_entrypoint_deletion_validity_audit_receipt.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-20

---

## Context (SCQA)

- **Situation** — `integrated_r4_deterministic_pipeline_run.py` was the sole composer for U0→L1→L0→C0 bypass→L2→Exit→exhaust→L7; apps_rg retained shadow `dispatch/*_dispatch`, `_offline/`, and legacy ops entrypoints.
- **Complication** — Entrypoint identity was coupled to `R4_SINGLE_ACTION`; cache hits could be bypassed by direct spine import; product proof did not require preflight receipts.
- **Question** — How do we hard-delete shadow paths and replace the R4-named entrypoint without shims while enforcing cache preflight on whole-run generation?
- **Answer** — `integrated_single_action_spine_run` + `cache_preflight_evidence` + canonical_dispatch ordering + product proof gate BLOCK; delete old module with no stub.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Shadow dispatch / `_offline` hard-delete → `internal/` + `sections/*_lane_api` | ✅ DONE | contract + unit | apps_rg/runtime, tests |
| W2 | Legacy ops shadow surfaces (CI prove script, narrative_pass, etc.) | ✅ DONE | ci boundary helpers | ops_scripts, tests/helpers |
| W3 | R4 deletion audit + controlled probe | ✅ DONE | audit receipt | docs/reports |
| W4 | New spine composer + cache preflight evidence module | ✅ DONE | — | agentic_core/entrypoints, apps_rg/cache |
| W5 | Repoint dispatch/tests, product proof gate, delete old R4 | ✅ DONE | +121 pytest | canonical_dispatch, __main__, tests |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Delete `dispatch/*_dispatch`, move lane APIs to `sections/` | ✅ DONE |
| W1.2 | Rename `_offline/` → `internal/`; `run_dispatch_main` ImportError | ✅ DONE |
| W2.1 | Delete `prove_apps_rg_e2e_runtime.py`, `narrative_pass.py` | ✅ DONE |
| W2.2 | CI helpers → `tests/helpers/ci_lane_dev_boundary.py` | ✅ DONE |
| W3.1 | ADG audit + deletion validity probe | ✅ DONE |
| W4.1 | `integrated_single_action_spine_run.py` + manifest fields | ✅ DONE |
| W4.2 | `cache_preflight_evidence.py` hit/miss receipts | ✅ DONE |
| W5.1 | Repoint `canonical_dispatch`, `apps_rg/__main__` | ✅ DONE |
| W5.2 | Product proof gate cache evidence requirement | ✅ DONE |
| W5.3 | Delete `integrated_r4_deterministic_pipeline_run.py` | ✅ DONE |
| W5.4 | `test_single_action_spine_entrypoint.py` + regression bundle | ✅ DONE |

---

## Out Of Scope

- Live canonical whole-run product / Fort Knox certification PASS
- Full-repo pytest green
- Historical archived plan markdown refresh (doc-only)
- `agentic_core` spine refactor beyond entrypoint swap

---

## Wave 1 — Shadow module path hard-delete

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Acceptance** (met):
- Old `apps_rg.runtime.dispatch.*_dispatch` paths not importable
- `_offline/` eliminated; helpers under `internal/` with non-CLI guards
- `test_no_outside_main_runtime_entrypoints.py` passes

---

## Wave 2 — Legacy ops shadow surfaces

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Acceptance** (met):
- `ops_scripts/ci/prove_apps_rg_e2e_runtime.py` and `ops_scripts/apps_rg/narrative_pass.py` deleted
- CI boundary helpers relocated to tests

---

## Wave 3 — R4 entrypoint deletion audit

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Acceptance** (met):
- Verdict `DELETE_AFTER_REPLACEMENT_VALID` documented
- Controlled probe: remove file → import failures; restored before replacement landed

---

## Wave 4 — Single-action spine + cache evidence

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Acceptance** (met):
- `run_integrated_single_action_spine` + `ROUTE_FAMILY = R4_SINGLE_ACTION` as data
- Manifest fields: `cache_preflight_completed`, `r1a_preflight_status`, `r1b_preflight_status`, `cache_result`, `cache_miss_receipt_ref`, `generation_spine_invocation_allowed`, `generation_spine_invocation_blocked_reason`, `route_family`

---

## Wave 5 — Repoint, enforce, delete old R4

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Acceptance** (met):
- `integrated_r4_deterministic_pipeline_run.py` deleted (no shim)
- `python -m apps_rg --help` exit 0
- Import old module → `ModuleNotFoundError`
- R1A/R1B hit skips spine; miss invokes spine once with evidence
- Product proof FAIL without cache receipts
- 121 targeted pytest passed

**Commands**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m apps_rg --help
python -m pytest tests/unit/apps_rg/test_single_action_spine_entrypoint.py tests/unit/apps_rg/test_r1b_whole_run_entrypoint_parity_w9b.py tests/unit/apps_rg/test_integrated_product_proof_gate.py tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_pipeline_profile_hardening.py tests/_apps_contract/test_apps_rg_r4_manifest_l2_fault_consistency.py tests/_apps_contract/test_apps_rg_generation_entrypoints.py tests/governance/test_integrated_single_action_run_identity.py -o addopts= -q
```

---

## Definition of Done

DoD-1: Old R4 entrypoint module not importable; zero active Python imports
- Evidence: `test_old_r4_module_not_importable`; grep agentic_core/apps_rg/tests
- Status: DONE

DoD-2: New spine preserves governed chain; route_family as data
- Evidence: `test_new_spine_module_importable`; L7 emit tests pass
- Status: DONE

DoD-3: Cache preflight gates whole-run generation (hit skips, miss receipts)
- Evidence: `test_r1a_hit_skips_generation_spine`, `test_cache_miss_invokes_spine_once`, r1b parity test
- Status: DONE

DoD-4: Product proof cannot PASS without cache preflight artifacts
- Evidence: `test_direct_spine_without_cache_fails_product_proof`
- Status: DONE

DoD-5: `python -m apps_rg --help` exits 0; plan on disk + Notion Completed
- Evidence: CLI smoke + this file + Notion Plans row
- Status: DONE

---

## Verification vs Deferral

| Item | Status | Notes |
|------|--------|-------|
| Shadow path deletion | DONE | W1–W2 |
| Spine replacement | DONE | W4–W5 |
| Live whole-run product proof | DEFERRED | section/lane proofs only |
| Fort Knox L7 certification | DEFERRED | not claimed |
| Doc refresh of archived R4 path names | DEFERRED | optional |

---

## Marker Log (chat closure)

```
WAVE_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 wave=1 note="+contract tests, 20+ files, scope=shadow-hard-delete"
WAVE_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 wave=2 note="ops delete, 2 files, scope=legacy-ops-shadow"
WAVE_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 wave=3 note="audit receipt, 1 doc, scope=deletion-validity"
WAVE_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 wave=4 note="2 new modules, scope=spine+cache-evidence"
WAVE_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 wave=5 note="+121 tests, 30+ files, scope=repoint-delete-proof"
PLAN_COMPLETE: plan=replace-r4-entrypoint-delete-old-path-b8e4f2 note="R4 entrypoint deleted; single-action spine + cache preflight enforced"
```
