# apps_lic 30-Profile Gap Remediation and Retest Plan

Plan ID: `apps-lic-30-profile-gap-remediation-a9f3c2`
Created: 2026-06-08
Worktree: `C:\Git\agentic-workflow-fresh-apps-lic`
Status: Draft, awaiting implementation approval

## Objective

Rectify all gaps found during the AIG 30-profile apps_lic E2E hardening run, then retest through W2/W3/W4/W5/W6/W7 with deterministic Exit gates and live or explicitly unavailable Claude Sonnet X1D judge proof.

## Current Baseline

Artifacts:

- `artifacts/apps_lic/e2e_aig_30_linkedin_profiles_20260608/results.json`
- `artifacts/apps_lic/e2e_aig_30_linkedin_profiles_20260608/summary.md`
- `artifacts/apps_lic/e2e_aig_30_linkedin_profiles_20260608/messages_all_30.md`
- `artifacts/apps_lic/e2e_aig_30_linkedin_profiles_20260608/messages_clear_drafts.md`

Current result:

- Classification: 30/30 expected classes matched.
- Exit expectation: 30/30 matched current policy expectations.
- Clear drafts: 24/30.
- Policy-blocked: 6/30.
- X1D artifact status: 24 pass, 6 blocked before judge execution.
- Judge mode: fake Claude Sonnet 4.6-style transport, not live Anthropic.

## Gap Register

| ID | Priority | Gap | Evidence | Required Outcome |
|---|---:|---|---|---|
| G1 | P0 | Live Claude X1D is not proven. | `ANTHROPIC_API_KEY` is missing; artifacts use fake Claude-style transport. | Live preflight either passes with model-backed judge results or emits a single fail-closed unavailable-judge artifact. |
| G2 | P0 | "All 30 pass" is impossible under strict current policy without changing evidence, target set, or message mode. | Six rows are intentionally blocked. | Add explicit retest modes: strict target-fit mode and all-clear eligible-contact mode. No silent policy weakening. |
| G3 | P0 | Six blocked profiles need root-cause handling. | Daisuke has regional JD mismatch; Kathleen/Dennis/Anirudh/Karthikeya/Indu lack target-owner class evidence. | Each blocked profile either receives stronger C0 evidence, an allowed alternate message route, or a clear NOT_TARGETABLE result. |
| G4 | P0 | C0 evidence is seeded manually, not fully governed public evidence ingestion into fact vectors. | 30-profile harness uses local seed snippets and in-memory store. | On-demand C0 ingestion checks existing vectors, writes governed fact vectors when missing/stale, and records source lineage. |
| G5 | P1 | 30-profile matrix is not a reusable test harness. | The matrix was run as an inline artifact script. | Add committed fixtures, runner, pytest coverage, and stable artifact schema. |
| G6 | P1 | Repetitive recruiter drafts pass gates but are not innovative enough. | Recruiter/Senior TA messages share nearly identical copy. | Provider-backed or candidate-template-diverse W6 path produces materially distinct, recipient-aware drafts. |
| G7 | P1 | Recruiter X1D policy is too narrow for quality. | Role-specific recruiter paths use `evidence_claim_support_x1d` only. | Add lightweight LinkedIn tone/non-generic X1D or deterministic originality gate for recruiter/Senior TA role-specific messages. |
| G8 | P1 | Blocked rows produce noisy downstream gate failures. | UNKNOWN rows show schema, whole-message, length, unsupported-claim cascade failures. | Exit artifact exposes the root blocker first: recipient class not derived or target not eligible. Secondary failures are diagnostic only. |
| G9 | P1 | Daisuke produces a blocked draft artifact. | `messages_all_30.md` includes a DO NOT SEND draft. | Product-facing artifact hides blocked drafts by default; internal artifact may retain with no-send watermark. |
| G10 | P2 | Retest does not prove Chroma/fact-vector readiness. | No vector stats, collection baselines, or stale/missing checks in artifact. | Retest includes vector collection stats and per-profile C0 readiness receipts. |

## Wave Plan

### W0 - Freeze Acceptance Modes and No-Weakening Rule

Priority: P0

Purpose: Define what "all pass" means without weakening gates.

Implementation:

- Add an E2E mode flag:
  - `strict_target_fit`: current policy; non-targetable or mismatched contacts are expected to block.
  - `all_clear_eligible`: only profiles with enough C0 evidence and opportunity fit are included, or blocked profiles use an explicitly allowed alternate message mode.
- Add acceptance notes to the 30-profile artifact:
  - Strict mode expected result: 24 clear, 6 correct blocks unless more evidence is supplied.
  - All-clear mode expected result: 30 clear only after evidence/routing remediation.
- Encode no-weakening invariant:
  - Do not disable `recipient_class_present_and_derived_gate`.
  - Do not disable `role_ownership_fit_gate`.
  - Do not allow SC or extra judges to compensate for missing C0 evidence.

Tests:

- Unit test mode contract.
- Regression test that strict mode still blocks Daisuke region mismatch.
- Regression test that UNKNOWN contacts do not silently generate sendable drafts.

Exit criteria:

- Retest reports distinguish "policy-correct block" from "gap to fix".

### W1 - Live Claude X1D Preflight and Judge Proof

Priority: P0

Purpose: Prove real Claude Sonnet X1D or fail closed cleanly.

Implementation:

- Add `apps_lic` judge preflight:
  - Detect `ANTHROPIC_API_KEY`.
  - Detect Anthropic SDK.
  - Confirm configured Claude Sonnet 4.6 model id.
  - Run a minimal rubric call with JSON parse validation.
- Add live judge mode to the 30-profile runner:
  - `--x1d-mode fake`
  - `--x1d-mode live`
  - `--x1d-mode unavailable-expected`
- Persist judge receipts:
  - provider
  - model
  - score
  - threshold
  - availability_status
  - independence_status
  - raw response digest, not raw prompt secrets

Tests:

- Fake transport pass test remains deterministic.
- Missing key test returns unavailable judge artifact and review/block disposition where X1D is required.
- Live test is opt-in and skipped only by environment marker, not `pytest.mark.skip`.

Exit criteria:

- With key: 24 or 30 generated drafts have live Claude X1D pass artifacts.
- Without key: artifact states live judge unavailable as the primary blocker.

### W2 - Governed C0 Public Evidence and Fact Vector Readiness

Priority: P0

Purpose: Move from manual snippet seeding to governed C0 retrieval and fact-vector readiness.

Implementation:

- Create per-profile evidence input records:
  - name
  - title/headline seed
  - LinkedIn/public URL
  - company
  - expected opportunity scope
- Add on-demand C0 ingestion runner:
  - Check Chroma/fact-vector namespace readiness.
  - If missing/stale, run governed ingestion outside inference.
  - Store contact facts, public snippets, role ownership facts, source lineage, confidence, and freshness.
- Baseline vector collections:
  - standing sender corpus
  - AIG company facts
  - AIG JD facts
  - per-contact public evidence facts
  - role ownership facts
- Emit per-profile readiness receipt:
  - ready/missing/stale/conflicted
  - source count
  - vector collection name
  - source_snapshot_ids

Tests:

- Missing vector collection returns ingestion required.
- Stale profile fact triggers governed refresh.
- C0 retrieval is read-only during inference.
- C0 writes require governed ingestion authority.

Exit criteria:

- Retest artifact proves C0 vector readiness for every included profile.

### W3 - Resolve the Six Blocked Profiles Without Policy Bypass

Priority: P0

Purpose: Make each blocked profile either clear through an allowed route or remain explicitly not targetable.

Profile remediation:

| Profile | Current Block | Remediation Path |
|---|---|---|
| Daisuke Hayashi | `role_ownership_fit_gate`: AIG Japan/Tokyo versus US JD. | Add opportunity-fit router. If goal is the US JD, keep blocked. If user chooses non-JD general intro to AIG Japan TA, remove JD reference and require company/contact context. |
| Kathleen Gerstner | UNKNOWN class from weak current title evidence. | Run C0 public evidence enrichment. If current recruiter/TA ownership is found, route recruiter or Senior TA. If not, mark NOT_TARGETABLE. |
| Dennis Najar | UNKNOWN class from vague "IT and Management Executive". | Run C0 enrichment for current title and ownership. If no C-level/hiring-owner signal, mark NOT_TARGETABLE. |
| Anirudh R | UNKNOWN IC profile. | Do not force apps_lic role outreach. Either exclude from eligible-contact matrix or add a separately approved peer-networking scope. |
| Karthikeya Gowd | UNKNOWN IC profile. | Same as Anirudh. |
| Indu Sri | UNKNOWN IC profile. | Same as Anirudh. |

Implementation:

- Add `target_eligibility` output:
  - `ELIGIBLE`
  - `ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE`
  - `NOT_TARGETABLE`
  - `C0_EVIDENCE_REQUIRED`
- Add optional `alternate_message_mode`:
  - `general_intro_no_jd`
  - `company_context_intro`
  - `peer_networking_intro` only if explicitly added to apps_lic scope.
- Add no-send rule:
  - A blocked strict JD-specific draft must not be exposed as user-visible copy.

Tests:

- Daisuke strict role-specific remains blocked.
- Daisuke alternate general intro can pass only when JD references are omitted.
- UNKNOWN profiles require C0 enrichment or NOT_TARGETABLE.
- IC profiles cannot pass as recruiter/hiring-manager/executive.

Exit criteria:

- Strict matrix: 24 clear, 6 explained blocks.
- All-clear matrix: 30 clear only with approved alternate routing or replacement/stronger C0 evidence for the six profiles.

### W4 - Reusable 30-Profile E2E Harness

Priority: P1

Purpose: Replace inline script with repeatable tests and artifacts.

Implementation:

- Add fixture:
  - `tests/apps_lic/fixtures/aig_30_profiles.json`
- Add runner:
  - `scripts/apps_lic/run_aig_30_profile_e2e.py`
- Add pytest:
  - `tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- Artifact schema:
  - `summary.json`
  - `results.json`
  - `messages_clear_drafts.md`
  - `blocked_profiles.md`
  - `judge_receipts.json`
  - `c0_readiness.json`

Tests:

- Runner produces deterministic fake-judge artifacts.
- Pytest asserts expected counts by mode.
- Artifact schema validation.

Exit criteria:

- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake`
- `python -m pytest tests/apps_lic/test_w8_aig_30_profile_e2e.py -q`

### W5 - Message Quality and Non-Repetition Hardening

Priority: P1

Purpose: Make messages less generic while preserving evidence discipline.

Implementation:

- Add message diversity controls:
  - candidate-level rhetorical angle
  - recipient-class-specific CTA
  - company trigger compression
  - proof point rotation based on recipient class
- Add anti-repetition gates:
  - no identical drafts across same class for different recipients unless same contact context.
  - n-gram similarity ceiling across matrix.
  - banned generic phrasing list.
- Add high-temperature provider path:
  - Keep W6 scaffold as deterministic fallback.
  - Add provider-backed generation adapter behind explicit config.
  - Preserve draft_only and no-send receipts.

Tests:

- Recruiter messages for at least 5 profiles are non-identical.
- Similarity ceiling regression.
- Generated copy still includes JD title and req for recruiter/Senior TA role-specific messages.
- No unsupported sender claims.

Exit criteria:

- 24 or 30 clear drafts pass diversity checks and Exit gates.

### W6 - X1D Judge Policy Upgrade by Recipient Type

Priority: P1

Purpose: Ensure LLM-as-judge coverage matches message risk and quality expectations.

Policy:

- Recruiter/Senior TA role-specific:
  - Keep `evidence_claim_support_x1d`.
  - Add lightweight `linkedin_tone_non_generic_x1d` when using provider-backed generation or when similarity gate flags risk.
- Hiring manager:
  - Evidence support X1D.
  - Tone/non-generic X1D for role-specific claims.
- Executive/CTO/VP_ENG:
  - LinkedIn tone/channel quality X1D.
  - Evidence support if using JD or technical proof.
- CEO/C_LEVEL:
  - Two judges remain required:
    - attention/originality/strategic sharpness
    - evidence overclaim/no-fabrication risk

Tests:

- Required judge profile mapping by recipient class and message type.
- Missing required judge causes review/block.
- Wrong model/provider fails independence/provider gate.
- Live/fake modes share the same normalized result contract.

Exit criteria:

- Every clear draft has required judge receipts.
- CEO/C_LEVEL always show two X1D judge passes.

### W7 - Exit UX and Blocked Artifact Cleanup

Priority: P1

Purpose: Make blocked results understandable and prevent accidental use.

Implementation:

- Add root-cause field:
  - `primary_blocker`
  - `user_action_required`
  - `safe_alternative`
- Collapse cascaded downstream failures under diagnostics.
- Split artifacts:
  - clear drafts only
  - blocked profiles with no draft by default
  - internal blocked draft appendix only with `DO_NOT_SEND` watermark

Tests:

- UNKNOWN profile exposes `recipient_class_not_derived` as primary blocker.
- Region mismatch exposes `role_ownership_region_mismatch`.
- Product-facing artifact never includes unwatermarked blocked draft.

Exit criteria:

- Blocked-profile report is human-readable and action-oriented.

### W8 - Final Retest Matrix

Priority: P0 for strict, P1 for all-clear

Retest commands:

```powershell
python -m pytest tests\apps_lic\test_w0_contract_freeze.py tests\apps_lic\test_w1_standing_sender_knowledge.py tests\apps_lic\test_w2_governed_opportunity_ingestion.py tests\apps_lic\test_w3_recipient_classification.py tests\apps_lic\test_w4_message_type_requirement_gate.py tests\apps_lic\test_w5_sender_proof_graph.py tests\apps_lic\test_w6_whole_message_generation.py tests\apps_lic\test_w7_validation_exit.py -q
python scripts\apps_lic\run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake
python scripts\apps_lic\run_aig_30_profile_e2e.py --mode all_clear_eligible --x1d-mode fake
python scripts\apps_lic\run_aig_30_profile_e2e.py --mode all_clear_eligible --x1d-mode live
python -m pytest tests\apps_lic\test_w8_aig_30_profile_e2e.py -q
```

Expected results:

- Strict target-fit fake mode:
  - 30/30 classification.
  - 24 clear drafts.
  - 6 correct blocks with primary blocker.
- All-clear eligible fake mode:
  - 30/30 clear only if the six blocked contacts are remediated through stronger C0 evidence, approved alternate route, or replacement with eligible contacts.
- Live mode:
  - With `ANTHROPIC_API_KEY`: all clear drafts have live Claude judge pass receipts.
  - Without `ANTHROPIC_API_KEY`: live mode fails closed with unavailable-judge artifacts.

## Implementation Order

1. W0, W1: make acceptance and live judge truth explicit.
2. W4: make the 30-profile matrix reusable before more changes.
3. W2, W3: fix evidence and blocked-profile routing without policy bypass.
4. W5, W6: improve quality and judge coverage.
5. W7, W8: clean artifacts and final retest.

## Non-Goals

- Do not weaken C0 evidence requirements.
- Do not make SC or judge count compensate for missing evidence.
- Do not auto-send or create send-ready output for blocked profiles.
- Do not classify IC profiles as recruiter, hiring manager, or executive without evidence.
- Do not treat fake X1D transport as live Claude proof.

## Open Decisions

1. Should apps_lic add a new peer/networking recipient class, or should IC profiles be excluded from eligible-contact outreach?
2. For Daisuke, should the all-clear route be an AIG Japan general intro, or should he remain blocked for the US JD?
3. Should live Claude be mandatory for every retest, or allowed as an opt-in CI/local proof when credentials exist?
4. Should blocked drafts be generated internally for debugging, or suppressed entirely unless a debug flag is set?

## W1 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added `apps_lic/engines/x1d_preflight.py` with explicit X1D modes: `fake`, `live`, and `unavailable-expected`.
- Live mode now fails closed unless `ANTHROPIC_API_KEY`, Anthropic SDK availability, configured `claude-sonnet-4-6`, and a parseable minimal Claude rubric response are all present.
- Fake and unavailable-expected modes produce explicit non-clearance receipts and do not call the judge transport.
- X1D judge receipts now persist `raw_response_digest`; Exit requires that digest and trusted Anthropic transport provenance for live Claude clearance.
- Non-Anthropic transports, injected Anthropic clients, and hand-built/mock live-looking artifacts are blocked.
- Updated `apps_lic/config/domain_contract/validation_exit.v1.yaml` with W1 preflight and digest policy.

Verification:

- `python -m py_compile apps_lic/engines/x1d_claude_judge_adapter.py apps_lic/engines/x1d_preflight.py apps_lic/engines/validation_exit.py`
- `python -m pytest tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w7_validation_exit.py -q` -> 22 passed, 1 skipped, 3 warnings.
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w7_validation_exit.py -q` -> 117 passed, 1 skipped, 3 warnings.

Notes:

- The skipped test is the explicit opt-in live Claude check, gated by `APPS_LIC_RUN_LIVE_CLAUDE_X1D=1`.
- No live Anthropic API call was made in this deterministic W1 run because the opt-in marker was not set.

Next: W2 governed C0/fact-vector readiness wave.

## W2 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added per-profile C0 evidence records through `ProfileEvidenceInputRecord`.
- Added W2 baseline fact-vector collection contract for standing sender corpus, AIG company facts, AIG JD facts, per-contact public evidence facts, and role ownership facts.
- Added profile-level readiness receipts with status, source counts, vector collection names, source snapshot IDs, and missing/stale/conflicted/blocked collection lists.
- Added `check_profile_evidence_readiness` as a read-only inference-safe readiness check.
- Added `ensure_profile_c0_readiness` to run governed ingestion only when profile evidence is missing or stale, and only with `governed_opportunity_ingestion` authority.
- Threaded `profile_id`, expected opportunity scope, confidence, and source lineage into contact and role-ownership fact documents.
- Updated `apps_lic/config/domain_contract/opportunity_ingestion.v1.yaml` with profile input, baseline collection, on-demand ingestion, and readiness receipt policy.

Verification:

- `python -m py_compile apps_lic/engines/governed_opportunity_ingestion.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py`
- `python -m pytest tests/apps_lic/test_w2_governed_opportunity_ingestion.py -q` -> 17 passed, 3 warnings.
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w7_validation_exit.py -q` -> 123 passed, 1 skipped, 3 warnings.

Notes:

- The W2 implementation remains store-agnostic and does not import Chroma directly; collection readiness is expressed through the fact-vector store protocol and deterministic in-memory test store.
- Inference checks remain read-only. Missing/stale refresh is modeled as a separate governed ingestion step.

Next: W3 blocked-profile routing and NOT_TARGETABLE handling.

## W3 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added `TargetEligibilityResult` with `ELIGIBLE`, `ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE`, `NOT_TARGETABLE`, and `C0_EVIDENCE_REQUIRED`.
- Added alternate message modes: `general_intro_no_jd`, `company_context_intro`, and `peer_networking_intro`.
- Added W3 target eligibility router that keeps strict JD-specific Daisuke/AIG Japan outreach blocked for the US JD, but allows an explicit `general_intro_no_jd` alternate route when requested.
- Added no-send draft exposure guard so blocked strict JD-specific drafts are not exposed as user-visible copy.
- Added alternate no-JD copy validation so Daisuke alternate copy blocks if it contains the JD title, requisition number, or JD/requisition language.
- Added UNKNOWN/IC handling: missing evidence returns `C0_EVIDENCE_REQUIRED`; weak current target-owner evidence and IC-only evidence return `NOT_TARGETABLE` unless peer networking is explicitly allowed.
- Updated `apps_lic/config/domain_contract/recipient_classification.v1.yaml` with target eligibility and no-send rules.

Verification:

- `python -m py_compile apps_lic/engines/recipient_classification.py tests/apps_lic/test_w3_recipient_classification.py`
- `python -m pytest tests/apps_lic/test_w3_recipient_classification.py -q` -> 28 passed, 3 warnings.
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w7_validation_exit.py -q` -> 129 passed, 1 skipped, 3 warnings.

Notes:

- W3 does not weaken `role_ownership_fit_gate`; it adds a pre-generation eligibility decision and draft exposure guard.
- `peer_networking_intro` exists only behind explicit scope allowance and does not reclassify IC profiles as recruiter, hiring manager, or executive.

Next: W4 reusable 30-profile matrix runner and artifact schema.

## W4 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added committed AIG 30 fixture at `tests/apps_lic/fixtures/aig_30_profiles.json`.
- Added reusable runner at `scripts/apps_lic/run_aig_30_profile_e2e.py`.
- Runner supports `--mode strict_target_fit` and `--mode all_clear_eligible`.
- Runner supports `--x1d-mode fake`, `--x1d-mode live`, and `--x1d-mode unavailable-expected`.
- Runner writes stable artifact schema:
  - `summary.json`
  - `results.json`
  - `messages_clear_drafts.md`
  - `blocked_profiles.md`
  - `judge_receipts.json`
  - `c0_readiness.json`
- Fake judge mode is explicit fixture replay only: it emits deterministic receipts with `live_claude_proof=false` and `clearance_allowed=false`; it does not claim live Claude proof.
- Blocked profiles artifact suppresses blocked draft copy; clear drafts stay isolated in `messages_clear_drafts.md`.
- Added pytest coverage at `tests/apps_lic/test_w8_aig_30_profile_e2e.py`.

Verification:

- `python -m py_compile scripts/apps_lic/run_aig_30_profile_e2e.py tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w4/strict_target_fit_fake`
- `python -m pytest tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 5 passed, 3 warnings.
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 134 passed, 1 skipped, 3 warnings.

Strict fake artifact summary:

- 30 profiles.
- 24 clear drafts.
- 6 policy-correct blocks.
- 30 C0-ready rows.
- 32 deterministic fixture judge receipts.
- Live Claude proof: false.

Notes:

- W4 intentionally separates acceptance-mode replay from live Claude proof. W1 remains the authority that fake/mock judge paths cannot clear live X1D.
- Generated W4 artifacts live under `artifacts/apps_lic/e2e_aig_30_profile_w4/strict_target_fit_fake` and are treated as generated outputs.

Next: W5 sender-proof/message quality hardening.

## W5 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added pure W5 message quality engine at `apps_lic/engines/message_quality.py`.
- Added deterministic message diversity controls:
  - candidate-level rhetorical angle selection.
  - recipient-class-specific CTA selection.
  - company trigger compression.
  - recipient-class-based approved proof point rotation.
- Added anti-repetition gates:
  - normalized identical-draft blocking across different recipients in the same class.
  - pairwise 5-gram Jaccard similarity ceiling.
  - banned generic phrase list.
  - role-specific JD title and requisition retention check for recruiter/Senior TA/hiring-manager drafts.
  - C0.3 `claims_used` authorization through the standing sender corpus.
- Wired the AIG 30 replay through W5 variants and summary-level `message_quality` results.
- Added explicit provider-backed generation policy contract in `apps_lic/config/domain_contract/whole_message_generation.v1.yaml`:
  - disabled by default.
  - requires explicit config.
  - whole-message only.
  - draft-only/no-send authority preserved.
  - W6 deterministic fallback remains available.
- Updated W6 deterministic fallback to rotate selected C0.3 proof points across SC candidates.
- Added pytest coverage at `tests/apps_lic/test_w5_message_quality.py`.

Verification:

- `python -m py_compile apps_lic/engines/message_quality.py apps_lic/engines/whole_message_generation.py scripts/apps_lic/run_aig_30_profile_e2e.py tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- `python -m pytest tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 13 passed, 3 warnings.
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w5/strict_target_fit_fake`
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 142 passed, 1 skipped, 3 warnings.

Strict fake W5 artifact summary:

- 30 profiles.
- 24 clear drafts.
- 6 policy-correct blocks.
- 24 clear drafts passed W5 diversity/quality checks.
- Max 5-gram similarity: 0.80.
- Similarity ceiling: 0.82.
- W5 quality violations: 0.
- Live Claude proof: false.

Notes:

- W5 does not treat fake X1D receipts as live proof. Fake mode remains deterministic fixture replay only.
- W5 improves wording/diversity but does not override C0 evidence, W4 requirements, X2 gates, no-send policy, or Exit disposition.

Next: W6 provider-backed generation integration/wiring.

## W6 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added W6 recipient/message-type X1D judge policy resolver in `apps_lic/engines/validation_exit.py`.
- Added lightweight `linkedin_tone_non_generic_x1d` judge profile.
- Enforced W6 matrix:
  - Recruiter/Senior TA role-specific: `evidence_claim_support_x1d` by default; add `linkedin_tone_non_generic_x1d` for provider-backed or similarity-risk paths.
  - Hiring manager role-specific: `evidence_claim_support_x1d` + `linkedin_tone_non_generic_x1d`.
  - Executive/CTO/VP_ENG: `linkedin_tone_channel_quality_x1d`; add evidence support when JD or technical proof is used.
  - CEO/C_LEVEL: `ceo_attention_originality_x1d` + `ceo_evidence_overclaim_risk_x1d`.
- Updated X1D depth reporting so resolved two-judge policies report depth `two`.
- Updated `apps_lic/config/domain_contract/validation_exit.v1.yaml` with the W6 judge matrix.
- Updated `scripts/apps_lic/run_aig_30_profile_e2e.py` so required judge receipts are derived from W6 policy, not stale fixture fields.
- Added `judge_policy` summary to AIG 30 artifacts with required receipt coverage and CEO/C_LEVEL two-judge proof.
- Added normalized result contract payloads to fixture receipts so fake/live fixture modes share the same receipt shape while still failing live-clearance authority.
- Added pytest coverage at `tests/apps_lic/test_w6_x1d_judge_policy.py`.

Verification:

- `python -m py_compile apps_lic/engines/validation_exit.py apps_lic/engines/whole_message_generation.py scripts/apps_lic/run_aig_30_profile_e2e.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- `python -m pytest tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 24 passed, 3 warnings.
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w6/strict_target_fit_fake`
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 149 passed, 1 skipped, 3 warnings.

Strict fake W6 artifact summary:

- 30 profiles.
- 24 clear drafts.
- 6 policy-correct blocks.
- Required judge receipts: 36.
- All clear drafts have required judge receipts: true.
- CEO/C_LEVEL clear drafts: 8.
- CEO/C_LEVEL with two required judges: 8.
- Missing required judge receipts: 0.
- Message quality passed: true.
- Live Claude proof: false.

Notes:

- Fake mode still cannot clear live Claude authority; normalized fixture receipts are schema-compatible only.
- W6 does not allow X1D to override C0 evidence, X2 gates, no-send policy, or Exit disposition.

Next: W7 live Claude wiring / Exit hardening.

## W7 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added blocked artifact UX engine at `apps_lic/engines/blocked_artifact_ux.py`.
- Added blocked row fields:
  - `primary_blocker`
  - `user_action_required`
  - `safe_alternative`
  - `diagnostics`
  - `blocked_draft_ref`
  - `product_draft_exposed=false`
- Collapsed cascaded downstream failures into diagnostics instead of presenting every downstream gate as the root cause.
- Mapped UNKNOWN/low-confidence profiles to `recipient_class_not_derived`.
- Mapped strict AIG Japan/contact vs US JD ownership mismatch to `role_ownership_region_mismatch`.
- Updated product-facing `blocked_profiles.md` to show action-oriented blocker fields and never show blocked draft text.
- Added `internal_blocked_draft_appendix.md` for internal diagnostic use only; any blocked draft text is isolated there with `DO_NOT_SEND` watermarking.
- Added `blocked_ux` summary to `summary.json` and `results.json`.
- Added pytest coverage at `tests/apps_lic/test_w7_blocked_artifact_ux.py`.

Verification:

- `python -m py_compile apps_lic/engines/blocked_artifact_ux.py scripts/apps_lic/run_aig_30_profile_e2e.py tests/apps_lic/test_w7_blocked_artifact_ux.py tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- `python -m pytest tests/apps_lic/test_w7_blocked_artifact_ux.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 10 passed, 3 warnings.
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w7/strict_target_fit_fake`
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w7_blocked_artifact_ux.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 154 passed, 1 skipped, 3 warnings.

Strict fake W7 artifact summary:

- 30 profiles.
- 24 clear drafts.
- 6 policy-correct blocks.
- Primary blocker counts:
  - `recipient_class_not_derived`: 5.
  - `role_ownership_region_mismatch`: 1.
- Product-facing blocked draft exposure count: 0.
- Product-facing blocked drafts suppressed: true.
- Internal blocked draft appendix count: 1.
- Internal appendix watermark: `DO_NOT_SEND`.
- Live Claude proof: false.

Notes:

- W7 is artifact UX only; it does not weaken C0 evidence, W4/W6 policies, X2 gates, no-send policy, or Exit clearance.
- Blocked drafts remain unavailable in product-facing artifacts. The internal appendix is explicitly watermarked and diagnostic-only.

Next: W8 final AIG 30 matrix hardening / closeout.

## W8 Completion - 2026-06-08

Status: Complete in apps-lic worktree.

Implemented:

- Added `final_retest_matrix.json` as a required AIG 30 E2E artifact.
- Mirrored W8 matrix status into `summary.json` via:
  - `final_retest_matrix_passed`
  - `final_retest_matrix_result`
  - `final_retest_matrix`
- Encoded retest semantics without weakening policy:
  - `strict_target_fit` + fake expects 24 clear drafts and 6 policy-correct blocks.
  - `all_clear_eligible` + fake expects remediation-required status for the same six blocked contacts until evidence/routing/contact set changes.
  - `all_clear_eligible` + live passes the W8 fail-closed retest when live Claude preflight is unavailable and no fixture receipt claims live proof.
- Added invariant checks to the matrix:
  - no weakening violations absent.
  - X1D did not override C0/X2/Exit.
  - SC did not compensate for missing C0 evidence.
  - fake mode does not claim live Claude proof.
  - product-facing blocked drafts remain suppressed.
- Added pytest coverage for W8 final matrix and live-without-key fail-closed behavior in `tests/apps_lic/test_w8_aig_30_profile_e2e.py`.

Verification:

- `python -m py_compile scripts/apps_lic/run_aig_30_profile_e2e.py tests/apps_lic/test_w8_aig_30_profile_e2e.py`
- `python -m pytest tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 6 passed, 3 warnings.
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode strict_target_fit --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w8/strict_target_fit_fake`
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode all_clear_eligible --x1d-mode fake --output-dir artifacts/apps_lic/e2e_aig_30_profile_w8/all_clear_eligible_fake`
- `python scripts/apps_lic/run_aig_30_profile_e2e.py --mode all_clear_eligible --x1d-mode live --output-dir artifacts/apps_lic/e2e_aig_30_profile_w8/all_clear_eligible_live`
- `python -m pytest tests/apps_lic/test_w0_contract_freeze.py tests/apps_lic/test_w1_x1d_preflight.py tests/apps_lic/test_w1_standing_sender_knowledge.py tests/apps_lic/test_w2_governed_opportunity_ingestion.py tests/apps_lic/test_w3_recipient_classification.py tests/apps_lic/test_w4_message_type_requirement_gate.py tests/apps_lic/test_w5_message_quality.py tests/apps_lic/test_w5_sender_proof_graph.py tests/apps_lic/test_w6_whole_message_generation.py tests/apps_lic/test_w6_x1d_judge_policy.py tests/apps_lic/test_w7_blocked_artifact_ux.py tests/apps_lic/test_w7_validation_exit.py tests/apps_lic/test_w8_aig_30_profile_e2e.py -q` -> 155 passed, 1 skipped, 3 warnings.

Final W8 artifact summary:

- `strict_target_fit_fake`:
  - acceptance passed: true.
  - final matrix result: `strict_target_fit_fake_passed`.
  - final matrix passed: true.
  - clear drafts: 24.
  - blocked/review: 6.
  - remediation required: 0.
  - unexpected gaps: 0.
- `all_clear_eligible_fake`:
  - acceptance passed: false.
  - final matrix result: `expected_remediation_required`.
  - final matrix passed: true.
  - clear drafts: 24.
  - blocked/review: 6.
  - remediation required: 6.
  - unexpected gaps: 0.
- `all_clear_eligible_live`:
  - acceptance passed: false.
  - final matrix result: `failed_closed_unavailable_judge`.
  - final matrix passed: true.
  - clear drafts: 24.
  - blocked/review: 6.
  - remediation required: 6.
  - unexpected gaps: 0.
  - live preflight: `CLAUDE_X1D_PREFLIGHT_UNAVAILABLE`.
  - Anthropic API key present: false.

Broad-suite note:

- `python -m pytest tests/apps_lic -q` was also run for visibility and is not clean: 414 passed, 1 skipped, 167 failed, 8 errors, 5 warnings.
- The broad failures are outside the W0-W8 redesign harness and concentrate in older canonical U0/L1/C0/E2E surfaces, including U0 silent-drop handling for `/research_requirements/allow_research`, FEC/C0 bridge expectations, and missing legacy imports for `get_gateway` / `get_fabric`.

Notes:

- No live Anthropic API call was made in W8 because `ANTHROPIC_API_KEY` was not present in the environment.
- Fake/fixture judge receipts still cannot prove live Claude clearance.
- W8 does not weaken C0 evidence, W4/W6 policies, X2 gates, no-send policy, or Exit clearance.

Next: If needed, open a separate legacy-stability plan for the broad `tests/apps_lic` failures; W0-W8 closeout is complete.
