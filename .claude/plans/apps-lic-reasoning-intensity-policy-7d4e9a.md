---
plan_id: apps-lic-reasoning-intensity-policy-7d4e9a
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

# apps_lic Reasoning Intensity Policy

PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

## Objective

Align `apps_lic` with the requested reasoning-intensity design: scale reasoning by risk, keep default LinkedIn drafting lightweight, use self-consistency only for candidate quality, fail closed or reduce specificity on weak evidence, keep judge roles narrow, and preserve Exit/no-send authority as the final decision point.

## Gap Analysis

1. **No explicit L0 control knobs**
   Current L1/L0 routing emits route family and reason codes, but not an explicit `sc_level`, `reasoning_intensity`, `judge_profile`, `max_candidates`, or fail-closed evidence policy.

2. **Default judge set is too broad**
   QA currently runs seven broad outreach judges by default. The target default is two targeted judges: deterministic schema/policy/no-send plus LinkedIn tone/channel quality.

3. **C0 weakness is not a policy boundary downstream**
   C0 already computes `PASS`, `WEAK`, or `EMPTY`, but L2/QA do not use that support status to prevent specificity escalation or to prove fail-closed behavior.

4. **PA prompt contract lacks reasoning policy**
   PA carries output format and governance text, but the selected SC/R-level and judge profile are not packed into the prompt artifact or component hashes.

5. **No candidate-count/SC E2E proof**
   Existing AIG E2E tests prove target category routing and high-temperature one-shot behavior, but not SC/R-level defaults, escalation, judge-count bounds, or weak-evidence behavior.

6. **Repair pass is implicit**
   HOP6 validation and HOP7 gate behavior exist, but the default `SC-1` "one draft plus one validation/repair pass" policy is not visible as a contract.

## Implementation Plan

### W1 - App-Owned Reasoning Policy

- Add `apps_lic/policy/reasoning_intensity.py`.
- Define supported policy levels:
  - `SC-0` / `R0_MINIMAL`: deterministic/generic low-risk, one-shot.
  - `SC-1` / `R1_STANDARD`: default, one draft plus validation/repair pass.
  - `SC-2` / `R2_DELIBERATE`: named recruiter/company/role, compare/select policy surface.
  - `SC-3` / `R3_STRICT`: executive/high-stakes/sensitive/claim-heavy cases.
- Keep default policy exactly:
  - `sc_level=SC-1`
  - `reasoning_intensity=R1_STANDARD`
  - `judge_profile=normal_default`
  - `judges=[deterministic_schema_policy_no_send_judge, linkedin_tone_channel_quality_judge]`
  - `max_candidates=1`
  - `validation_repair_passes=1`
  - `fail_closed_on_empty_evidence=true`
  - `no_send_authority=true`

### W2 - Thread Policy Through the Spine

- L1 estimates ambiguity/risk from lead profile, campaign objective, personalization, and send/sensitive/metric language.
- L0 records the selected controls in route reason codes and audit refs without changing `RouteContract`.
- C0 support status remains authoritative; weak/empty evidence never escalates SC.
- PA packs the selected policy into prompt text, slot lineage, and component hashes.
- L2 passes the policy and C0 support status into HOP context and generated draft metadata.
- QA runs only the targeted judges for the selected profile and emits policy proof.
- Manifest exposes reasoning policy and evidence support status for E2E proof.

### W3 - Tests and E2E

- Add focused tests for:
  - default SC-1/R1 policy and two judges;
  - executive/high-stakes escalation to SC-3/R3 and three judges;
  - weak/empty evidence fails closed or reduces specificity, never escalates SC;
  - AIG E2E manifest/draft/QA surfaces carry the reasoning contract;
  - no-send remains true and Exit remains the single X3 authority.
- Run focused apps_lic E2E tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

## Acceptance Criteria

- Default apps_lic path is one candidate with one validation/repair pass and two narrow judges.
- SC-2/SC-3 are selected only by documented risk/escalation triggers.
- C0 `WEAK`/`EMPTY` support does not increase SC and does not authorize unsupported specificity.
- QA output includes `reasoning_policy`, `judge_profile`, `active_judges`, `judge_count`, and targeted judge scores only.
- E2E artifacts show `SC-1`/`R1_STANDARD` for default recruiter flow and `SC-3`/`R3_STRICT` for executive/high-stakes flow.
- Exit/no-send policy remains authoritative: no send, no L4 write, one X3 decision.

## Verification

Planned command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p pytest_timeout tests/apps_lic/test_reasoning_intensity_policy.py tests/apps_lic/test_aig_target_category_e2e.py tests/apps_lic/test_linkedin_qwen_refactor.py tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_runtime_proof_bundle.py
```

## Notes

This plan adds the policy contract, defaults, escalation surfaces, and proof. `max_candidates` now records the selected SC candidate budget; L2 remains a single bounded provider execution packet and returns the selected draft for Exit clearance.

## Completion

Implemented:

- `apps_lic/policy/reasoning_intensity.py` app-owned policy.
- L1/L0 reasoning knobs and reason-code receipts.
- C0 support status preservation through L2/HOP context.
- PA prompt/lineage/component hash policy packing.
- Generation metadata for SC/R-level, candidate budget, selection strategy, and repair pass count.
- Validation fail-closed behavior for `WEAK`/`EMPTY` evidence.
- Targeted QA judge profiles with two-judge default and three-judge strict profile.
- Manifest/FEC summary proof fields.
- Focused E2E tests.

Verification:

```text
28 passed, 11 warnings
```

PLAN_COMPLETE: plan=apps-lic-reasoning-intensity-policy-7d4e9a note="Reasoning-intensity controls, targeted judges, C0 evidence boundary, PA/L2/QA/manifest proof, and E2E tests implemented."
