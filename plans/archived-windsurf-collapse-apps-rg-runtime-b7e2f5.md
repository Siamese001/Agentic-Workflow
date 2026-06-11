---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\collapse-apps-rg-runtime-b7e2f5.md'
original_relative_path: 'collapse-apps-rg-runtime-b7e2f5.md'
source_sha256: 165d54e2fa342792d99db92a6292c079690b8a49eddd7ff8772e68c91631b90d
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Collapse `apps_rg/runtime/` → `apps_shared/spine_emission/`

**Plan ID**: `collapse-apps-rg-runtime-b7e2f5`
**Status**: **Completed** (all 4 waves shipped 2026-05-02 UTC-04:00)
**Author**: Cursor Agent
**Tier**: T2 (single-layer migration; one app impacted; zero semantic change required)
**Related plans**:
- Predecessor (DONE): `apps-e2e-spine-cert-wireup-e1c4d7` — authored `apps_shared/spine_emission/` and wired 5 apps through it. §13 "What remains" #3 is exactly this plan.
- ADR reference: `docs/adr/ADR-081-apps-e2e-spine-cert-wireup.md` §Consequences.Negative — documented the duplication as an accepted trade-off at the time of certification.

---

## 1. Intent

Collapse the 700-LOC duplication between `apps_rg/runtime/{__init__,contracts,context,otel_trace}.py` and `apps_shared/spine_emission/*` by migrating `apps_rg/__main__.py` to the shared helper and deleting `apps_rg/runtime/`.

## 2. Why Do It Now

- Duplication was an accepted trade-off ONLY to guarantee apps_rg's certified baseline bundle-hash stability during the W1–W7 wire-up. Now that all 5 other apps are certified through the shared helper without issue, the determinism claim is empirically validated.
- One SSOT cuts future-maintenance cost — any refinement to spine emission (new receipt type, new verifier rule, schema bump) only needs to land once.
- Removes a subtle foot-gun: a future developer editing `apps_shared/spine_emission/` might miss that apps_rg has its own copy.

## 3. Scope

**In**: `apps_rg/runtime/` deletion; `apps_rg/__main__.py` rewrite to use `apps_shared.spine_emission.governed_run`; any shared-helper extensions needed to preserve apps_rg's semantics (late-bound `run_dir`, target_company / target_role passthrough).

**Out**: semantic changes to the apps_rg receipts; any change to the 9 emitted filenames; any change to `apps_rg/config/route_registry.yaml` or `apps_rg/config/l3_dag.yaml`; any change to verifier rules.

## 4. Semantic Parity Requirements (post-migration MUST)

1. apps_rg strict verifier → `SPINE_COMPLETE_CERTIFIED` (same as pre-migration).
2. The 9 emitted receipts land in `artifacts/apps_rg/runs/<ts>/` with the SAME filenames (`u0_intake_envelope.json`, `l1_plan_contract.json`, `route_contract.json`, `l3_bypass_receipt.json`, `l2_execution_receipt.json`, `exit_review_packet.json`, `runtime_exhaust_bundle.json`, `otel_runtime_trace.json`, plus `prompt_assembly_manifest.json` if the new path emits one).
3. `target_company` + `target_role` still populate `u0_intake_envelope.json` (covered by shared U0IntakeEnvelope — fields already Optional).
4. `run_dir` resolves LATE — after `generate_resume.main()` creates its own timestamped dir — so receipts land next to `generated_resume.json` + DOCX, NOT in a separate shared-helper-timestamped dir.
5. 226 tests pass / 1 skip / 0 fail (unchanged).
6. Negative-control suite (23 tests, N1–N20) remains green.

## 5. Wave Structure

| Wave | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---:|---|---|
| **W1 — Extend shared helper** | Add `set_run_dir(path)` method on `GovernedRun`; add `target_company` + `target_role` optional fields on `EmissionConfig` + threading into U0IntakeEnvelope | ~2k | **DONE** | 19 unit tests pass (17 existing + 2 new) |
| **W2 — Migrate apps_rg/__main__.py** | Replace `from apps_rg.runtime import governed_run` with shared helper; pass `EmissionConfig` with the HOP plan, rationale, and target_company/role | ~2k | **DONE** | apps_rg strict = SPINE_COMPLETE_CERTIFIED (0 violations) using shared helper |
| **W3 — Delete `apps_rg/runtime/`** | Remove the 4 files; confirm no residual importers | ~1k | **DONE** | Folder removed; 0 residual imports in live code; apps_rg_e2e/_shared.py self-check relaxed to accept shared-helper path |
| **W4 — Verify + seal** | Full regression (226 tests) + strict verifier (8 of 8 apps) + matrix rebuild | ~1k | **DONE** | 250/2/0 green; 8 of 8 strict PASS; matrix rebuilt |

Total: ~6k tokens.

## 6. Files In Scope

**Modified**:
- `@c:/Git/Agentic-Workflow-FRESH/apps_shared/spine_emission/context.py` (add `set_run_dir`, extend `EmissionConfig` with `target_company`, `target_role`)
- `@c:/Git/Agentic-Workflow-FRESH/apps_shared/spine_emission/contracts.py` (no change — U0 already has target_company/target_role fields)
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/__main__.py:190-262` (migrate to shared helper)
- `@c:/Git/Agentic-Workflow-FRESH/tests/unit/apps_shared/spine_emission/test_spine_emission.py` (+2 tests)
- `@c:/Git/Agentic-Workflow-FRESH/tools/certification/apps_rg_e2e/_shared.py:154` (relax self-check — `governed_run` now imported from apps_shared)

**Deleted**:
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/runtime/__init__.py`
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/runtime/contracts.py`
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/runtime/context.py`
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/runtime/otel_trace.py`

**Untouched**:
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/config/route_registry.yaml`
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/config/l3_dag.yaml`
- All certification artifacts
- All verifier rules

## 7. Risks

| Risk | Mitigation |
|---|---|
| apps_rg U0 envelope gains `app_name` + `entrypoint_command` fields (shared envelope has them; apps_rg's didn't) | These are PURE additions — verifier has no "forbid unknown fields" check on U0; base rules and N1–N20 don't inspect `app_name`/`entrypoint_command` in U0. Validated by running strict after migration. |
| Late-bound `run_dir` semantics change | Preserve existing `set_run_dir` method signature exactly. New test pins the behavior. |
| apps_rg certification regresses | W4 strict verifier is the gate — if it fails, revert the deletion and rework. |

## 8. Supersedes / Is Superseded By

- **Supersedes**: the "accepted duplication" clause in ADR-081 §Consequences.Negative. After this plan ships, ADR-081's duplication trade-off note is updated to reference this plan's closure.
- **Is superseded by**: none.

## 9. Final Closure (2026-05-02 UTC-04:00)

**ALL 4 WAVES SHIPPED.** Duplication collapsed.

### Results

| Check | Result |
|---|---|
| apps_rg strict verifier | **SPINE_COMPLETE_CERTIFIED (0 violations)** |
| Full strict (8 apps) | **8 pass / 0 fail** |
| Bundle emission gate | exit 0 ✅ |
| Spine certification gate (BLOCKING) | exit 0 ✅ |
| Test suite | **250 pass / 2 skip / 0 fail** (was 226/1 — +24 apps_rg_e2e tests + +2 W1 tests, zero regressions) |
| Residual `from apps_rg.runtime` imports in live code | 0 |

### Artifacts

**Added**
- 2 new unit tests in `@c:/Git/Agentic-Workflow-FRESH/tests/unit/apps_shared/spine_emission/test_spine_emission.py:282-321` — `test_set_run_dir_retargets_phase2_receipts` + `test_target_company_and_role_thread_into_u0_intake`

**Modified**
- `@c:/Git/Agentic-Workflow-FRESH/apps_shared/spine_emission/context.py` — added `EmissionConfig.target_company` + `EmissionConfig.target_role` (Optional); added `GovernedRun.set_run_dir(path)`; threaded both fields into `U0IntakeEnvelope`
- `@c:/Git/Agentic-Workflow-FRESH/apps_rg/__main__.py:190-305` — replaced `from apps_rg.runtime import governed_run` with `from apps_shared.spine_emission import governed_run`; extracted `_apps_rg_emission_config(...)` helper
- `@c:/Git/Agentic-Workflow-FRESH/tools/certification/apps_rg_e2e/_shared.py:125-162` — updated docstring + `governed_run_adapter` signal accepts either `apps_shared.spine_emission` or legacy `apps_rg.runtime`

**Deleted (4 files, ~700 LOC)**
- `apps_rg/runtime/__init__.py`
- `apps_rg/runtime/contracts.py`
- `apps_rg/runtime/context.py`
- `apps_rg/runtime/otel_trace.py`

### Semantic parity verified

- Receipts still land in `artifacts/apps_rg/runs/<ts>/` (late-bound `set_run_dir` works)
- `target_company` + `target_role` still populate `u0_intake_envelope.json`
- All 9 receipt filenames unchanged
- Bundle sha256 changes per run (expected — real wall-clock + new run_id) but structural shape identical
- apps_rg certification unchanged: SPINE_COMPLETE_CERTIFIED (0 violations)

### Plan SSOT

`.windsurf/plans/collapse-apps-rg-runtime-b7e2f5.md` §9.
