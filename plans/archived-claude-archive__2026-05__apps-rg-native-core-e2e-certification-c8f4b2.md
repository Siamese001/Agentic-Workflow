---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-native-core-e2e-certification-c8f4b2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-native-core-e2e-certification-c8f4b2.md'
source_sha256: d6558e6c47c0791dedf6e640d85a07326ee0e06a97b254c6cfd15bee5efcce75
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-native-core-e2e-certification-c8f4b2
plan_type: apps_rg runtime certification (native core proof harness)
plan_status: Completed
parent_plan: ag5-exit-x1-evaluator-wiring-d8e4a2
dod_exempt: false
---

# apps_rg — Native core E2E certification (opt-in proof harness)

**Purpose:** Prove `apps_rg` **binding package data** can traverse the **generic** `agentic_core` binding consumer and the **AG-5** Exit path end-to-end (`normalize → X1 → X2 → exactly one X3`) plus a **RuntimeExhaustBundle-shaped** observer-only L6 handoff — **without** changing `python -m apps_rg`, the default product orchestrator, DOCX, registry, v1 prompts, routing/policy, or L6 calibration.

This completion applies only to the **opt-in certification harness** and fixture package under `tests/_core_contract/fixtures/apps_rg_binding_package/`.

## Waves

| Wave | Scope | Proof |
|------|--------|-------|
| W1 | Harness entry + generic loader | `tests/_apps_contract/test_apps_rg_native_core_e2e_entry.py`, `ops_scripts/ci/prove_apps_rg_native_core_e2e.py` |
| W2 | U0/L1/L0 contract chain | `agentic_core/runtime/bindings/native_contract_chain.py`, `tests/_apps_contract/test_apps_rg_native_core_u0_l1_l0_chain.py` |
| W3 | Evidence / PA / nested refs | `tests/_apps_contract/test_apps_rg_native_core_evidence_pa_l2_chain.py` |
| W4 | AG-5 Exit chain | `agentic_core/runtime/exit/{exit_review_normalizer,x1_checkout_runner,x2_aggregator,x3_emitter}.py`, `tests/_apps_contract/test_apps_rg_native_core_ag5_exit_chain.py` |
| W5 | Runtime exhaust + L6 observer | `tests/_apps_contract/test_apps_rg_native_core_runtime_exhaust_l6_handoff.py` |
| W6 | CI gate + certification bundle | `tests/_apps_contract/test_apps_rg_native_core_e2e_certification.py`, `_core_contract` generic binding + AG-5 tests |

## Definition of Done

All of the following must pass on a clean checkout:

1. `python -m pytest --override-ini="addopts=-q" tests/_core_contract/test_generic_app_binding_loader.py tests/_core_contract/test_no_app_specific_binding_imports.py tests/_core_contract/test_generic_app_binding_profile_validators.py tests/_core_contract/test_generic_app_binding_ref_validators.py tests/_core_contract/test_generic_exit_binding_validator.py tests/_core_contract/test_generic_l6_handoff_validator.py tests/_core_contract/test_generic_app_binding_consumer_ci.py tests/_core_contract/test_generic_app_binding_negative_controls.py tests/_core_contract/test_generic_app_binding_no_domain_semantics.py -v`
2. `python ops_scripts/ci/check_generic_app_binding_consumer.py` → exit 0
3. `python -m pytest --override-ini="addopts=-q" tests/_core_contract/test_ag5_exit_review_packet_normalizer.py tests/_core_contract/test_ag5_x1_checkout_runner.py tests/_core_contract/test_ag5_x1_unknown_na_rules.py tests/_core_contract/test_ag5_x2_aggregator.py tests/_core_contract/test_ag5_x3_disposition.py tests/_core_contract/test_ag5_exit_contract_chain.py tests/_core_contract/test_ag5_no_app_specific_exit_imports.py -v`
4. `python ops_scripts/ci/check_ag5_exit_x1_evaluator_wiring.py` → exit 0
5. `python -m pytest --override-ini="addopts=-q" tests/_apps_contract/test_apps_rg_w1_spine_binding_cli.py tests/_apps_contract/test_apps_rg_w2_static_l1_l0_profiles.py tests/_apps_contract/test_apps_rg_w3_exit_compat_mapper.py -v`
6. `python -m pytest --override-ini="addopts=-q" tests/_apps_contract/test_apps_rg_native_core_e2e_entry.py tests/_apps_contract/test_apps_rg_native_core_u0_l1_l0_chain.py tests/_apps_contract/test_apps_rg_native_core_evidence_pa_l2_chain.py tests/_apps_contract/test_apps_rg_native_core_ag5_exit_chain.py tests/_apps_contract/test_apps_rg_native_core_runtime_exhaust_l6_handoff.py tests/_apps_contract/test_apps_rg_native_core_e2e_certification.py -v`
7. `python ops_scripts/ci/prove_apps_rg_native_core_e2e.py` → exit 0
8. `python ops_scripts/ci/check_plan_definition_of_done.py` → advisory WARN allowed unless `PLAN_DOD_GATE_FAIL_CLOSED=1`
9. `python -m apps_rg --help` → exit 0

## Allowed certification claim

If and only if items 1–7 and 9 above pass:

> apps_rg native core E2E certification proof PASS for the opt-in proof harness.

## Explicit non-claims

- Default `python -m apps_rg` product path migrated to native core.
- Production runtime behavior changed for resume generation.
- L6 calibration complete or authorized to mutate current runtime.
- Repo-wide legacy app coupling eliminated.

## Closeout artifact

`artifacts/governance/plan_closeout_apps-rg-native-core-e2e-certification-c8f4b2.md`

WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=1 note="Generic loader + fixture manifest; bindings tree apps_* import scan clean; apps_rg --help unchanged"
WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=2 note="ValidatedRequest/L1PlanContract/RouteContract derived from binding YAML; single managed route; no cache-final route"
WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=3 note="Evidence policy + PA hash closure + nested ref scan (template paths skipped)"
WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=4 note="AG-5 normalize→X1→X2→X3; deterministic_blocked blocks ALLOW; L6 rescue blocked at emit"
WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=5 note="RuntimeExhaustBundle-shaped proof; L6 approval NONE; no promotion/mutation flags"
WAVE_COMPLETE: plan=apps-rg-native-core-e2e-certification-c8f4b2 wave=6 note="prove_apps_rg_native_core_e2e gate green; plan DoD + disk closeout recorded"
