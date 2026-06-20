---
plan_id: apps-lic-canonical-hardening-wireup-4c9d2a
plan_type: hardening-wireup
status: Not Started
created: 2026-06-08
owner: ChatGPT
scope: apps_lic canonical runtime plan only
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_lic Canonical Hardening Wireup

## Status

PLAN_STATUS: NOT_STARTED  
CURRENT_WAVE: W0  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-06-08

This is a **planning and control artifact only**. It does not approve implementation by itself.

Until explicit implementation approval is given, do not edit runtime files, tests, configs, Chroma/vector data, generated corpora, branch refs, PRs, or deployment settings from this plan alone.

## Objective

Wire the already-present apps_lic hardening modules into the live canonical path so the production route is no longer protected only by inline C0, U0-derived target class, HOP-local validation, generic Exit defaults, or AIG-specific copy gates.

The intended live path after implementation is:

```text
U0 → L1 → L0 → C0 readiness + C0-A recipient classification → C0-B message requirements → C0.3 sender proof graph → PA sealed prompt envelope → L3 → L2 whole-message candidates → apps_lic X2 → required X1D → ExitDispositionReceipt → RuntimeExhaustBundle
```

The hardening target is not “better copy.” The target is **authority correctness**:

- C0, not U0, derives recipient_class.
- C0 readiness, not inline seed presence, decides whether evidence is usable.
- C0.3, not L2 prose, authorizes sender claims.
- apps_lic X2/X1D, not generic hardcoded Exit defaults, clears or blocks the draft.
- Exit emits exactly one disposition.
- No stage silently retrieves, writes, sends, or upgrades weak evidence.

## Current Gap Summary

Prior review found the merged `main` state is a useful intermediate checkpoint, not the completed hardened refactor.

### Good intermediate state already present

- Canonical dispatch exists and routes through U0/L1/L0/C0/PA/L3/L2/Exit.
- Deprecated apps_research/R3R4 research paths fail closed.
- Qwen/vLLM unavailable behavior fails closed instead of silently authorizing generic copy.
- No-send/no-L4-write assertions are present in runtime manifests.
- L3 and L2 carry no-durable-commit authority assertions.
- modules exist for governed opportunity ingestion, recipient classification, sender proof graph, whole-message generation, apps_lic X2/X1D, and Claude X1D adapter.

### Gaps to close

1. **C0 live path is still inline-only.** It can mark support PASS from lead_profile + campaign context, without governed opportunity readiness, freshness, public evidence, vector namespace checks, or contradiction handling.
2. **recipient_class is still effectively U0-controlled.** PA/L2 can derive from lead_profile.seniority_class and fall back to RECRUITER.
3. **C0.3 sender proof graph is not on the canonical prompt path.** L2 claims are not forced to map to approved proof IDs.
4. **apps_lic W7/X2/X1D exists but is not wired into canonical dispatch.** Generic Exit still sees hardcoded groundedness/c0_status defaults.
5. **Claude X1D adapter exists but is not required in live clearance.** CEO/C-level/two-judge policy is not live-enforced.
6. **SC-2/SC-3 candidate counts are metadata, not inspectable candidate batches.**
7. **AIG-specific operating-insight gates are global in HOP validation.** They should become profile/fixture-specific, not default apps_lic behavior.
8. **Terminal R5 denial is not yet a full ExitDispositionReceipt-compatible path.**

## Non-Bypass Laws

These are implementation blockers, not preferences.

1. **No inline C0 PASS for personalized named outreach**
   - Inline U0/app_payload seed facts may support request shape.
   - They must not by themselves clear public-evidence readiness for personalized named outreach.
   - C0 must emit explicit readiness: `C0_READY`, `C0_OPPORTUNITY_INGESTION_REQUIRED`, `C0_EVIDENCE_STALE`, `C0_EVIDENCE_CONFLICTED`, or `C0_EVIDENCE_BLOCKED`.

2. **No U0 recipient-class authority**
   - `lead_profile.seniority_class`, CLI `recipient_class`, and user notes are hints only.
   - PA and L2 must not default unknown target class to `RECRUITER`.
   - Low-confidence, missing, or conflicted class derivation must block or route HITL/review_required.

3. **No proofless sender claims**
   - PA may pack only approved C0.3 proof IDs and associated claim text.
   - L2 candidate artifacts must map every sender-side factual claim to approved proof IDs.
   - X2 must repair-by-omission once or block; it must not allow unsupported claim text.

4. **No app-specific W7 bypass**
   - Canonical dispatch must run apps_lic X2 before any X1D or final Exit clearance.
   - X1D cannot run on X2-failed artifacts except diagnostic/non-clearance mode.
   - Generic Exit must not hardcode `groundedness=1.0`, `faithfulness=1.0`, `citation_precision=1.0`, or `c0_status=PASS`.

5. **No X1D soft-pass on required judge unavailability**
   - If X1D is required and unavailable, result is `review_required`, not `clear_draft`.
   - If judge and generator independence is required but not proven, label `non_independent_judge` and require review or stricter policy.

6. **No fake self-consistency**
   - SC-2 and SC-3 require real candidate batch objects with candidate IDs, model/provider receipts, selection reason, and rejected-candidate metadata.
   - Metadata may not claim multiple candidates when only one provider output exists.

7. **No AIG-only global validation**
   - AIG-specific terms belong to an AIG fixture/profile lane.
   - Generic apps_lic validation must use message_type, recipient_class, proof packet, company trigger, and source-backed personalization.

8. **No terminal route outside Exit accounting**
   - R5 can still short-circuit before L2, but it must emit an Exit-compatible denial/abstain receipt or an explicitly normalized `[RET]` packet consumed by Exit.

9. **No durable writes outside approved write paths**
   - Runtime generation may write artifacts/receipts only under approved artifact roots.
   - No Chroma/vector/corpus/L4 writes from C0 inference, PA, L2, X2, X1D, or Exit.
   - Governed ingestion writes are separate, explicit, traceable, and not part of inference.

## Hardened Contract Targets

### C0 Canonical Evidence Packet

Add or wire a C0 packet carrying:

```text
readiness_status
support_status
source_snapshot_ids
source_count_by_namespace
missing_namespaces
stale_namespaces
conflicted_namespaces
blocked_namespaces
ingestion_required_reason
retrieval_mode
no_inference_write_receipt
derived_recipient_class
recipient_class_confidence
class_reason_codes
contradiction_report
message_type
message_modifiers
missing_required_fields
reduce_specificity_allowed
```

### C0.3 Sender Proof Packet

Canonical PA must receive:

```text
proof_packet_id
approved_sender_proof_points[]
allowed_claim_ids[]
forbidden_claims[]
omitted_claims[]
claim_permission_map_hash
proof_to_target_relevance_score
proof_graph_refs[]
unsupported_claim_policy
```

### PA Prompt Envelope

Canonical PA must emit:

```text
prompt_hash
component_hash_map
policy_hash
proof_bundle_hash
instruction_data_boundary_receipt
allowed_claim_ids
length_budget_chars
length_budget_words
sentence_budget
message_type
recipient_class
send_mode
sc_level
candidate_count
repair_budget
judge_profile
```

### L2 Candidate Batch

L2 must emit:

```text
batch_id
selected_candidate_id
candidates[]
  candidate_id
  draft_text
  char_count
  word_count
  sentence_count
  claims_used[] as proof IDs
  unresolved_claims[]
  model_id
  provider_id
  temperature
  top_p
  attempt_seed
  no_durable_write_receipt
selection_reason
repair_history
```

### apps_lic W7 Proof Bundle

W7/Exit must emit:

```text
x2_gate_results[]
x1d_results[]
required_judge_depth
independence_status
exit_disposition
exit_reason
review_required_reason
final_user_visible_draft_id
runtime_exhaust_ref
no_send_receipt
no_l4_write_receipt
```

## Implementation Waves

### W0 — Freeze Current Reality And Protect The Baseline

Goal: prove the current live path and pin the exact gaps before code changes.

Tasks:

- Re-run focused apps_lic tests from the last merged PR.
- Add characterization tests that show current gaps, initially expected to fail or marked xfail with explicit reason.
- Confirm all modules to wire: governed_opportunity_ingestion, recipient_classification, message_type_requirement_gate, sender_proof_graph, whole_message_generation, validation_exit, x1d_claude_judge_adapter.
- Confirm current canonical path does not already call apps_lic W7/X2/X1D.

Acceptance:

- Baseline doc/table says which paths are live, dead, test-only, or planned.
- No runtime behavior changes.
- No implementation yet beyond characterization tests if approved.

### W1 — Canonical C0 Readiness And Recipient Class Authority

Goal: make C0 authoritative for evidence readiness and recipient_class.

Tasks:

- Extend `c0_binding.py` to read governed opportunity facts through a read-only store interface.
- Add a readiness gate that returns missing/stale/conflicted/blocked status before PA.
- Wire `derive_recipient_class` into C0 and preserve confidence, source IDs, and contradiction status.
- Retain inline app_payload evidence as `USER_ASSERTED_SEED`, not public evidence authority.
- Remove any fallback-to-recruiter behavior from PA/L2 canonical path.

Acceptance:

- Named outreach with only inline lead+campaign does not clear public-evidence readiness.
- Unknown/low-confidence recipient_class cannot proceed to PA as recruiter.
- Missing readiness returns precise status and source namespace gaps.

### W2 — C0-B Message Type And Requirement Gate

Goal: make message requirements live after class derivation.

Tasks:

- Wire the five canonical message types: `general_intro`, `role_specific`, `trigger_based_insight`, `referral_ask`, `follow_up`.
- Add modifiers for JD, application status, company trigger, referral, prior thread, relationship, and sensitive constraints.
- Enforce JD, position name, requisition number, application status, prior-thread, referral permission, relationship evidence, and trigger source requirements.
- Preserve exact missing-field statuses in proof bundles.

Acceptance:

- Recruiter/Senior TA role_specific without requisition number blocks.
- Follow-up without prior thread cannot invent continuity.
- Referral ask without permission cannot mention referral.
- General intro remains possible only when low-risk and no unsupported specificity is required.

### W3 — C0.3 Sender Proof Packet Into PA And L2

Goal: make sender claims proof-controlled.

Tasks:

- Build/resolve C0.3 proof packet before PA.
- PA packs only approved proof IDs and allowed claim text.
- L2 candidate schema requires `claims_used[]` as proof IDs.
- Unsupported claims are repaired by omission once or blocked.
- Add proof packet hash to PA and runtime manifest.

Acceptance:

- Any draft claim not mapped to C0.3 proof ID is blocked.
- Candidate proof cannot be invented by prompt text, L2 repair, or QA.
- Proof bundle reports approved, omitted, and blocked claims.

### W4 — Real Candidate Batch And Length Budget Wireup

Goal: replace simulated SC with inspectable candidate batches and message-type budgets.

Tasks:

- Add real `WholeMessageCandidateBatch` construction in L2.
- SC-1 emits one candidate; SC-2 emits two; SC-3 emits three.
- Candidate selection is explicit for SC-2/SC-3.
- Replace global 600-char validation with message_type × recipient_class length budgets.
- Keep repair budget same-authority only: formatting/length/schema/tone; never missing evidence.

Acceptance:

- SC-2/SC-3 cannot claim candidate selection unless multiple candidates exist.
- CEO/C-level and follow-up caps are enforced separately from recruiter role_specific caps.
- Length failures repair once or block.

### W5 — Wire apps_lic X2/X1D Before Exit

Goal: make app-specific validation the canonical clearance path.

Tasks:

- Convert L2 output into W7 request + candidate batch.
- Run `run_x2_validation` before X1D.
- Run required X1D depth by risk tier and recipient_class.
- Integrate Claude X1D adapter for live judge when required.
- Represent unavailable/non-independent judge as review_required, not clear.
- Feed apps_lic proof bundle into Exit instead of generic hardcoded groundedness defaults.

Acceptance:

- X1D never runs for clear-path judgment when X2 fails.
- CEO/C-level requires two judge passes for clear draft.
- Required judge unavailable yields review_required.
- Generic Exit packet reflects real C0/X2/X1D status.

### W6 — R5 / RET Exit Normalization

Goal: make terminal fallback auditable under Exit rules.

Tasks:

- Create an Exit-compatible terminal denial/abstain receipt for R5.
- Preserve current fail-closed behavior.
- Ensure all terminal outcomes still emit exactly one final disposition.

Acceptance:

- Deprecated apps_research request yields a single Exit-compatible denial.
- Terminal R5 path has no C0/PA/L2 execution but still has Exit accounting.

### W7 — De-AIG Global Validation

Goal: keep AIG-specific quality gates as fixtures/profiles, not global apps_lic law.

Tasks:

- Move AIG operating-insight checks into AIG fixture/profile config.
- Replace global AIG terms with source-backed company_trigger / company_context requirements.
- Add non-AIG company fixtures.

Acceptance:

- AIG tests still pass under AIG profile.
- Non-AIG personalized outreach is not forced to mention underwriting, claims, AIG, or insurance-specific language.

### W8 — E2E Proof And Rollout Controls

Goal: prove happy paths and fail-closed paths end to end.

Tasks:

- Add deterministic fixture suite covering all critical paths.
- Add runtime proof bundle checks for C0, C0.3, X2, X1D, Exit.
- Add rollout flags and kill switches.
- Document rollback behavior.

Acceptance:

- E2E proves C0 readiness, derived recipient class, C0-B gates, C0.3 proof, real candidate batches, apps_lic X2/X1D, and Exit disposition.
- Rollback returns to safe generic low-claim/review-required/block behavior, not ungrounded personalization.

## Minimum Negative Fixture Suite

These fixtures are mandatory before completion.

| Fixture | Expected outcome |
| --- | --- |
| Named target with only inline lead+campaign | readiness block/review; no public-evidence PASS |
| Unknown or typo recipient_class hint | no fallback to recruiter |
| Ambiguous “Talent Partner / Business Partner” profile | low-confidence/HITL |
| Conflicting recruiter and hiring-manager signals | conflicted/HITL |
| Recruiter general_intro with sufficient C0 evidence and no JD | allowed low-risk draft |
| Recruiter role_specific missing JD | block |
| Senior TA role_specific missing requisition number | block |
| Hiring manager role_specific missing JD | block |
| Trigger-based note with stale trigger | stale block or policy-approved reduce-specificity |
| Referral ask without permission | block referral mention |
| Follow-up without prior thread | block continuity claims |
| L2 invents project/metric not in C0.3 packet | X2 unsupported-claim block |
| SC-3 with one candidate only | candidate-selection gate fails |
| CEO/C-level with one judge pass and one fail | review_required/block, never clear |
| Required X1D unavailable | review_required |
| Same model/provider where independent judge required | non_independent_judge review_required |
| Non-AIG target under generic profile | no AIG term requirement |
| Deprecated apps_research request | single Exit-compatible deny/abstain |
| Chroma/vector store unavailable | readiness error, no silent inline PASS |
| Inference attempted vector/write handle | hard failure/no-write receipt failure |

## Rollout Flags

Implement behind explicit flags. Defaults should be safe.

```text
APPS_LIC_C0_READINESS_REQUIRED=true
APPS_LIC_INLINE_C0_PASS_DENY_FOR_NAMED_OUTREACH=true
APPS_LIC_C0_DERIVED_RECIPIENT_CLASS_REQUIRED=true
APPS_LIC_C0B_MESSAGE_REQUIREMENT_GATE_REQUIRED=true
APPS_LIC_C03_PROOF_PACKET_REQUIRED=true
APPS_LIC_REAL_CANDIDATE_BATCH_REQUIRED_FOR_SC2_SC3=true
APPS_LIC_APP_X2_REQUIRED=true
APPS_LIC_X1D_REQUIRED_BY_RISK=true
APPS_LIC_GENERIC_EXIT_HARDCODED_GROUNDING_DENY=true
APPS_LIC_R5_EXIT_RECEIPT_REQUIRED=true
APPS_LIC_AIG_QUALITY_PROFILE_GLOBAL=false
APPS_LIC_AUTO_SEND_DISABLED=true
APPS_LIC_INFERENCE_VECTOR_WRITE_DENY=true
```

Rollback rule:

- If C0/C0.3/X2/X1D wireup destabilizes, rollback must produce `review_required`, `blocked`, or generic low-claim draft where explicitly allowed. It must not restore ungrounded named personalization.

## Definition Of Done

Implementation is complete only when all are true:

- The canonical path cannot clear a named/personalized message with inline-only C0 evidence.
- C0 emits readiness status, derived_recipient_class, confidence, reason codes, and source snapshot IDs.
- PA has no fallback-to-recruiter path.
- PA packs C0.3 proof IDs and rejects unapproved claims.
- L2 emits real candidate batches for SC-2/SC-3.
- X2 runs before X1D and before final Exit clearance.
- Required X1D unavailability produces review_required.
- Generic Exit no longer hardcodes C0/grounding PASS values.
- R5 terminal paths emit one Exit-compatible disposition.
- AIG-specific validation is profile-specific, not global.
- All minimum negative fixtures pass.
- Runtime proof bundle explains clear/review/block/abstain with C0, C0.3, X2, X1D, and Exit receipts.
- No implementation path performs Chroma/vector/L4 writes during inference.

## Reviewer Checklist For Codex/Agent Output

Reviewers must block any implementation PR that:

- lets inline app_payload evidence become C0 public-evidence PASS for named outreach;
- lets U0 recipient class bypass C0 derivation;
- preserves fallback-to-recruiter on unknown class;
- packs free-form sender proof claims into PA without C0.3 IDs;
- claims SC-2/SC-3 without real candidate batches;
- uses generic Exit hardcoded groundedness/c0_status defaults;
- lets X1D run before X2 pass;
- clears CEO/C-level without two required judge passes;
- keeps AIG-specific terms as global validation law;
- creates any inference-time vector/write/L4 mutation path.

## Open Decisions Before Implementation

- Which read-only opportunity fact store adapter is canonical for C0 readiness in local/CI/live contexts?
- What are final freshness windows for contact, role ownership, company, JD, trigger, referral, relationship, and prior thread facts?
- Should generic low-claim fallback be allowed for named targets with weak C0, or should all named weak-C0 cases be review_required?
- Which provider/model combinations satisfy X1D independence for CEO/C-level?
- How should C0.3 proof packets be serialized into existing `CompiledPromptArtifact` without widening generic contracts?
- Should terminal R5 produce an apps_lic-specific ExitDispositionReceipt directly or a normalized `[RET]` packet consumed by shared Exit?
- Which AIG-specific gates remain in AIG fixture/profile and which become generic company-trigger checks?

## Verification Command Target

Initial focused command after implementation begins:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p pytest_timeout \
  tests/apps_lic/test_canonical_dispatch_smoke.py \
  tests/apps_lic/test_runtime_proof_bundle.py \
  tests/apps_lic/test_reasoning_intensity_policy.py \
  tests/apps_lic/test_w3_recipient_classification.py \
  tests/apps_lic/test_w5_sender_proof_graph.py \
  tests/apps_lic/test_w7_validation_exit.py
```

Add or update E2E tests as each wave wires into the canonical path.

## Non-Goals

- No broad copy-style rewrite.
- No replacement of Qwen/vLLM provider strategy.
- No live web research delegation during inference.
- No Chroma/vector ingestion from canonical runtime.
- No auto-send implementation.
- No app-wide rewrite outside the stated wireup seams.
- No agentic multi-file refactor without wave-level acceptance tests.

## Completion Marker

Do not mark complete until W0-W8 acceptance criteria and the full negative fixture suite pass.

```text
PLAN_COMPLETE: plan=apps-lic-canonical-hardening-wireup-4c9d2a note="Canonical C0 readiness, derived recipient_class, C0-B gates, C0.3 proof packet, real candidate batches, apps_lic X2/X1D, Exit-compatible R5, profile-scoped AIG validation, proof bundle, and negative fixtures wired and verified."
```
