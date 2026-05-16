## Summary

Adds the generic agentic_core apps_* binding consumer, AG-5 Exit wiring, and an opt-in apps_rg native core E2E certification proof harness.

This PR proves apps_rg can pass through the generic binding consumer and AG-5 Exit chain as an opt-in proof harness while preserving the existing apps_rg product entry.

## Scope

- Generic apps_* binding package loader and validators
- Generic binding conformance CI
- AG-5 ExitReviewPacket -> X1CheckoutResult -> X2AggregationResult -> X3 disposition wiring
- apps_rg native core E2E proof harness
- apps_rg binding/package fixtures and contract tests
- Governance plan closeouts and proof artifacts

## Certification statement

apps_rg native core E2E certification proof PASS for the opt-in proof harness.

## Not claimed

- Default apps_rg product path migration
- Production runtime behavior change
- L6 calibration
- Memory/prompt/policy promotion
- Repo-wide legacy app coupling cleanup
- Live full spine orchestrator replacement

## Validation

Prior certification runs were green before commit, and commit cc529d0ead represents the same tested tree with no subsequent file changes.

Validated gates included:

- generic binding pytest bundle: PASS
- check_generic_app_binding_consumer.py: PASS
- AG-5 pytest bundle: PASS
- check_ag5_exit_x1_evaluator_wiring.py: PASS
- apps_rg W1-W3 spine pytest: PASS
- native-core apps_contract pytest: PASS
- prove_apps_rg_native_core_e2e.py: PASS
- python -m apps_rg --help: PASS

Post-commit smoke:

- python ops_scripts/ci/prove_apps_rg_native_core_e2e.py: PASS (exit 0; output includes `[APPS-RG-NATIVE-CORE-E2E] OK`)

## Commit

cc529d0ead
