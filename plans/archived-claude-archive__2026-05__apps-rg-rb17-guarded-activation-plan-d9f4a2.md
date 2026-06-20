---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-rb17-guarded-activation-plan-d9f4a2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-rb17-guarded-activation-plan-d9f4a2.md'
source_sha256: a43e042bb3e76c769f1e75233122e1cd774e0e269064b07d5c23dad4e10e1aaa
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps-rg-rb17-guarded-activation-plan-d9f4a2

## Purpose

Create the explicit activation decision framework for apps_rg managed workflow routing. This is a PLANNING and CONTROLLED-READINESS wave — not an activation wave.

**CRITICAL**: RB17 does NOT activate production. No live providers are enabled globally. No provider_mode changes from stub_only. Rollback controls remain in place. All GateMesh, Exit, L6, UWG, and L4 write controls are preserved.

## Context

- RB16 is complete: Boundary drift fixed, executive_positioning now config-driven, 157 tests passing
- Route status: `registered_not_active`
- Default activation mode: `disabled`
- Default provider mode: `stub_only`
- 21 receipts present and verified

## Wave Structure

| Phase ID | Title | Scope | Status |
|----------|-------|-------|--------|
| P1 | Activation Decision Matrix | 5-option decision framework | ✅ DONE |
| P2 | Guarded Rollout Profile | Template profile (not activated) | ✅ DONE |
| P3 | Rollback Procedure | 5-scenario rollback guide | ✅ DONE |
| P4 | Operator Checklist | 11-item verification checklist | ✅ DONE |
| P5 | Risk Register | 11-risk catalog with mitigations | ✅ DONE |
| P6 | Pre-Activation Tests | 25 new tests, 192 total | ✅ DONE |
| P7 | Activation Receipt | RB17 completion receipt | ✅ DONE |

## Files In Scope

**Created:**
- `artifacts/apps_rg/apps_rg_rb17_activation_decision_matrix.md`
- `apps_rg/config/domain_contract/activation_profile.resume_generation.guarded.v1.json`
- `artifacts/apps_rg/apps_rg_rb17_rollback_procedure.md`
- `artifacts/apps_rg/apps_rg_rb17_operator_activation_checklist.md`
- `artifacts/apps_rg/apps_rg_rb17_activation_risk_register.md`
- `tests/_apps_contract/test_apps_rg_rb17_guarded_activation_plan.py`
- `artifacts/apps_rg/apps_rg_rb17_guarded_activation_plan_receipt.json`

**Modified:**
- None (RB17 is pure planning — no state changes)

## Definition of Done

| ID | Criterion | Status |
|----|-----------|--------|
| DoD-1 | Activation decision matrix with Options A-E created | ✅ |
| DoD-2 | Guarded rollout profile template exists (unactivated) | ✅ |
| DoD-3 | Rollback procedure with 5 scenarios documented | ✅ |
| DoD-4 | Operator checklist with 11 verification items created | ✅ |
| DoD-5 | Risk register with 11 risks cataloged | ✅ |
| DoD-6 | 25 RB17-specific tests pass | ✅ |
| DoD-7 | 192 total tests pass (0 failed) | ✅ |
| DoD-8 | Route remains `registered_not_active` | ✅ |
| DoD-9 | Activation mode remains `disabled` | ✅ |
| DoD-10 | Provider mode remains `stub_only` | ✅ |
| DoD-11 | Receipt created and validated | ✅ |

## Verification

**Test Commands:**
```bash
pytest tests/_apps_contract/test_apps_rg_rb17_guarded_activation_plan.py -v
pytest tests/_apps_contract/test_apps_rg_guarded_activation_readiness.py -v
pytest tests/_apps_contract/test_apps_rg_full_spine_stubbed_e2e.py -v
pytest tests/_apps_contract/test_apps_rg_w11_final_certification.py -v
pytest tests/_apps_contract/test_apps_rg_quality_parity.py -v
pytest tests/_apps_contract/test_apps_rg_llm_judge_gateway.py -v
```

**Results:** 192 tests, 191 passed, 0 failed, 1 skipped

## Acceptance

- [x] RB17 produces activation plan artifacts
- [x] No production activation performed
- [x] route_registry.yaml remains `registered_not_active`
- [x] Default activation mode remains `disabled`
- [x] Default provider mode remains `stub_only`
- [x] Guarded activation profile exists (template)
- [x] Rollback procedure exists
- [x] Operator checklist exists
- [x] Risk register exists
- [x] All tests pass

## Non-Goals

- Actual route activation (deferred to future wave)
- Provider_mode escalation to `live_allowed` (requires separate approval)
- Production customer exposure (blocked until security/cost review)
- Removal of existing safeguards

## Next Wave

**RB18 (or later, separate approval):** Controlled test activation or production readiness certification

**Prerequisites for activation:**
1. Explicit operator decision from activation decision matrix
2. All 11 operator checklist items verified
3. Risk register reviewed and accepted
4. Rollback procedure tested
5. Guarded profile populated with non-null values
6. Receipts RB12-RB17 all present and valid
