---
plan_id: core-same-authority-incremental-regen-e7a4b1
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: artifacts/governance/migration_receipts/20260525_core_same_authority_incremental_regen_w0.json
dod_exempt: false
---

# Agentic Core — Same-Authority Incremental Regen Chassis (vLLM / Qwen)

**North star:** Incremental regen is **first-class L2 E4 Heal** — not a parallel execution path. After an `AttemptReceipt` or judge/gate feedback identifies a **SOFT_REPAIRABLE** semantic defect, `SameAuthorityRegenRunner` appends one bounded **REGEN_DELTA** user turn under a **frozen** `CompiledPromptArtifact`, invokes the **same** provider lane, emits a **HealReceipt-compatible** `SameAuthorityRegenReceipt`, and returns to **L2 E3 retry** or **L2 E5 seal**. It must not bypass `SealedL2Artifact`, `ExitReviewPacket`, app-owned X1/X2/X3, or durable commit.

**Problem this solves:** `apps_rg` prescriptive delta regen works in-app only; core has `JudgePanelRunner`, `HealReceipt`, and sequencer state `RETRYING_SAME_AUTHORITY` ([`l2_sequencer_contract.py`](../agentic_core/L2_execution/types/l2_sequencer_contract.py)) but no generic immutable-prefix regen chassis. Without it, regen re-teaches the compile (Brown `101226`: X2 fail → revert).

**Anti-pattern (forbidden):** Rubric prose, X2 gate IDs, X3 policy, section schemas, or app orchestration in `agentic_core`. **Forbidden side channel:** regen that skips E4 Heal receipts, mutates frozen compile, substitutes provider/model, or treats `JudgePanelRunner` transport retries as semantic regen proof.

**Related:**
- [`core-judge-panel-harness-f3c8d1.md`](core-judge-panel-harness-f3c8d1.md) — **DONE**
- [`exec-summary-x1d-transport-parity-d8f2a1.md`](exec-summary-x1d-transport-parity-d8f2a1.md) — **DONE**
- [`exec-summary-operator-ship-a3f7c2.md`](exec-summary-operator-ship-a3f7c2.md) — X3 operator semantics (app Exit)
- [`exec-summary-l2-x1d-input-parity-c4f8e1.md`](exec-summary-l2-x1d-input-parity-c4f8e1.md) — L2/judge parity (apps)

> **plan_id discipline:** `core-same-authority-incremental-regen-e7a4b1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
PLAN_HARDENING: applied_2026-05-25 execution_contract_v3
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-25
PLAN_COMPLETE: plan=core-same-authority-incremental-regen-e7a4b1 note="W0–W3 DONE: core SameAuthorityRegenRunner + apps_rg delegation + Brown live proof; W4 orchestrator DEFERRED per PD-8"
DEFERRED_SCOPE_FOLLOWUP: plan=exec-summary-judge-regen-loop-closure-d8f3a1 path=.cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md note="W4 + DS-1..DS-8 loop closure (post-regen X2, lane unify, orchestrator, Brown re-proof)"
EXECUTION_APPROVED: true
WAVE_COMPLETE: plan=core-same-authority-incremental-regen-e7a4b1 wave=0 note="ADR-085 + envelope spec v1 + migration receipt + author gate dominance_fires"
WAVE_COMPLETE: plan=core-same-authority-incremental-regen-e7a4b1 wave=1 note="append_same_authority_turn + vLLM messages[] + NC-1..NC-3 pytest"
WAVE_COMPLETE: plan=core-same-authority-incremental-regen-e7a4b1 wave=2 note="SameAuthorityRegenRunner + receipt + delta guards + boundary CI"
WAVE_COMPLETE: plan=core-same-authority-incremental-regen-e7a4b1 wave=3 note="apps_rg delegation + Brown exec_summary_20260525_122058 live regen artifacts + receipt"

NOTION_PAGE_ID: 36b27693-f55c-81d2-a344-fded674227f6
NOTION_PLAN_URL: https://www.notion.so/core-same-authority-incremental-regen-e7a4b1-36b27693f55c81d2a344fded674227f6

PLAN_CREATED: slug=core-same-authority-incremental-regen-e7a4b1 path=.cursor/plans/core-same-authority-incremental-regen-e7a4b1.md status=Not Started notion_page=36b27693-f55c-81d2-a344-fded674227f6

---

## L2 Spine Placement (mandatory — not a parallel path)

Incremental regen is an **E4 Heal subtype**: `repair_tactic=incremental_delta_turn_v1`.

| Rule | Requirement |
|------|-------------|
| Entry | `SameAuthorityRegenRunner` runs **only** from L2 **E4 Heal** after `AttemptReceipt` and/or app-supplied judge/gate feedback classifies defect as **`SOFT_REPAIRABLE`** (`ResultClass` / `HealOutcomeStamp` alignment per [`l2_v3_receipts.py`](../agentic_core/L2_execution/types/l2_v3_receipts.py)). |
| Sequencer | Must transition via `LOCAL_REPAIR_EVALUATION` → `RETRYING_SAME_AUTHORITY` → back to `VALIDATED`/`EXECUTING` per [`L2SequencerState`](../agentic_core/L2_execution/types/l2_sequencer_contract.py). |
| Receipt | Emit **`SameAuthorityRegenReceipt`** that is **HealReceipt-compatible** (extends/wraps v4 `HealReceipt` fields: `repair_attempt_id`, `parent_attempt_receipt_id`, `determinism`, `lineage`, `before_hash`/`after_hash`, `next_action=RETURN_TO_E3`). |
| Exit path | On success → **L2 E3 retry** with regenerated output; on terminal heal fail → **E5 seal** / `NEEDS_HELP` — never direct Exit X3 from core. |
| Forbidden bypass | Must **not** skip `SealedL2Artifact`, `ExitReviewPacket`, app X1/X2/X3, UWG commit, or L6 learn-while-run. |

**Rationale:** Spine already defines Heal as same route, policy, blueprint, sandbox, capability, replay key, no durable commit. Regen **extends** Heal — it does not create a side channel.

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | Regen modules are app-agnostic (static boundary tests — see §Boundary). |
| INV-2 | Frozen compile immutable: system/developer/slot snapshot unchanged across regen. |
| INV-3 | Delta turn = generic `REGEN_DELTA` envelope (core) + app `delta_lines` only. |
| INV-4 | **`semantic_regen_attempt_index`** ≠ **`transport_retry_count`**; panel/HTTP retries never satisfy semantic regen DoD. |
| INV-5 | App-owned: trigger policy, floors, X2 re-check, judge rescore, X3 consequence. |
| INV-6 | No FAIL→PASS laundering in core regen path. |
| INV-7 | Mocked/UNKNOWN provider ≠ runtime ALLOW. |
| INV-8 | Migration receipt + populated `author_gate_receipt_ref` before merge. |
| INV-9 | W4 `JudgeDirectedRegenOrchestrator` **blocked** until W1–W3 live proof (not MVP). |
| INV-10 | All regen receipts participate in spine contract chain (§Envelope). |
| INV-11 | **Semantic regen ceiling** enforced (`max_semantic_regen_attempts`); no recursive regen loops. |
| INV-12 | **Anchor safety** classified by app only; core refuses unsafe anchors. |

---

## Semantic regen attempt ceiling (required)

`SameAuthorityRegenRunner` enforces a **hard semantic repair budget**, separate from provider transport retry. Prevents judge-driven regen from becoming hidden iterative rewriting.

| Rule | Requirement |
|------|-------------|
| Source | `max_semantic_regen_attempts` from app `regen_policy.v1.yaml` (core validates schema only). |
| Default | **`1`** unless app explicitly opts into a higher ceiling. |
| Counter | `semantic_regen_attempt_index` is monotonic per packet family; compared against ceiling **before** provider dispatch. |
| Over budget | Return **terminal heal failure** → **E5 seal** / `NEEDS_HELP` (`next_action=SEND_TO_E5`); emit receipt with `heal_outcome=FAIL_TERMINAL` or `NEEDS_HELP` per app policy. |
| No recursion | **Forbidden:** regen-on-regen chains, nested heal loops, or implicit re-entry without a new `AttemptReceipt` + fresh app trigger. One semantic regen per heal evaluation unless app ceiling > 1 and app re-triggers explicitly. |
| Transport | `transport_retry_count` and HTTP/panel retries **do not** consume semantic budget. |

**Receipt fields (add):** `max_semantic_regen_attempts`, `semantic_regen_budget_exhausted` (bool when terminal).

---

## Anchor safety (required — app classifies, core enforces)

`anchor_output_hash` is required, but **core must not decide anchor safety**. App mapper supplies classification; core enforces.

| Rule | Requirement |
|------|-------------|
| Safe anchor | Anchor output must be the **last app-approved candidate** OR explicitly **`degraded_anchor_allowed`** per app `regen_policy.v1.yaml`. |
| X2-red refusal | If prior output is X2-red for **authority / ledger / schema safety**, regen **must refuse** unless app mapper classifies defect as **`SOFT_REPAIRABLE`** **and** anchor as **`anchor_safe`** or **`degraded_anchor_allowed`**. |
| Core role | Core validates presence + enum of `anchor_classification` on `IncrementalRepairContract`; **no** X2 gate ID logic or rubric interpretation in core. |
| App role | App mapper / lane sets `anchor_classification`: `last_approved` \| `degraded_anchor_allowed` \| `refuse_unsafe`. |

**Receipt fields (add):** `anchor_classification`, `anchor_x2_snapshot_ref` (app artifact path, optional).

**Failure codes (add):** `anchor_unsafe`, `anchor_x2_red_not_soft_repairable`.

---

## Core vs App Boundary (locked)

### Core MAY own

- Message thread topology (`append_same_authority_turn`, `to_chat_messages`)
- Immutable prefix enforcement + negative-control tests
- Generic `REGEN_DELTA` / `PROMPT_LOCK` envelope text
- Semantic vs transport attempt budgets, **ceiling enforcement**, and counters
- **Delta size/shape guards** (§Delta guards) — structural refusal only, no rubric text
- `SameAuthorityRegenReceipt` / `IncrementalRepairContract` schema
- Provider multi-turn dispatch (vLLM `messages[]`)
- OTel spans (`l2.regen.delta_turn`, `l2.heal.incremental_delta`)
- E4 Heal subtype wiring + refusal guards (§Failure modes)

### Apps MUST own

- Trigger policy (quorum, solitary soft-fail, X2-green prerequisite)
- **`max_semantic_regen_attempts`** in `regen_policy.v1.yaml` (default 1)
- **Anchor safety classification** (`last_approved`, `degraded_anchor_allowed`, refuse unsafe)
- `RemediationDeltaMapper` — delta line generation
- App-specific monotonicity floors (word count, ledger, sentence count)
- X2 re-check after regen
- Judge rescore mode (`soft_failed_only` vs `full_panel`)
- Disposition consequence (X3 / ExitReviewPacket)
- Section/schema/rubric vocabulary

### Static boundary tests (required — W2/W3)

New `agentic_core` regen modules must contain **none** of:

- `apps_rg` / `apps_lic` imports
- Resume/section literals (`executive_summary`, `resume_display_text` as gate names in core)
- Executive-summary rubric text / `GRAPH_ONLY_GRADE_ONLY_RUBRIC`
- X2 gate IDs (`x2_exec_summary_*`)
- X3 operator policy strings
- Brown-specific role strings (`Brown & Brown`, target title literals)
- Section JSON output schemas

**Proof:** `tests/unit/agentic_core/.../test_regen_core_boundary.py` + CI gate `check_same_authority_regen_boundary.py` (extend panel boundary pattern).

---

## Spine Contract Envelope (required — no loose receipts)

`IncrementalRepairContract` and `SameAuthorityRegenReceipt` MUST include standard spine envelope fields (or wrap `RuntimeIdentityEnvelope` + stage metadata). Minimum surface:

| Field | Purpose |
|-------|---------|
| `contract_type` | e.g. `IncrementalRepairContract` / `SameAuthorityRegenReceipt` |
| `contract_version` | Semver for schema evolution |
| `producer_stage` | `L2_E4_HEAL` |
| `consumer_stage` | `L2_E3_EXEC` or `L2_E5_SEAL` |
| `request_id`, `run_id`, `trace_root` | Identity chain |
| `parent_contract_ref` | Prior `AttemptReceipt` or heal parent |
| `contract_digest` | Canonical hash |
| `policy_hash`, `blueprint_hash`, `registry_digest_set` | Determinism bundle |
| `l5_governance_context_digest` | Carried, not executed by L5 |
| `runtime_gate_refs` | 00C gate refs visible at regen boundary |
| `receipt_refs` | Linked provider request/response artifacts |
| `replay_key` | Unchanged across regen |
| `authority_scope` | `same_authority_no_commit` |
| `data_boundary_labels` | Origin tags preserved |
| `audit_manifest_ref` | Audit linkage |

Align with [`RuntimeIdentityEnvelope`](../agentic_core/runtime/contracts/identity.py) and [`CompiledPromptArtifact`](../agentic_core/runtime/contracts/compiled_prompt_artifact.py) replay/provenance fields.

---

## SameAuthorityRegenReceipt — required fields

Do **not** conflate with `JudgePanelRunner.max_attempts` or HTTP retry counters.

| Field | Required |
|-------|----------|
| `semantic_regen_attempt_index` | Monotonic per packet family (E4 semantic repair count) |
| `transport_retry_count` | Separate; from provider transport only |
| `trigger_source` | `X2` \| `X3_JUDGE` \| `OUTPUT_SCHEMA` \| `APP_MAPPER` |
| `frozen_compile_ref` | Stable ref to **prior** `CompiledPromptArtifact` (compilation_hash / prompt_hash) |
| `anchor_output_hash` | Hash of anchored prior output |
| `delta_message_hash` | Hash of REGEN_DELTA user turn only |
| `prior_output_hash` | Pre-regen model output |
| `regenerated_output_hash` | Post-regen model output |
| `provider_request_ref` | Artifact path to request with `messages[]` |
| `provider_response_ref` | Artifact path to response |
| `same_authority_assertions` | Structured pass/fail checks |
| `no_prompt_recompile_assertion` | Must be `true` when regen accepted |
| `no_provider_substitution_assertion` | Must be `true` when regen accepted |
| `no_app_policy_decision_assertion` | Core did not apply X3/disposition |
| `max_semantic_regen_attempts` | Ceiling from app policy at heal time |
| `semantic_regen_budget_exhausted` | `true` when terminal heal due to ceiling |
| `anchor_classification` | App-supplied: `last_approved` \| `degraded_anchor_allowed` |

**Immutable-prefix proof:** regen preserves prior `CompiledPromptArtifact` ref; only `delta_message_hash` is new content.

---

## Delta size / shape guards (required — W2)

Core refuses mapper output that structurally resembles a **full prompt rewrite** (before provider dispatch):

| Guard | Refuse when |
|-------|-------------|
| Line budget | Delta line count exceeds app `regen_policy.v1.yaml` `max_delta_lines` (core default cap if unset: **20**). |
| Token budget | Estimated delta tokens exceed app `max_delta_tokens` (core enforces numeric limit from policy schema). |
| Section leakage | Delta contains `system`, `developer`, `rubric`, `schema`, `OUTPUT_SCHEMA`, or `GRAPH_ONLY` section headers. |
| Full output blob | Delta contains full résumé/section output body (heuristic: multiline block > N chars matching prior `anchor_output_hash` span). |
| Instruction reset | Delta contains `ignore previous`, `disregard above`, `new instructions`, `forget the prompt`, or equivalent reset language (case-insensitive). |
| Full rewrite | Same as `full_rewrite_delta` — mapper returned re-teach / full prompt replacement. |

**Failure codes:** `delta_line_budget_exceeded`, `delta_token_budget_exceeded`, `delta_shape_forbidden`, `delta_instruction_reset`.

**App policy fields (schema):** `max_delta_lines`, `max_delta_tokens`, `max_semantic_regen_attempts`, `degraded_anchor_allowed`.

---

## Negative-control tests (required — W1)

| Test | Must |
|------|------|
| NC-1 | Mutating system/developer/slot snapshot **after** `append_same_authority_turn` → **fail** (immutable prefix guard). |
| NC-2 | Changing `prompt_hash`, `policy_hash`, `blueprint_hash`, `registry_digest_set`, `capability_token`, `sandbox_envelope`, `provider_lane`, `model_lane`, or `replay_key` across regen → **fail**. |
| NC-3 | Same-authority regen preserves prior compiled prompt artifact ref; emits **new** `delta_message_hash` only. |

---

## Failure-mode refusals (required — W2)

`SameAuthorityRegenRunner` MUST refuse (structured error, no silent degrade):

| Code | Condition |
|------|-----------|
| `missing_frozen_compile_ref` | No artifact ref |
| `missing_anchor_output` | No prior output to anchor |
| `empty_delta_lines` | Mapper returned nothing |
| `provider_substitution` | Provider/lane/model change vs parent attempt |
| `prompt_recompile` | New PA compile or slot mutation detected |
| `full_rewrite_delta` | App mapper returned full rewritten prompt / re-teach blob |
| `unknown_validation_status` | Unclassified defect |
| `mocked_provider_allow` | Mocked provider claimed as runtime ALLOW |
| `missing_authority_refs` | policy/blueprint/registry/replay refs absent or drift |
| `authority_blocked` | X2/gate failure = missing authority, blocked ACL, stale policy, route mismatch, stale registry, sandbox gap, HITL need, capability expansion, direct-write bypass |
| `semantic_regen_budget_exhausted` | `semantic_regen_attempt_index` > `max_semantic_regen_attempts` |
| `recursive_regen_forbidden` | Nested regen without new attempt + app trigger |
| `anchor_unsafe` | App `anchor_classification=refuse_unsafe` or missing classification |
| `anchor_x2_red_not_soft_repairable` | X2-red anchor without soft-repairable + anchor-safe app classification |
| `delta_line_budget_exceeded` | §Delta guards |
| `delta_token_budget_exceeded` | §Delta guards |
| `delta_shape_forbidden` | §Delta guards (section/rubric/schema leakage) |
| `delta_instruction_reset` | §Delta guards (instruction-reset language) |

---

## 00C and L5 touchpoints (visibility only — no new authority)

| Layer | Requirement |
|-------|-------------|
| **00C** | G19/G20/G24 (and G21 where applicable) visible on regen budget, replay, schema receipts — regen does not consume new 00C authority. |
| **L5** | `l5_governance_context_digest` / `l5_certification_ref` **carried** into regen contract; L5 does **not** execute, repair, approve output, emit X3, or commit. |
| **Exit** | Remains **only** layer emitting final current-run disposition (app `ExitReviewPacket`). |

---

## Product Decisions (lock W0)

| ID | Decision |
|----|----------|
| PD-1 | Package: `agentic_core/L2_execution/regen/` — E4 Heal subtype SSOT. |
| PD-2 | `PromptMessages.append_same_authority_turn` + immutability guards. |
| PD-3 | `RemediationDeltaMapper` protocol — apps only. |
| PD-4 | Core owns generic `PROMPT_LOCK`; apps remove duplicate ownership in W3. |
| PD-5 | vLLM `messages[]` multi-turn. |
| PD-6 | App `regen_policy.v1.yaml` — core validates schema only. |
| PD-7 | W3: `apps_rg` delegates; preserves app floors in mapper. |
| PD-8 | **W4 orchestrator explicitly DEFERRED** — blocked until W1–W3 proof (PD-9). |
| PD-9 | HealReceipt compatibility: `SameAuthorityRegenReceipt` extends E4.7 shape. |
| PD-10 | `max_semantic_regen_attempts` default **1**; terminal heal on exceed. |
| PD-11 | Anchor safety: app classifies; core enforces enum + refusal. |

---

## Core Module Map (MVP path only)

| Module | Responsibility |
|--------|----------------|
| `regen/incremental_repair_contract.py` | Envelope + `IncrementalRepairContract` + validation |
| `regen/delta_shape_guard.py` | Line/token/shape/reset guards (app-agnostic heuristics) |
| `regen/same_authority_regen_runner.py` | E4 subtype runner; ceiling + refusal guards |
| `regen/same_authority_regen_receipt.py` | `SameAuthorityRegenReceipt` + HealReceipt bridge |
| `regen/remediation_delta_mapper.py` | Protocol only |
| `prompt_messages.py` (extend) | Frozen append + NC guards |
| `_provider_local_vllm.py` (extend) | `messages[]` |
| `tests/.../test_regen_*` | NC, failure-mode, boundary |
| `tools/ci/check_same_authority_regen_boundary.py` | Static leakage gate |

**Deferred (W4+ — blocked for MVP):**

| Module | Status |
|--------|--------|
| `judge_directed_regen.py` | **BLOCKED** until W3 live Brown proof passes DoD-5 |

---

## Execution Order (MVP = W0–W3 only)

| Wave | Focus | Est. Tokens |
|------|-------|-------------|
| **W0** | ADR-085, Author-Gate receipt populated, envelope spec | ~45K |
| **W1** | Thread + immutability NC tests + vLLM `messages[]` | ~90K |
| **W2** | E4 runner + receipt schema + refusal tests + boundary CI | ~110K |
| **W3** | apps_rg delegation + **live Brown proof** | ~90K |
| ~~W4~~ | ~~Orchestrator~~ | **DEFERRED** — see PD-8 |

**W4 unblock criteria (all required):**

1. W1 NC tests green (immutable prefix, no hash drift).
2. W2 `SameAuthorityRegenReceipt` + semantic/transport counter separation proven in tests.
3. W3 apps_rg delegation removes duplicate `PROMPT_LOCK` from apps; app floors preserved.
4. W3 live Brown: X2-green **after** regen, **before** judge rescore; real judge/gate trigger — not fixture/smoke/docs-only.

---

## Status Tables

### Wave Summary

| Wave | Status | Success Criteria |
|------|--------|------------------|
| W0 | ✅ DONE | ADR-085 + **populated** `author_gate_receipt_ref` + migration receipt |
| W1 | ✅ DONE | NC-1..NC-3 PASS; vLLM `messages[]` unit proof |
| W2 | ✅ DONE | Runner refusals + ceiling/anchor/delta guards + boundary CI PASS |
| W3 | ✅ DONE | Brown `exec_summary_20260525_122058` + [receipt](../docs/reports/apps_rg/core_same_authority_regen_brown_20260525_122058_receipt.md) |
| W4 | **DEFERRED** | PD-8 — orchestrator; unblock criteria not met (post-regen X2 revert on Brown) |

### Phase-Level Summary

| Phase | Title | Status |
|-------|-------|--------|
| W0.0 | ADR-085 E4 incremental regen subtype | ✅ DONE |
| W0.1 | Author-Gate + [migration receipt](../artifacts/governance/migration_receipts/20260525_core_same_authority_incremental_regen_w0.json) | ✅ DONE |
| W0.2 | [Envelope spec v1](../docs/reference/L2_execution/same_authority_regen_envelope_spec_v1.md) + [regen_policy schema](../docs/reference/L2_execution/regen_policy.v1.schema.yaml) | ✅ DONE |
| W1.0 | `append_same_authority_turn` + immutability | ✅ DONE |
| W1.1 | vLLM multi-turn | ✅ DONE |
| W1.2 | NC-1..NC-3 tests | ✅ DONE |
| W2.0 | `SameAuthorityRegenRunner` E4 wiring | ✅ DONE |
| W2.1 | `SameAuthorityRegenReceipt` + HealReceipt bridge | ✅ DONE |
| W2.2 | Failure-mode + delta guards + boundary CI | ✅ DONE |
| W2.3 | Semantic ceiling + anchor refusal tests | ✅ DONE |
| W3.0 | apps_rg mapper → core runner | Done |
| W3.1 | Lane E4 integration + artifact paths | Done |
| W3.2 | Live Brown proof receipt | Done — [core_same_authority_regen_brown_20260525_122058_receipt.md](../docs/reports/apps_rg/core_same_authority_regen_brown_20260525_122058_receipt.md) |
| W4.0 | Orchestrator | **BLOCKED** |

---

## Definition of Done

| ID | Criterion | Proof |
|----|-----------|-------|
| DoD-0 | `author_gate_receipt_ref` populated in plan frontmatter | Non-empty path in YAML |
| DoD-1 | NC-1..NC-3 + envelope validation tests PASS | `pytest tests/unit/agentic_core/.../regen/` |
| DoD-2 | Semantic vs transport counters separated in receipt | Unit test asserts `semantic_regen_attempt_index` ≠ panel `max_attempts` |
| DoD-3 | HealReceipt-compatible `SameAuthorityRegenReceipt` in contract chain | Schema test + `producer_stage=L2_E4_HEAL` |
| DoD-4 | apps_rg: core owns `PROMPT_LOCK`; apps own floors only | Grep + mapper tests |
| DoD-5 | **Live Brown** (narrowed — see below) | `docs/reports/apps_rg/core_same_authority_regen_brown_*_receipt.md` |
| DoD-6 | Static boundary gate PASS | `check_same_authority_regen_boundary.py` |
| DoD-7 | Notion Completed only after DoD-0–8 | `PLAN_COMPLETE` marker |
| DoD-8 | §Wave closeout commands all exit 0 | Receipt lists each command + exit code |
| DoD-8a | Semantic ceiling + anchor refusal tests PASS | W2.3 pytest |
| DoD-8b | Delta shape guard tests PASS | W2.2 pytest |
| DoD-8c | Provider request strict proof in live Brown | §Provider request proof rows |

### DoD-5 (replaces vague “regen does not break X2”)

Live Brown run MUST prove:

1. Regen triggered from **real** judge/gate delta (`trigger_source` + artifact evidence).
2. **Frozen compile / provider authority preserved** (`same_authority_assertions`, NC fields).
3. `SameAuthorityRegenReceipt` emitted with full required fields.
4. Regeneration through provider `messages[]` (not flat recompile).
5. App-owned **X2 passed after regen** before any judge rescore or X3 disposition claim.

**Non-claims:** If judge provider blocked or X3 is `REVIEW`, receipt must state explicitly — no PASS theater.

**Not accepted as DoD-5:** Unit tests alone, fixtures-only, smoke paths, docs-only receipts.

---

## Live Brown Proof Shape (W3.2 — mandatory artifact checklist)

| Artifact | Required content |
|----------|------------------|
| Command + exit code | Exact `python -m apps_rg ...` and exit code |
| `run_dir` | Under `artifacts/apps_rg/runtime_proofs/executive_summary/real/` |
| `compiled_prompt_artifact.json` | Pre-regen compile; hash stable across regen |
| `provider_request.json` | **Strict proof** (see §Provider request proof) |
| `provider_response.json` | Post-regen model output |
| `same_authority_regen_receipt.json` | All §Receipt fields + envelope fields |
| `x2_gate_outputs.json` (before) | Snapshot before regen |
| `x2_gate_outputs.json` (after) | All relevant gates pass post-regen |
| `x1d_llm_judge_outputs.json` | Shows real trigger (soft-fail / dimension lines) |
| `judge_remediation_cycles.json` | Regen accepted or reverted with reason |
| `x3_disposition.json` | Final disposition; explicit if REVIEW/BLOCKED |
| Trigger proof | Judge/gate feedback ≠ transport retry |
| X2 ordering proof | After-regen X2 pass **before** judge rescore in timeline |

### Provider request proof (strict — W3.2)

`provider_request.json` MUST demonstrate (hostile verifier checks in Brown receipt):

| Check | Required evidence |
|-------|-------------------|
| Same authority | `model` / `provider` (or lane ids) **identical** to parent `AttemptReceipt` / pre-regen provider request. |
| Thread shape | Full `messages[]`: frozen **system** (+ developer if present) → prior **assistant** output (anchor) → single bounded **user** REGEN_DELTA turn. |
| Prefix hash | `system_prefix_hash` (or equivalent) **equals** `frozen_compile_ref` / `compilation_hash` from `compiled_prompt_artifact.json`. |
| No recompile | No `prompt_assembly` / PA artifact regeneration timestamps; no new `compilation_hash` on regen request; `no_prompt_recompile_assertion=true` on receipt. |
| No re-render | Request body is thread append only — not a flat recompiled prompt string replacing the thread. |

Brown closeout receipt MUST cite pass/fail per row above.

---

## Wave closeout commands (required — Cursor must run and record)

Every wave closeout and final plan closeout MUST record **exact command + exit code** in the wave receipt / `docs/reports/apps_rg/core_same_authority_regen_*_receipt.md`.

### Core + CI (W1/W2 closeout and final)

```bash
python -m compileall agentic_core apps_rg -q
pytest tests/unit/agentic_core/L2_execution/regen/ -q
python tools/ci/check_same_authority_regen_boundary.py
```

Expected: all **exit 0**.

### apps_rg delegation (W3 closeout)

```bash
pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py tests/unit/apps_rg/test_same_authority_regen_delegation.py -q
```

(`test_same_authority_regen_delegation.py` — add in W3 if not present; path is the SSOT for mapper→core wiring tests.)

Expected: **exit 0**.

### Live Brown (W3.2 — mandatory)

```bash
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --provider qwen_vllm --allow-non-allow-exit-zero --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

(Set `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1` and `APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1` for regen path. Artifacts land under `artifacts/apps_rg/runtime_proofs/executive_summary/real/`.)

```bash
# legacy doc typo — flag does not exist on CLI:
# python -m apps_rg --section executive_summary --target-company "Brown & Brown" --proof-mode real
```

Record: **exit code**, `run_dir`, and full artifact checklist (§Live Brown Proof Shape + §Provider request proof).

**Final plan closeout:** run **all** commands above in order; none may be skipped for PASS.

---

## Merge Acceptance Gate

**No merge** until ALL:

- [x] W0 Author-Gate receipt populated (`author_gate_receipt_ref` non-empty)
- [x] W1/W2 core contract tests prove immutable-prefix + no-substitution
- [x] W3 apps_rg delegation: apps no longer own duplicate `PROMPT_LOCK`; app floors preserved
- [x] W3 live Brown receipt proves **canonical runtime** behavior (§Live Brown Proof Shape + §Provider request proof) — not fixture/smoke/docs-only
- [x] §Wave closeout commands recorded with exit 0 (compileall, pytest regen, boundary CI, apps delegation, live Brown)

---

## Out of Scope (moved to follow-up)

> **Follow-up plan:** [exec-summary-judge-regen-loop-closure-d8f3a1.md](exec-summary-judge-regen-loop-closure-d8f3a1.md) — Notion + disk; owns W4 and deferred scope register DS-1..DS-8.

- W4 `JudgeDirectedRegenOrchestrator` on MVP path → **follow-up W3**
- X3 policy / 2-of-3 judge quorum in core
- Rubric / X2 gate definitions in core
- L5 executing repair or emitting disposition
- Claude-as-author (same Qwen/vLLM profile from app)

---

## Reference: REGEN_DELTA envelope (apps reference → core generic)

```text
REGEN_DELTA_v1
PROMPT_LOCK   — core generic text; frozen compile authoritative
ANCHOR_*      — app names anchor field; core requires anchor_output_hash
JUDGE_DELTA   — app mapper delta_lines only
*_FLOOR       — app mapper floors (not in core envelope)
```
