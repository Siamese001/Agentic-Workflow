# apps_lic End-to-End Quality Governance Remediation Plan

Created: 2026-06-09
Worktree: `C:\Git\Agentic-Workflow-apps_lic`
Status: In Progress

## Objective

Review apps_lic end to end as an agentic engineer and close the policy, duplication, and bottleneck gaps that allow live harness passes while leaving recipient policy, route policy, judge thresholds, and repair behavior harder to reason about than they should be.

## Evidence Snapshot

- ADG health: SQLite SSOT healthy, Redis cache healthy, cache-hit capable, snapshot `06082026_1758`.
- Latest live harness: 12/12 clear, all `INMAIL` / `linkedin_inmail`, live Qwen/vLLM required, live Claude X1D enabled.
- Structural hotspots:
  - `apps_lic/engines/validation_exit.py`: ADG apps_lic risk hotspot #1; 25 debt findings; fan-out 42.
  - `apps_lic/runtime/dispatch/canonical_dispatch.py`: ADG apps_lic chokepoint #1; fan-in 43, fan-out 45; `run_canonical_apps_lic_spine` is 587 lines.
  - `apps_lic/engines/whole_message_generation.py`: ADG chokepoint; fan-in 56, fan-out 43.
  - `apps_lic/engines/generation_engine.py`: 2,078 lines, 69 functions, seven functions >=80 lines.
- Runtime coverage note: ADG static coverage tables are empty for runtime coverage; use runtime harness, test reachability, and targeted tests rather than static `coverage_pct`.

## Findings

### F1. X1D threshold policy is inconsistent and under-strict for C-level

`validation_exit.py` hardcodes:

- `ceo_attention_originality_x1d`: `0.80`
- `ceo_evidence_overclaim_risk_x1d`: `0.80`
- `evidence_claim_support_x1d`: `0.86`
- `linkedin_tone_non_generic_x1d`: `0.84`
- `linkedin_tone_channel_quality_x1d`: `0.82`

This makes C-level clear at a lower bar than recruiter evidence support. The same values also exist in `apps_lic/config/domain_contract/validation_exit.v1.yaml`, so threshold policy is duplicated between config and code.

Impact: C-level rows can clear at 8.2/10 while recruiter rows require 8.6/10. That is backwards for an executive outreach product.

### F2. Requested slot, derived LIC class, mapped archetype, and X1D policy are split decisions

The harness has a requested slot and expected archetype, but runtime derives the LIC class independently. Two latest rows requested as `Executive` derive as `HIRING_MANAGER`, map to `EXECUTIVE`, and clear with `X1D_NOT_REQUIRED` because the X1D policy only covers `HIRING_MANAGER + role_specific`, not `HIRING_MANAGER + trigger_based_insight`.

Impact: The product can say "Executive archetype passed" while the validation path treats it as a class that needs no judge for that message type.

### F3. Route policy has multiple authorities

Route decisions appear in all of these surfaces:

- `apps_lic/types/linkedin_route_envelope.py`
- `apps_lic/engines/HOP4RoutingAgent.py`
- `apps_lic/types/k1_router_types.py`
- `apps_lic/types/message_route_types.py`
- duplicated YAML: `apps_lic/policy/pre_flight_policy.yaml` and `apps_lic/validators/policy/pre_flight_policy.yaml`
- `apps_lic/runtime/dispatch/canonical_dispatch.py`

Impact: InMail behavior can be fixed in one canonical path while legacy/HOP paths continue to encode different route defaults, candidate counts, and temperatures.

### F4. Prompt/template policy is scattered across config and imperative code

The four intended archetypes exist in `recipient_archetype_mapping.py`, but company-specific message bodies and repair templates are hardcoded in `generation_engine.py` and `x1d_judge_feedback_regeneration.py`.

Impact: Quality improvements become company-specific patches. This passed the latest harness but does not generalize to new companies, new JDs, or the 30-contact run.

### F5. Harness acceptance can hide X1D-not-required clearances

`_quality_violations()` permits `X1D_NOT_REQUIRED` for cleared rows. For low-risk paths that is fine. For executive archetype or trigger-based insight rows, it is too permissive unless policy explicitly says X2-only is acceptable.

Impact: 12/12 can pass while two executive-archetype trigger rows have no live LLM judge receipt.

### F6. Score reporting collapses heterogeneous score bases

Rows use `gate_score_basis`:

- `min_required_live_x1d_judge` when X1D exists.
- `x2_applicable_gate_pass_ratio` when X1D is not required.

Impact: A `10.0` row without X1D is not comparable to a `9.1` row judged by live Claude. The report table should make this visually impossible to miss.

### F7. Repair loop is bounded but too semantically coupled to current companies

The repair loop now works, but it contains company-specific fallbacks for Citi and Neo4j recruiter failures, plus AIG-specific texture guards.

Impact: The repair loop is reliable for the tested matrix but still fragile for JD/briefing companies outside AIG/Citi/Neo4j.

### F8. Large modules create review and change bottlenecks

Top local code-size bottlenecks:

- `generation_engine.py`: 2,078 lines; `_draft_from_model_text`, `_try_qwen_generation`, `_stub_message_text`, and `_build_judge_feedback_repair_prompt` are all large.
- `canonical_dispatch.py`: 1,435 lines; `run_canonical_apps_lic_spine` is 587 lines.
- `validation_exit.py`: 1,169 lines; mixes X2 gates, X1D profile registry, X1D evaluation, and Exit disposition.
- `runtime_proof_bundle.py`: 1,366 lines; `build_runtime_proof_bundle` is 307 lines.

Impact: Policy changes require touching broad, high-blast-radius files.

## Remediation Waves

### W0. Policy Ledger and Failing Characterization

Create failing characterization tests before changing behavior:

- C-level X1D thresholds must be >= evidence threshold.
- Executive archetype rows must require X1D unless an explicit policy profile says X2-only.
- HIRING_MANAGER + trigger_based_insight must not silently clear under executive archetype without X1D.
- Harness report must distinguish X1D score from X2 score.

Acceptance:

- New tests fail on current code for threshold and X1D-not-required policy gaps.
- No harness code changes yet.

Status: Completed 2026-06-09.

Implementation:

- Added `tests/apps_lic/test_apps_lic_quality_governance_w0.py`.
- Pinned current policy gaps as strict expected failures:
  - C-level X1D thresholds are lower than evidence-support threshold.
  - `HIRING_MANAGER + trigger_based_insight` currently has no live judge requirement.
  - `EXECUTIVE + trigger_based_insight + commercial proof` currently omits evidence X1D.
  - Matrix acceptance currently allows executive-archetype rows to clear as `X1D_NOT_REQUIRED`.
- Added a passing score-basis test proving the harness can distinguish live X1D min-judge scores from X2 pass-ratio scores.

Verification:

- `python -m pytest tests/apps_lic/test_apps_lic_quality_governance_w0.py -q`
  - Result: `1 passed, 4 xfailed`.
- `python -m pytest tests/apps_lic/test_apps_lic_quality_governance_w0.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py -q`
  - Result: `20 passed, 4 xfailed`.

### W1. Centralize X1D Judge Profile Policy

Move judge profile definitions out of hardcoded `_judge_profile_for_id()` and into a single typed policy loader backed by `validation_exit.v1.yaml` or a small dedicated `x1d_judge_profiles.v1.yaml`.

Recommended threshold policy:

- `ceo_attention_originality_x1d`: 0.88
- `ceo_evidence_overclaim_risk_x1d`: 0.86
- `evidence_claim_support_x1d`: 0.86
- `linkedin_tone_non_generic_x1d`: 0.84
- `linkedin_tone_channel_quality_x1d`: 0.82

Acceptance:

- Code and YAML cannot drift; test asserts loaded profile thresholds match config.
- C-level latest harness rows at 8.2 become review-required until repaired.

Status: Completed 2026-06-09.

Implementation:

- Added `rubric_id` to each `x1d.rubric_profiles` entry in `apps_lic/config/domain_contract/validation_exit.v1.yaml`.
- Centralized runtime judge profile construction behind `x1d_judge_profile_policy()` in `apps_lic/engines/validation_exit.py`.
- Exported `X1DJudgeProfilePolicy` and `x1d_judge_profile_policy` for tests and future policy-profile consumers.
- Set C-level thresholds to:
  - `ceo_attention_originality_x1d`: `0.88`.
  - `ceo_evidence_overclaim_risk_x1d`: `0.86`.
- Converted the W0 C-level threshold characterization from strict expected-fail to passing regression coverage.
- Added a W6 regression proving the runtime loader matches the YAML domain contract for every configured judge profile.

Verification:

- `python -m pytest tests/apps_lic/test_apps_lic_quality_governance_w0.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_x1d_judge_feedback_regeneration.py -q`
  - Result: `39 passed, 1 skipped, 3 xfailed`.
  - Remaining xfails are intentional W0 characterization debt for executive/HIRING_MANAGER X1D-not-required policy gaps addressed in later waves.

### W2. Introduce Recipient Policy Profile

Replace separate slot/class/archetype/judge decisions with one derived `RecipientPolicyProfile` receipt:

- requested slot
- actual LinkedIn title
- derived LIC class
- mapped prompt archetype
- message type
- required route family
- required X1D judge profile IDs
- minimum score profile
- reason codes

Acceptance:

- Harness rows display policy profile ID.
- Executive-archetype rows cannot hide `HIRING_MANAGER` derived class.
- `requested_slot != derived_class` is not automatically a failure, but must be explained by policy reason code.

Status: Completed 2026-06-09.

Implementation:

- Added `apps_lic/types/recipient_policy_profile.py` with a typed `RecipientPolicyProfile` receipt and deterministic `build_recipient_policy_profile()` helper.
- The receipt captures requested slot, requested-slot archetype, actual LinkedIn title, derived LIC class, mapped prompt archetype, expected prompt archetype, message type, required route family, required X1D judge profile IDs, X1D thresholds, minimum score profile, and reason codes.
- Wired `scripts/apps_lic/run_post_w7_live_12_archetype_matrix.py` so each row now emits:
  - `recipient_policy_profile_id`.
  - nested `recipient_policy_profile`.
  - `recipient_policy_reason_codes`.
  - `minimum_score_profile_id`.
  - `minimum_x1d_threshold`.
- Updated `full_messages.md` report output to display the policy profile ID and reason codes next to the full message.
- Kept W2 observational only: executive-archetype rows with no X1D are now visible via `executive_archetype_has_no_required_x1d_current_policy`, but W2 does not make that a hard acceptance failure. That remains W3.

Verification:

- `python -m pytest tests/apps_lic/test_w2_recipient_policy_profile.py tests/apps_lic/test_recipient_archetype_mapping.py tests/apps_lic/test_apps_lic_quality_governance_w0.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py -q`
  - Result: `38 passed, 3 xfailed`.
  - Remaining xfails are intentional W0 debt for X1D-required policy expansion planned in W3.

### W3. Raise X1D Coverage for Executive/Strategic Trigger Rows

Update `required_x1d_judge_ids_for_context()` so these require X1D:

- `C_LEVEL` / `CEO` / `CTO`: two executive judges for all message types.
- `EXECUTIVE` / `VP_ENG`: tone judge plus evidence judge when trigger-based or technical proof is used.
- `HIRING_MANAGER` mapped to `EXECUTIVE`: at least tone/non-generic plus evidence when trigger-based insight or technical proof is used.

Acceptance:

- The two current `HIRING_MANAGER -> EXECUTIVE` rows no longer clear as `X1D_NOT_REQUIRED`.
- 12-row harness still passes only after live judge receipts exist or messages are repaired.

Status: Completed 2026-06-09.

Implementation:

- Updated `required_x1d_judge_ids_for_context()` in `apps_lic/engines/validation_exit.py`:
  - `CEO`, `C_LEVEL`, and `CTO` now require `ceo_attention_originality_x1d` plus `ceo_evidence_overclaim_risk_x1d` for all message types.
  - `EXECUTIVE` and `VP_ENG` trigger-based, JD-backed, or technical-proof paths now require `linkedin_tone_channel_quality_x1d` plus `evidence_claim_support_x1d`.
  - `HIRING_MANAGER` trigger-based or technical-proof paths now require `evidence_claim_support_x1d` plus `linkedin_tone_non_generic_x1d`.
- Updated `apps_lic/config/domain_contract/validation_exit.v1.yaml` so the domain-contract risk matrix matches the runtime policy.
- Hardened `_matrix_violations()` in `scripts/apps_lic/run_post_w7_live_12_archetype_matrix.py` so cleared executive/C-level archetype rows with `X1D_NOT_REQUIRED` are quality violations.
- Converted the remaining W0 X1D policy expected-fail tests into passing regression coverage.

Verification:

- `python -m pytest tests/apps_lic/test_apps_lic_quality_governance_w0.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w2_recipient_policy_profile.py -q`
  - Result: `29 passed`.
- `python -m pytest tests/apps_lic/test_post_w7_live_15_contact_company_validation.py::test_post_w7_live_sources_are_5_per_company_and_targeting_files_exist tests/apps_lic/test_w2_recipient_policy_profile.py tests/apps_lic/test_apps_lic_quality_governance_w0.py -q`
  - Result: `10 passed`.
- Attempted broader live-runner surface command:
  - `python -m pytest tests/apps_lic/test_post_w7_live_15_contact_company_validation.py tests/apps_lic/test_w2_recipient_policy_profile.py tests/apps_lic/test_apps_lic_quality_governance_w0.py -q`
  - Result: timed out after ~124 seconds because it includes the live 15-contact runner path. This is not counted as W3 deterministic policy verification; rerun as a live canary when provider/runtime budget is available.

### W4. Route Policy SSOT

Make `linkedin_route_envelope.py` the route SSOT and adapt legacy HOP/K1/message-route surfaces to call it or mark them deprecated.

Work:

- Deduplicate `pre_flight_policy.yaml` under one location.
- Add drift test comparing legacy adapters against the route envelope.
- Ensure explicit `INMAIL` override with `premium_available=false` has a documented policy outcome.

Acceptance:

- One route authority for `INMAIL`, `CONNECTION_REQ`, and connected direct/follow-up behavior.
- Legacy/HOP path parity tests pass or deprecated paths are fenced.

Status: Completed 2026-06-09.

Implementation:

- Kept `apps_lic/types/linkedin_route_envelope.py` as the canonical LinkedIn route resolver.
- Updated `apps_lic/engines/HOP4RoutingAgent.py`:
  - Added pure `resolve_hop4_linkedin_route()` helper that delegates to `resolve_linkedin_route_envelope()`.
  - Replaced HOP4's imperative override/premium route chain with the canonical envelope.
  - Preserved legacy `FOLLOW_UP` output for connected direct drafts by mapping canonical `LINKEDIN_DIRECT` to legacy `FOLLOW_UP`.
  - Attached the canonical `linkedin_route_envelope` packet to HOP4 metadata.
  - Documented explicit `INMAIL` override with `premium_available=false` as an allowed envelope decision instead of a HOP4 premium-mismatch block.
- Added/updated route parity tests:
  - `tests/apps_lic/test_linkedin_route_envelope.py` now verifies explicit InMail override behavior, HOP4 delegation, and legacy `route_types` / `message_route_types` parity for core LinkedIn routes.
  - `tests/apps_lic/test_w4_route_policy_ssot.py` verifies the duplicated `pre_flight_policy.yaml` copies remain byte-identical until fully deduped, and that core route rules match the canonical envelope.

Verification:

- `python -m pytest tests/apps_lic/test_linkedin_route_envelope.py tests/apps_lic/test_w4_route_policy_ssot.py tests/unit/apps_lic/types/test_route_and_archetype_contracts.py -q`
  - Result: `12 passed`.
- `python -m pytest tests/apps_lic/test_linkedin_route_envelope.py tests/apps_lic/test_w4_route_policy_ssot.py tests/apps_lic/test_w4_candidate_batch_wireup.py tests/apps_lic/test_w6_whole_message_generation.py -q`
  - Result: `27 passed`.

### W5. Template and Length Policy SSOT

Move archetype templates, length budgets, and route-aware subject rules into a typed config object:

- four archetypes: Recruiter/TA, Senior TA, Executive, C-level including CEO
- per-route budgets: InMail, connection request, connected direct/follow-up
- subject rules by route
- CTA style by archetype

Acceptance:

- `whole_message_generation.py`, `pa_binding.py`, and `generation_engine.py` read the same policy object.
- No hardcoded archetype length bands remain in generation paths.

Status: Completed 2026-06-09.

Implementation:

- Added typed template/length SSOT objects in `apps_lic/types/recipient_archetype_mapping.py`:
  - `TemplateLengthPolicy`.
  - `RecipientTemplatePolicy`.
  - `resolve_recipient_template_policy()`.
- The shared policy now owns:
  - four prompt archetypes: Recruiter/TA, Senior TA, Executive, C-level including CEO/CTO.
  - route/message length budgets for InMail, connection request, and standard LinkedIn draft/follow-up paths.
  - subject-line requirement by route.
  - signature requirement by route.
  - CTA guidance by archetype.
- Updated `apps_lic/engines/whole_message_generation.py` so `resolve_length_budget()` materializes its runtime `LengthBudget` from `resolve_recipient_template_policy()` instead of a local hardcoded branch table.
- Extended `LengthBudget.to_packet()` with `channel`, `route_family`, `subject_required`, `signature_required`, and `cta_style`.
- Updated `apps_lic/runtime/bindings/pa_binding.py` so prompt assembly reads the shared template policy and merges it with any supplied C0.3 length budget.
- Updated `apps_lic/engines/generation_engine.py` so subject/channel decisions prefer explicit `subject_required` and `channel` from the shared length-budget packet, with legacy inference retained as fallback.
- Added W5 regression coverage:
  - `tests/apps_lic/test_w5_template_length_policy_ssot.py`.
  - expanded `tests/apps_lic/test_recipient_archetype_mapping.py`.
  - expanded `tests/apps_lic/test_w6_whole_message_generation.py`.
  - expanded `tests/apps_lic/test_w5_apps_lic_c0_pa.py`.

Verification:

- `python -m pytest tests/apps_lic/test_recipient_archetype_mapping.py tests/apps_lic/test_w5_template_length_policy_ssot.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w5_apps_lic_c0_pa.py -q`
  - First run found a missing `CHANNEL_LINKEDIN_INMAIL` import after narrowing imports.
  - After fix: `120 passed`.
- `python -m pytest tests/apps_lic/test_linkedin_route_envelope.py tests/apps_lic/test_w4_route_policy_ssot.py tests/apps_lic/test_w5_template_length_policy_ssot.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w2_recipient_policy_profile.py -q`
  - Result: `29 passed`.

### W6. Replace Company-Specific Repair Templates With Evidence-Driven Repair Planner

Convert the current deterministic repair fallback into a generic planner:

- parse judge issues into repair intents
- choose one evidence bridge sentence from approved proof and company/JD facts
- enforce recipient altitude and CTA style from the policy profile
- ban cross-company texture through validation profiles

Acceptance:

- Citi/Neo4j current fixes still pass.
- Add a fourth unseen company fixture; repair cannot rely on hardcoded AIG/Citi/Neo4j strings.

Status: Completed 2026-06-09.

RCA:

- `x1d_judge_feedback_regeneration.py` had a bounded loop, but its repair fallback was still semantically coupled to the latest harness companies:
  - Citi recruiter failures received a full hardcoded Citi message.
  - Neo4j recruiter failures received a full hardcoded Neo4j message.
  - AIG/claims/underwriting and graph-context CTA repairs were handled by company-specific branches.
- That meant the harness could pass while the repair mechanism did not prove generalization to a fourth company, new JD facts, or briefing-only company evidence.
- W6 verification also exposed a route/template policy gap from W5: recruiter and Senior TA `trigger_based_insight` InMail budgets were missing, causing canonical non-AIG trigger-backed runs to crash before validation.

Implementation:

- Added an internal `X1DFeedbackRepairPlan` in `apps_lic/engines/x1d_judge_feedback_regeneration.py`.
- Replaced company-specific repair templates with a generic repair planner that:
  - parses judge feedback into repair intents such as role-fit bridge, governed platform controls, redundant bridge removal, scale/outcome, CTA, and unsupported-claim cleanup.
  - builds one evidence bridge sentence from approved proof IDs plus company/JD fields.
  - derives archetype, altitude, CTA style, channel, and message-type policy from `resolve_recipient_template_policy()`.
  - removes cross-company texture before and after repair insertion.
- Kept proof-claim accounting bounded to allowed proof IDs, so generated repairs can add `sp_agentic_platform`, `sp_runtime_reliability`, or `sp_platform_commercialization` only when the request proof packet permits them.
- Added a W6 unseen-company regression using Waystar to prove the repair path removes borrowed AIG/Neo4j texture and still produces a recruiter-safe evidence bridge.
- Updated Citi and Neo4j repair tests to assert invariant behavior rather than hardcoded company-specific rescue sentences.
- Added missing recruiter and Senior TA `trigger_based_insight` InMail length policies in `apps_lic/types/recipient_archetype_mapping.py`.
- Added a regression proving those recruiting trigger InMail budgets resolve with subject-line requirements.

Verification:

- `python -m pytest tests/apps_lic/test_x1d_judge_feedback_regeneration.py -q`
  - Result: `8 passed`.
- `python -m pytest tests/apps_lic/test_recipient_archetype_mapping.py tests/apps_lic/test_w5_template_length_policy_ssot.py -q`
  - Result: `16 passed`.
- First adjacent profile run:
  - `python -m pytest tests/apps_lic/test_w7_profile_scoping.py -q`
  - Result: `7 passed, 2 failed`.
  - Failure: missing `('RECRUITER', 'trigger_based_insight')` InMail policy, fixed in W6 because it blocks canonical trigger-backed InMail validation.
- After policy fix:
  - `python -m pytest tests/apps_lic/test_w7_profile_scoping.py -q`
  - Result: `9 passed`.
- Final focused regression:
  - `python -m pytest tests/apps_lic/test_x1d_judge_feedback_regeneration.py tests/apps_lic/test_recipient_archetype_mapping.py tests/apps_lic/test_w5_template_length_policy_ssot.py -q`
  - Result: `25 passed`.

### W7. Split High-Blast-Radius Modules

Refactor without behavior change:

- `generation_engine.py`
  - provider transport
  - JSON parsing/sanitization
  - deterministic fallback
  - subject policy
  - company evidence repair
- `validation_exit.py`
  - X2 gates
  - X1D profile registry
  - X1D evaluator
  - Exit disposition
- `canonical_dispatch.py`
  - ingress builder
  - stage runner
  - artifact writer
  - harness manifest bridge

Acceptance:

- No behavior drift in targeted tests.
- ADG chokepoint score for canonical dispatch and validation_exit decreases in next graph regen.

Status: Completed 2026-06-09.

Implementation:

- Split generation subject/channel policy out of `apps_lic/engines/generation_engine.py` into `apps_lic/engines/generation_subject_policy.py`.
  - `generation_engine._subject_required()` and `_channel_from_length_budget()` remain compatibility wrappers.
  - Subject/channel policy can now be tested without importing provider transport, prompt assembly, deterministic fallback, or parsing code.
- Split X1D judge profile and recipient-risk policy out of `apps_lic/engines/validation_exit.py` into `apps_lic/engines/x1d_judge_policy.py`.
  - `validation_exit` keeps compatibility exports for `x1d_judge_profile_policy`, `required_x1d_judge_ids_for_context`, judge IDs, model/provider constants, and modifier constants.
  - `validation_exit.py` now focuses more tightly on X2/X1D result normalization and Exit disposition.
- Split canonical manifest field shaping out of `apps_lic/runtime/dispatch/canonical_dispatch.py` into `apps_lic/runtime/dispatch/canonical_manifest_fields.py`.
  - `_w4_manifest_fields` and `_w5_manifest_fields` remain compatibility aliases in the dispatcher.
  - Final and blocked manifests still use the same field packets.
- Added `tests/apps_lic/test_w7_hotspot_policy_extraction.py` to prove the extracted modules are the active owners while legacy compatibility surfaces preserve behavior.

Verification:

- Syntax parse check:
  - `python -c "... ast.parse ..."`
  - Result: parsed 6 touched production files.
- Focused W7 policy/exit/repair regression:
  - `python -m pytest tests/apps_lic/test_w7_hotspot_policy_extraction.py tests/apps_lic/test_w5_template_length_policy_ssot.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_x1d_judge_feedback_regeneration.py tests/apps_lic/test_recipient_archetype_mapping.py tests/apps_lic/test_w7_profile_scoping.py -q`
  - Result: `57 passed`.
- Canonical dispatcher smoke/wireup regression:
  - `python -m pytest tests/apps_lic/test_w7_hotspot_policy_extraction.py tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_w5_validation_exit_canonical_wireup.py -q`
  - Result: `12 passed`.

Residual:

- W7 intentionally did not move provider transport, JSON parsing, deterministic fallback, or the full canonical artifact-writer block. Those are now safer W9/W10 candidates after this policy/manifest split because the externally visible compatibility surfaces are pinned by tests.
- ADG chokepoint-score reduction must be measured on the next graph regeneration; this wave added the structural split and deterministic verification, not a fresh ADG regen.

### W8. Harness Honesty Upgrade

Update `full_messages.md` and `rows.json`:

- show `Score Type`: live X1D min score vs X2 pass ratio
- show every judge threshold and pass/fail
- flag `X1D_NOT_REQUIRED` as acceptable only when policy profile says so
- add `policy_profile_id`
- add `threshold_profile_id`

Acceptance:

- A reader can tell which rows were live-judged without inspecting JSON.
- No row with executive archetype can pass without judge evidence unless explicitly waived.

Status: Completed 2026-06-09.

Implementation:

- Updated `scripts/apps_lic/run_post_w7_live_12_archetype_matrix.py` rows/report output:
  - Added explicit `score_type`: `Live X1D min score` vs `X2 pass ratio`.
  - Added `policy_profile_id` as a reader/report alias for the recipient policy profile.
  - Added `threshold_profile_id`: `atp::apps_lic::outreach_message::v1`.
  - Added `x1d_not_required_policy_acceptable`.
  - Added `x1d_policy_clearance`.
- Updated `full_messages.md` summary table:
  - Shows `Policy Profile`.
  - Shows `Threshold Profile`.
  - Shows `Score Type`.
  - Shows gate score and threshold side by side.
  - Shows X1D policy clearance.
- Updated `full_messages.md` judge details:
  - Live-judged rows render a judge table with judge ID, score/10, threshold/10, and pass/fail.
  - X2-only rows explicitly render `none_required_by_policy` rather than silently looking equivalent to live judged rows.
- Hardened `X1D_NOT_REQUIRED` acceptability so executive/C-level archetype clears remain violations unless policy reason codes include an explicit waiver.
- Added W8 regression coverage in `tests/apps_lic/test_w2_recipient_policy_profile.py`.

Verification:

- `python -m pytest tests/apps_lic/test_w2_recipient_policy_profile.py tests/apps_lic/test_apps_lic_quality_governance_w0.py -q`
  - Result: `10 passed`.
- `python -m pytest tests/apps_lic/test_w2_recipient_policy_profile.py tests/apps_lic/test_apps_lic_quality_governance_w0.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py -q`
  - Result: `30 passed`.

### W9. Verification Run

Run in this order:

1. Focused unit tests for policy profile, route envelope, length budget, X1D profile loader.
2. Existing apps_lic targeted regression suite.
3. Live 12-row harness.
4. Live 15-row or 30-row contact harness with all companies and all archetypes.
5. ADG SQLite direct health and Redis cache health.

Acceptance:

- Live harness reports `acceptance_passed=true`.
- No C-level row clears below the new C-level threshold.
- No executive-archetype row clears with `X1D_NOT_REQUIRED` unless explicitly waived by policy.
- Quality violations remain zero.

## Recommended Priority

1. W0-W3 first. These are correctness and governance gaps.
2. W8 next, so the report cannot oversell X2-only rows as equivalent to live X1D rows.
3. W4-W6 after that, to remove route/template/repair drift.
4. W7 last, after behavior is pinned, because it is mostly blast-radius reduction.

## Open Policy Decisions

- Whether C-level threshold should be `0.86` or `0.88`. Recommendation: `0.88` for attention/originality and `0.86` for evidence/overclaim.
- Whether `HIRING_MANAGER -> EXECUTIVE` should use the Executive judge profile or a separate Hiring Manager strategic trigger profile. Recommendation: separate profile if this becomes common; until then use Executive judge requirements when mapped to Executive archetype.
- Whether live harness acceptance should require X1D for every InMail row. Recommendation: no for recruiter/Senior TA low-risk general intro, yes for all executive/C-level and all trigger-based insight rows.
