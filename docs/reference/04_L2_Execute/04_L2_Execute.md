========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 04_L2_Execute.md
Layer / subsystem: 04 — L2 Execute (parent)
Parent file: docs/reference/README.md
Ownership surface: Bounded execution: E1 Prep, E2 Valid, E3 Exec, E4 Heal, E5 Seal; Programmatic Tool Calling sandbox; sealed L2 artifact; proposed_state_diff (inert until Exit); local verify-then-execute critique; L2 sequencer/orchestrator contract.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: L2 executes one packet or one step. It does not re-decide route (L0), expand workflow (L3), retrieve (C0), assemble prompts (PA), commit (UWG), approve (L5), evaluate (L6), or decide final disposition (Exit).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `04_L2_Execute.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the E1..E5 sub-stage handoff invariants (Prep → Valid → Exec → Heal → Seal)
- the rule that mutations are emitted only as `proposed_state_diff` (never durable writes)
- the rule that E2 validation and E4 heal use the **same** `blueprint_hash`, `policy_hash`, and replay snapshot
- the PTC sandbox invariants (no ambient tool use, raw outputs isolated)
- the sealed_l2_artifact emission contract

It does **not** own:
- per-stage detail (lives in `04.0`..`04.10`)
- routing, retrieval, prompt assembly, commit, approval, evaluation

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: signed `PromptEnvelope` (or `L3StepContract` for managed-workflow runs) plus capability_token, sandbox_envelope.
**Downstream outputs**: `sealed_l2_artifact`, `proposed_state_diff` (when applicable), tool/model receipts.
**Forbidden behaviors**: changing route, expanding hidden workflow, fetching evidence, mutating L4 directly, approving final output, escaping sandbox.
**Allowed outputs only**: prep_receipts, validation_receipts, attempt_receipts, heal_receipts, sandbox receipts, sealed_l2_artifact, proposed_state_diff, downstream recommendation as non-authoritative metadata.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L2-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-L2-NO-DIRECT-L4-WRITE-001` | L2 MUST NOT write to L4 directly. All durable mutations go through `proposed_state_diff` → Exit X1J → UWG. | 04 | (governance) | (none) | trace under `l2.*` shows no `uwg.commit` child | NOT_APPLICABLE: anti-pattern detection | `compiler_anti_cheat_findings.json` | `validator: l2_no_direct_l4_write_validator` (release-gate) | `NC-L2-DIRECT-L4-WRITE-001`: L2 attempts L4 mutation directly | `direct_l4_write_attempt` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-L2-ENTRY-AUTHORITY-001` | L2 MUST accept only a signed PromptEnvelope or current `L3StepContract`; raw inputs are FAIL. | 04.1 | upstream contract | accepted packet | input verified against HMAC sig; capability_token bound | `l2.entry` parent span | `l2_entry_receipt.json` | `validator: l2_entry_authority_validator` (release-gate) | `NC-L2-RAW-ENTRY-001`: L2 invoked without signed envelope | `l2_unsigned_entry` | `byte_identical` | DOC_ONLY |
| `REQ-L2-E1-PREP-RECEIPT-001` | E1 Prep MUST produce a `prep_receipt` with frozen execution context, environment digest, idempotency key, lineage root, write-lock assertion, and determinism bindings. | 04.2 | accepted packet | `prep_receipt` | all 6 fields present | `l2.e1_prep` span | `prep_receipt.json` | `validator: l2_e1_prep_validator` (release-gate) | `NC-L2-IDEMPOTENT-DUP-001`: same idempotency key processes twice | `l2_idempotency_violation` | `byte_identical` | DOC_ONLY |
| `REQ-L2-E2-SAME-BLUEPRINT-VALIDATION-001` | E2 Valid MUST use the same `blueprint_hash`, `policy_hash`, and replay snapshot as E1 Prep; mismatch is FAIL. | 04.3 | prep_receipt | validation_packet | hashes recorded match prep_receipt | `l2.e2_valid` span | `validation_packet.json` or `sealed_rejection_packet.json` | `validator: l2_e2_validation_validator` (release-gate) | `NC-L2-BLUEPRINT-DRIFT-001`: E2 reads a newer blueprint_hash than E1 | `e2_blueprint_drift` | `byte_identical` | DOC_ONLY |
| `REQ-L2-E3-EXEC-LANES-001` | E3 Exec MUST use bounded attempt lanes inside the sandbox_envelope; lane choice is recorded; out-of-lane execution is FAIL. | 04.4 | validation_packet | `attempt_receipt` | `attempt_receipt.lane_id`, `result_class` recorded | `l2.e3_exec` span | `attempt_receipt.json` | `validator: l2_e3_exec_validator` (release-gate) | `NC-L2-OUT-OF-LANE-001`: tool runs outside declared lane | `l2_out_of_lane_execution` | `byte_identical` | DOC_ONLY |
| `REQ-L2-E4-HEAL-SAME-AUTHORITY-001` | E4 Heal MUST use the same authority context as E2 (no scope expansion, no policy escalation, no new capability_token). Oscillation must be detected. | 04.5 | attempt outcome | `heal_receipt` | heal_receipt records `authority_context_id` matching E2; `oscillation_signal` field present | `l2.e4_heal` span | `heal_receipt.json` | `validator: l2_e4_heal_validator` (release-gate) | `NC-L2-HEAL-ESCALATE-001`: heal acquires new capability mid-run | `heal_authority_escalation` | `byte_identical` | DOC_ONLY |
| `REQ-L2-E5-SEAL-ARTIFACT-001` | E5 Seal MUST emit a `sealed_l2_artifact` with content_hash, lineage to E1..E4 receipts, terminal_class, and (if any) `proposed_state_diff` reference. | 04.6 | E1..E4 receipts | `sealed_l2_artifact` | sealed artifact carries `content_hash`, lineage, terminal_class | `l2.e5_seal` span | `sealed_l2_artifact.json` | `validator: l2_e5_seal_validator` (release-gate) | `NC-L2-SEAL-MISSING-LINEAGE-001`: sealed artifact lacks lineage to prep | `sealed_artifact_lineage_break` | `byte_identical` | DOC_ONLY |
| `REQ-L2-PTC-SANDBOX-001` | PTC scripts MUST run inside a frozen sandbox; raw outputs MUST remain isolated; only sealed stdout summary is allowed downstream; ambient tool use is FORBIDDEN. | 04.7 | PTC script | sandbox receipt | `sandbox_envelope_hash`, `raw_output_isolated=true` | `l2.ptc_sandbox` span | `ptc_sandbox_receipt.json` | `validator: l2_ptc_sandbox_validator` (release-gate) | `NC-L2-AMBIENT-TOOL-001`: PTC script invokes ambient tool | `ambient_tool_use` | `byte_identical` | DOC_ONLY |
| `REQ-L2-PROPOSED-STATE-DIFF-001` | `proposed_state_diff` MUST be inert until Exit X1J; L2 MUST NOT apply it. | 04.9 | E5 seal | `proposed_state_diff` | diff carries `commit_request_candidate=true`, `applied=false` | `l2.state_diff` span | `proposed_state_diff.json` | `validator: l2_state_diff_inert_validator` (release-gate) | `NC-L2-DIFF-APPLY-001`: L2 applies state diff before Exit | `state_diff_applied_pre_exit` | `byte_identical` | DOC_ONLY |
| `REQ-L2-VERIFY-THEN-EXECUTE-001` | L2 local critique MUST not expand scope or change authority; verify-then-execute is bounded by the prep_receipt. | 04.10 | prep_receipt + intermediate output | critique receipt | critique receipt records `scope_expansion=false`, `authority_context_id` matched | `l2.verify_then_execute` span | `critique_receipt.json` | `validator: l2_critique_validator` (release-gate) | `NC-L2-CRITIQUE-EXPAND-001`: critique expands scope | `critique_scope_expansion` | `byte_identical` | DOC_ONLY |
| `REQ-L2-OBSERVABILITY-001` | L2 MUST emit observability and anti-bypass signals on every E1..E5 transition. | 04.8 | every L2 stage | observability stream | every transition logged | `l2.observability` span | `l2_observability.json` | `validator: l2_observability_validator` (release-gate) | `NC-L2-DARK-EXEC-001`: stage transition not logged | `l2_dark_execution` | `byte_identical` | DOC_ONLY |
| `REQ-L2-NO-PROVIDER-FALLBACK-001` | L2 MUST NOT silently switch model provider; fallback requires E2 re-validation against the new provider's policy/blueprint. | 04.4 | model invocation | provider receipt | `provider_id` and `provider_governance_hash` recorded; fallback always re-validated | `l2.model_call` span | `model_call_receipt.json` | `validator: l2_no_silent_fallback_validator` (release-gate) | `NC-L2-PROVIDER-SILENT-FALLBACK-001`: provider switch without re-validation | `silent_provider_fallback` | `byte_identical` | DOC_ONLY |
| `REQ-L2-SEQUENCER-CONTRACT-001` | The L2 sequencer MUST run E1..E5 in order; out-of-order or skipped stages are FAIL. | 04.0 | sequencer | (governance) | trace shows E1→E2→E3→E4 (when triggered)→E5 in order | `l2.sequencer` span events | `l2_sequencer_log.json` | `validator: l2_sequencer_validator` (release-gate) | `NC-L2-SKIP-E2-001`: E3 runs without E2 | `l2_stage_order_violation` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`sealed_l2_artifact` MUST carry: `sealed_l2_artifact_id`, `request_id`, `route_id`, `step_id?`, `prompt_envelope_id`, `trace_root`, `trace_id`, `span_id`, `lineage` (to all E1..E5 receipts), `terminal_class` ∈ {`success`, `repaired_success`, `failed_safe`, `failed_unrecoverable`}, `proposed_state_diff_id?`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `validator_receipt_id`, `downstream_recommendation?` (non-authoritative).

Each E1..E5 receipt carries the same governance fields plus its stage-specific schema.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans: `l2.entry`, `l2.sequencer` (parent), `l2.e1_prep`, `l2.e2_valid`, `l2.e3_exec`, `l2.e4_heal` (when triggered), `l2.e5_seal`, `l2.ptc_sandbox` (when PTC), `l2.state_diff` (when applicable), `l2.verify_then_execute`, `l2.model_call`, `l2.tool_call`, `l2.observability`.

Required attributes: `req_id`, `request_id`, `route_id`, `step_id?`, `prompt_envelope_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `parent_contract_id`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `l2_no_direct_l4_write_validator`, `l2_entry_authority_validator`, `l2_e1_prep_validator`, `l2_e2_validation_validator`, `l2_e3_exec_validator`, `l2_e4_heal_validator`, `l2_e5_seal_validator`, `l2_ptc_sandbox_validator`, `l2_state_diff_inert_validator`, `l2_critique_validator`, `l2_observability_validator`, `l2_no_silent_fallback_validator`, `l2_sequencer_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-L2-*` row in §4 is mandatory. Critical-severity controls: `NC-L2-DIRECT-L4-WRITE-001`, `NC-L2-AMBIENT-TOOL-001`, `NC-L2-DIFF-APPLY-001`, `NC-L2-PROVIDER-SILENT-FALLBACK-001`, `NC-L2-BLUEPRINT-DRIFT-001`, `NC-L2-HEAL-ESCALATE-001`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(PromptEnvelope, capability_token, sandbox_envelope, policy_hash, blueprint_hash, seed)`, `sealed_l2_artifact.content_hash` and per-stage receipt `content_hash` MUST replay byte-identical (allowed nondeterminism: ids, span_id, trace_id, timestamps).

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 04 row's `Release Gate` is `PASS` only when: no direct L4 write; signed entry; E1..E5 in order with same blueprint_hash; PTC sandbox enforced; proposed_state_diff inert; verify-then-execute scoped; no silent provider fallback; observability complete.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L2 bounded execution invariants and the E1..E5 contract.

**Related files own**: per-stage detail in `04.0`..`04.10`; `COVERAGE_MATRIX.md` and `EVIDENCE_AUDIT.md` are historical (subsumed by `00X` registry per `00X §13`).

**Forbidden duplicated ownership**: L2 MUST NOT route, expand workflow, retrieve, assemble prompts, commit, approve, evaluate, or decide final disposition.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL` (as final disposition), `COMMIT_REQUEST_TO_UWG` (as final disposition), `SAFE_FALLBACK` (as final disposition), `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `04.0_L2_Sequencer_Orchestrator_Contract.md` — `REQ-L2-SEQ-*`
- `04.1_L2_Execution_Entry_Authority_and_Packet_Intake.md` — `REQ-L2-ENTRY-*`
- `04.2_L2_E1_Prep_Frozen_Execution_Room.md` — `REQ-L2-E1-*`
- `04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md` — `REQ-L2-E2-*`
- `04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md` — `REQ-L2-E3-*`
- `04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md` — `REQ-L2-E4-*`
- `04.5a_L2_Resolution_Context_Invariant.md` — `REQ-L2-RESOLUTION-*`
- `04.6_L2_E5_Seal_Artifact_and_Dispatch.md` — `REQ-L2-E5-*`
- `04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md` — `REQ-L2-PTC-*`
- `04.8_L2_Observability_Replay_Anti_Bypass_Tests.md` — `REQ-L2-OBS-*`, `REQ-L2-ANTIBYPASS-*`
- `04.9_L2_StateDiffCandidate_and_Mutation_Intent.md` — `REQ-L2-STATE-DIFF-*`
- `04.10_L2_Verify_Then_Execute_Local_Critique.md` — `REQ-L2-CRITIQUE-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 12 child files own per-stage REQ_IDs (deferred for full conversion).
- E1..E5 ordering rule and same-blueprint-hash rule are binding.
- PTC sandbox isolation and proposed_state_diff inertness are binding.

END OF 04 — L2 EXECUTE PARENT
========================================================================================================================
