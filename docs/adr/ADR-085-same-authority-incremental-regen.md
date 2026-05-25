# ADR-085: Same-Authority Incremental Regen as L2 E4 Heal Subtype

**Status:** Accepted (W0)  
**Date:** 2026-05-25  
**Plan:** `core-same-authority-incremental-regen-e7a4b1`  
**Envelope spec:** [`docs/reference/L2_execution/same_authority_regen_envelope_spec_v1.md`](../reference/L2_execution/same_authority_regen_envelope_spec_v1.md)

> **Note:** ADR-083 is reserved for apps_rg PA ownership boundary. This regen chassis uses ADR-085.

## Context

`apps_rg` executive-summary judge remediation can append a prescriptive **REGEN_DELTA** user turn after X1D soft-fail, but implementation lives in-app only. Brown run `exec_summary_20260525_101226` showed regen **revert** because post-regen X2 failed — indicating regen must preserve frozen compile and same provider authority, not re-teach synthesis.

Core already defines:

- L2 sequencer states `LOCAL_REPAIR_EVALUATION` → `RETRYING_SAME_AUTHORITY` ([`l2_sequencer_contract.py`](../../agentic_core/L2_execution/types/l2_sequencer_contract.py))
- `AttemptReceipt` (E3) and `HealReceipt` (E4.7) ([`l2_v3_receipts.py`](../../agentic_core/L2_execution/types/l2_v3_receipts.py))
- `CompiledPromptArtifact` with `replay_key`, `l5_certification_ref` ([`compiled_prompt_artifact.py`](../../agentic_core/runtime/contracts/compiled_prompt_artifact.py))

There is no generic chassis for immutable-prefix multi-turn regen with semantic vs transport budget separation.

## Decision

Add `agentic_core/L2_execution/regen/` as **E4 Heal subtype** `repair_tactic=incremental_delta_turn_v1`:

| Component | Role |
|-----------|------|
| `IncrementalRepairContract` | Spine envelope + app-supplied anchor/delta inputs |
| `SameAuthorityRegenRunner` | E4-only runner; ceiling, delta shape, anchor enum enforcement |
| `SameAuthorityRegenReceipt` | HealReceipt-compatible; semantic/transport counters separated |
| `RemediationDeltaMapper` | Protocol only — apps implement |
| `delta_shape_guard.py` | App-agnostic structural refusal (line/token/reset language) |

**Entry:** Only after `SOFT_REPAIRABLE` classification from `AttemptReceipt` or app judge/gate feedback.

**Exit:** `RETURN_TO_E3` on success; terminal heal → `SEND_TO_E5` / `NEEDS_HELP` on budget exceed or refusal.

**Default policy:** `max_semantic_regen_attempts: 1` unless app `regen_policy.v1.yaml` opts higher.

## Boundary (mirror ADR-082)

| Core owns | Apps own |
|-----------|----------|
| Thread topology, frozen prefix guards | Trigger policy, mapper delta lines |
| REGEN_DELTA / PROMPT_LOCK generic text | Rubric, X2 gates, X3 disposition |
| Semantic ceiling enforcement | Anchor safety classification |
| Receipt schema + provider `messages[]` dispatch | X2 re-check, judge rescore |

Core must not import `apps_rg` or embed section/rubric/X2 gate literals.

## Consequences

- **Positive:** Regen extends Heal receipt chain; prevents hidden iterative rewriting; reusable by `apps_*`.
- **Negative:** Requires `apps_rg` W3 delegation; dual path until lane migrates off in-app regen.
- **Migration:** W1–W3 per plan; W4 `JudgeDirectedRegenOrchestrator` blocked until live Brown proof.

## Non-goals

- X3 operator policy or 2-of-3 judge quorum in core
- L5 executing repair or emitting disposition
- `JudgeDirectedRegenOrchestrator` on MVP path (W4+)
- Replacing app-owned X2 validators or rubrics

## Related

- ADR-082 — multi-provider judge panel harness (precedent for core/apps split)
- ADR-083 — apps_rg PA ownership (separate concern; number not reused here)
