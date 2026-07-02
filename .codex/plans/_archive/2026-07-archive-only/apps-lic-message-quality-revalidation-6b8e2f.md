---
plan_id: apps-lic-message-quality-revalidation-6b8e2f
plan_type: quality-hardening
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
created: 2026-06-08
owner: Codex
---

# apps_lic Message Quality Revalidation

PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

## Objective

Revalidate the apps_lic outreach generation path so AIG LinkedIn messages are routed to the right target category, generated with a high-temperature Qwen/vLLM contract, judged for originality and recipient fit, and blocked when they read like generic candidate outreach.

## Gaps Found

1. Quality metadata was not explicit enough: Qwen temperature, top_p, generation attempts, self-consistency sample count, and X1-X3 retry policy were not surfaced in the QA/proof contract.
2. HOP6 validation caught basic structure but did not reject common bland outreach phrases like "I noticed your role", "potential synergies", or generic alignment claims.
3. QA reporting did not run the calibrated outreach judges as a first-class scorecard, so message distinctiveness was not visible in testable output.
4. The target-profile E2E harness proved routing but did not yet assert high-temperature generation settings, one-shot attempts, or category-specific message texture.
5. Live Qwen output could still be weak or unavailable; the runtime needed to fail closed instead of silently authorizing a generic fallback.

## Implemented Plan

### W1 - Generation Contract

- Set apps_lic Qwen defaults to `temperature=0.82` and `top_p=0.92`.
- Kept generation attempts to `1` and max generation attempts to `1`.
- Made provider settings visible on every draft: `generation_temperature`, `top_p`, `attempts`, and `max_generation_attempts`.
- Tightened the live Qwen prompt to require JSON-only LinkedIn output, an AIG-specific operating insight, one Amit proof point, no invented metrics, and no generic phrases.

### W2 - Validation and Judges

- Added validation gates for generic outreach anti-patterns, AIG operating insight, candidate proof, low-friction ask, unsupported claims, length, markdown links, and em dash usage.
- Added unverified metric blocking for candidate claims that attach percentage outcomes to unsupported verbs.
- Wired deterministic outreach judges into QA reporting: response likelihood, brand voice, personalization, proof appropriateness, asymmetric insight, ask friction, and anti-pattern cleanliness.
- Added `quality_contract` to QA output:
  - `self_consistency_samples=1`
  - `generation_attempts=1`
  - `max_generation_attempts=1`
  - `x1_x2_x3_exit_retries=0`
  - `retry_policy=one_shot_fail_closed`

### W3 - AIG E2E Proof

- Added AIG public-profile cases for executive, senior talent acquisition, and recruiter categories.
- Proved routing:
  - Scott Hallworth -> `EXECUTIVE`
  - Daisuke Hayashi -> `SENIOR_TA`
  - Nina K. -> `RECRUITER`
- Added assertions that messages contain category-specific texture instead of generic filler:
  - executive: operating-model rewrite
  - senior TA: not slideware
  - recruiter: production AI
- Verified deterministic proof artifacts pass as `X3D` with outcome authorization.
- Verified live Qwen weak/unavailable output is denied as `X3A` rather than authorized.

## SC, Paths, and Retry Contract

| Item | Current Contract | Rationale |
|---|---|---|
| Self-consistency samples | `1` | One canonical draft is judged and either authorized or denied; no validator gaming through repeated samples. |
| Generation path | `U0 -> L1 -> L0 -> C0 -> PA -> L3 -> L2 -> EXIT` | Existing canonical apps_lic spine remains the only live path. |
| Provider path | Qwen/vLLM primary, explicit test stub only under `APPS_LIC_TEST_PROVIDER_STUB=1` | Production does not silently fall back to generic scaffold text. |
| X1-X3 retries | `0` | Exit gates are one-shot and fail closed. |
| Retry policy | `one_shot_fail_closed` | Weak, empty, unsupported, or generic output is denied instead of retried around validators. |

## Verification

Command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p pytest_timeout tests/apps_lic/test_aig_target_category_e2e.py tests/apps_lic/test_linkedin_qwen_refactor.py tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_runtime_proof_bundle.py
```

Result:

```text
21 passed, 9 warnings
```

## Remaining Risk

Live Qwen can still produce weak copy under high temperature. That is acceptable for this wave because the runtime now denies that output. The next improvement, if desired, should be a separate prompt-eval/calibration plan that measures live Qwen pass rate across a larger AIG and non-AIG contact set without changing the one-shot fail-closed exit policy.

PLAN_COMPLETE: plan=apps-lic-message-quality-revalidation-6b8e2f note="Judges, quality gates, high-temperature provider metadata, category-specific AIG E2E tests, and one-shot X1-X3 fail-closed contract implemented and verified."
