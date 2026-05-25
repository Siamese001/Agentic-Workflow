# Same-Authority Incremental Regen — Envelope Spec v1

**Plan:** `core-same-authority-incremental-regen-e7a4b1`  
**ADR:** [`ADR-085-same-authority-incremental-regen.md`](../../adr/ADR-085-same-authority-incremental-regen.md)  
**Schema version:** `1.0.0`

## Purpose

Normative field contract for `IncrementalRepairContract` (input) and `SameAuthorityRegenReceipt` (output). All instances MUST participate in the spine contract chain — no loose JSON sidecars.

## Stage placement

```
E3 AttemptReceipt (failure / SOFT_REPAIRABLE)
  → E4 LOCAL_REPAIR_EVALUATION
  → E4 SameAuthorityRegenRunner (incremental_delta_turn_v1)
  → SameAuthorityRegenReceipt (HealReceipt-compatible)
  → E3 retry OR E5 seal
```

Producer: `L2_E4_HEAL`. Consumer: `L2_E3_EXEC` or `L2_E5_SEAL`.

## Base spine envelope (both contracts)

Required on every contract instance (wrap or embed [`RuntimeIdentityEnvelope`](../../../agentic_core/runtime/contracts/identity.py)):

| Field | Type | Rule |
|-------|------|------|
| `contract_type` | string | `IncrementalRepairContract` \| `SameAuthorityRegenReceipt` |
| `contract_version` | string | Semver; initial `1.0.0` |
| `producer_stage` | string | `L2_E4_HEAL` |
| `consumer_stage` | string | `L2_E3_EXEC` \| `L2_E5_SEAL` |
| `request_id` | string | Non-empty |
| `run_id` | string | Non-empty |
| `trace_root` | string | Non-empty |
| `parent_contract_ref` | string | `AttemptReceipt` id or prior heal id |
| `contract_digest` | string | Canonical SHA-256 of stable fields |
| `policy_hash` | string | Unchanged vs parent attempt |
| `blueprint_hash` | string | Unchanged vs parent attempt |
| `registry_digest_set` | string[] | Unchanged vs parent attempt |
| `l5_governance_context_digest` | string | Carried; L5 does not execute repair |
| `runtime_gate_refs` | string[] | 00C G19/G20/G21/G24 visibility refs |
| `receipt_refs` | string[] | Linked artifact paths |
| `replay_key` | string | Unchanged vs parent attempt |
| `authority_scope` | string | `same_authority_no_commit` |
| `data_boundary_labels` | string[] | Origin tags from compile |
| `audit_manifest_ref` | string | Optional audit linkage |

## IncrementalRepairContract (input to runner)

| Field | Type | Source | Rule |
|-------|------|--------|------|
| `frozen_compile_ref` | string | Core | Path or digest ref to **unchanged** `CompiledPromptArtifact` |
| `parent_attempt_receipt_id` | string | Core | E3 attempt being healed |
| `anchor_output_hash` | string | Core | Hash of model output to anchor |
| `anchor_classification` | enum | **App** | `last_approved` \| `degraded_anchor_allowed` \| `refuse_unsafe` |
| `anchor_x2_snapshot_ref` | string? | App | Path to pre-regen X2 snapshot |
| `defect_class` | enum | App | Must be `SOFT_REPAIRABLE` for accept |
| `trigger_source` | enum | App | `X2` \| `X3_JUDGE` \| `OUTPUT_SCHEMA` \| `APP_MAPPER` |
| `delta_lines` | string[] | App mapper | Non-empty; subject to delta shape guard |
| `max_semantic_regen_attempts` | int | App `regen_policy.v1.yaml` | Default **1** |
| `max_delta_lines` | int | App policy | Core default cap 20 if unset |
| `max_delta_tokens` | int | App policy | Required for enforcement |
| `provider_lane` | string | Frozen compile | Must match parent |
| `model_lane` | string | Frozen compile | Must match parent |
| `degraded_anchor_allowed` | bool | App policy | Explicit opt-in |

Core MUST NOT interpret X2 gate IDs or rubric text when validating `anchor_classification`.

## SameAuthorityRegenReceipt (output)

Extends HealReceipt v4 fields: `repair_attempt_id`, `parent_attempt_receipt_id`, `determinism`, `lineage`, `before_hash`, `after_hash`, `repair_tactic=incremental_delta_turn_v1`, `next_action`.

| Field | Type | Rule |
|-------|------|------|
| `semantic_regen_attempt_index` | int | Monotonic; compared to ceiling before dispatch |
| `transport_retry_count` | int | Provider transport only; never increments semantic index |
| `max_semantic_regen_attempts` | int | Copied from contract at heal time |
| `semantic_regen_budget_exhausted` | bool | `true` on terminal heal from ceiling |
| `trigger_source` | enum | Echo from contract |
| `frozen_compile_ref` | string | Same ref as input |
| `delta_message_hash` | string | Hash of REGEN_DELTA user turn only |
| `prior_output_hash` | string | Pre-regen |
| `regenerated_output_hash` | string | Post-regen |
| `provider_request_ref` | string | Artifact with `messages[]` proof |
| `provider_response_ref` | string | Post-regen response artifact |
| `anchor_classification` | enum | Echo from app |
| `same_authority_assertions` | object | Per-check pass/fail map |
| `no_prompt_recompile_assertion` | bool | Must be `true` on accept |
| `no_provider_substitution_assertion` | bool | Must be `true` on accept |
| `no_app_policy_decision_assertion` | bool | Core did not set X3/disposition |
| `heal_outcome` | enum | Aligns `HealOutcomeStamp` / terminal classes |
| `refusal_code` | string? | Set when runner refuses (see refusal table) |

### Provider request proof (live Brown)

`provider_request_ref` artifact MUST satisfy:

1. Same `model` / `provider` (or lane ids) as parent attempt.
2. `messages[]`: system (+ developer if any) → assistant anchor → single REGEN_DELTA user turn.
3. `system_prefix_hash` equals `frozen_compile_ref` / `compilation_hash`.
4. No PA recompile timestamps or new `compilation_hash` on regen request.

## Refusal codes

| Code | When |
|------|------|
| `missing_frozen_compile_ref` | No compile ref |
| `missing_anchor_output` | No anchor hash |
| `empty_delta_lines` | Mapper empty |
| `provider_substitution` | Lane/model drift |
| `prompt_recompile` | PA/slot mutation |
| `full_rewrite_delta` | Full prompt replacement |
| `semantic_regen_budget_exhausted` | Index > ceiling |
| `recursive_regen_forbidden` | Nested regen without new attempt |
| `anchor_unsafe` | `refuse_unsafe` classification |
| `anchor_x2_red_not_soft_repairable` | Unsafe anchor without app soft-repairable |
| `delta_line_budget_exceeded` | Too many lines |
| `delta_token_budget_exceeded` | Token cap |
| `delta_shape_forbidden` | Section/rubric/schema leakage |
| `delta_instruction_reset` | Reset language detected |
| `authority_blocked` | Authority/ACL/HITL/sandbox blockers |
| `mocked_provider_allow` | Mock claimed as ALLOW |

## App policy schema (`regen_policy.v1.yaml`)

Core validates schema only; apps author values.

```yaml
# regen_policy.v1.yaml (app-owned)
schema_version: "1.0"
max_semantic_regen_attempts: 1   # default 1; explicit opt-in for >1
max_delta_lines: 20
max_delta_tokens: 512
degraded_anchor_allowed: false
```

## 00C / L5 / Exit touchpoints

| Layer | Role at regen |
|-------|----------------|
| 00C G19/G20/G24 | Visible in `runtime_gate_refs`; budget/replay/schema — no new authority |
| 00C G21 | Schema visibility when output-schema trigger |
| L5 | `l5_governance_context_digest` carried; L5 does not repair, approve, or commit |
| Exit | Sole emitter of final current-run disposition |

## Implementation waves

| Wave | Delivers |
|------|----------|
| W0 | This spec + ADR-085 + migration receipt (no runtime code) |
| W1 | `PromptMessages.append_same_authority_turn` + NC tests |
| W2 | Runner + receipt dataclasses + refusal tests |
| W3 | apps_rg delegation + live Brown proof |
