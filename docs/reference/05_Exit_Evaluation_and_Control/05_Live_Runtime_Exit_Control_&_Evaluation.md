========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 05_Live_Runtime_Exit_Control_&_Evaluation.md
Layer / subsystem: 05 — Exit Evaluation and Control (parent)
Parent file: docs/reference/README.md
Ownership surface: ExitReviewPacket normalization; X1A..X1J current-run checkout checks; X2 aggregation; X3A..X3E disposition (exactly one X3); HITL freeze/review/reclearance flow; CommitRequest emission to UWG; runtime exhaust packaging; Exit-specific observability and anti-bypass.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: Exit aggregates and disposes — exactly one disposition per run. It does not execute (L2), retrieve (C0), mutate L4 directly (UWG owns admission), let L6 rescue (L6 fires after boundary), or own G01–G29 gate definitions (00C).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `05_Live_Runtime_Exit_Control_&_Evaluation.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the ExitReviewPacket schema invariant
- the rule that Exit emits **exactly one** X3 disposition per run
- the rule that Exit emits CommitRequest to UWG (UWG owns admission)
- the HITL freeze/review/reclearance flow invariants

It does **not** own:
- per-check detail (X1A..X1J in `05.2`..`05.4`)
- aggregation/disposition mechanics detail (`05.5`)
- HITL flow detail (`05.6`)
- runtime exhaust packaging detail (`05.7`)
- Exit observability detail (`05.8`)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: `sealed_l2_artifact` OR completed `L3WorkflowContract` package OR L0 RET (route-terminal) packet.
**Downstream outputs**: exactly one X3 disposition per run; `CommitRequest` to UWG when durable mutation requested; `RuntimeExhaustBundle` to L6 after boundary; HITL packet when freeze required.
**Forbidden behaviors**: executing tools, retrieving evidence, mutating L4 directly, allowing L6 to rescue current run, owning G01–G29 definitions.
**Allowed outputs only**: `ExitReviewPacket`, X1 verdicts, X3 disposition, `CommitRequest`, HITL freeze packet, `RuntimeExhaustBundle`, sealed return response.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-EXIT-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-EXIT-INPUT-NORMALIZATION-001` | Exit MUST normalize the input artifact (sealed_l2_artifact, L3 package, or RET packet) into a single canonical `ExitReviewPacket` before running checks. | 05.1 | upstream artifact | `ExitReviewPacket` | every Exit run reads exactly one ExitReviewPacket | `exit.normalize` parent span | `exit_review_packet_<run_id>.json` | `validator: exit_input_normalization_validator` (release-gate) | `NC-EXIT-MISSING-RECEIPT-FIELD-001`: input missing required receipt field | `exit_review_packet_field_missing` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-EXIT-X1A-X1F-CHECKS-001` | Exit MUST run X1A..X1F current-run checkout checks; each emits a per-check verdict bundled into `ExitReviewPacket.x1_verdicts[]`. | 05.2 | ExitReviewPacket | x1_verdicts | each x1_<id> verdict carries result, reason_codes | `exit.x1.<id>` spans | `x1_verdict_bundle.json` | `validator: exit_x1a_x1f_validator` (release-gate) | `NC-EXIT-X1-SKIP-001`: skip a required X1 check | `x1_check_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-X1G-X1I-REPLAY-OBS-001` | Exit MUST run X1G..X1I (replay determinism, observability/trace consistency); each emits its verdict. | 05.3 | ExitReviewPacket | x1_verdicts | `replay_verdict.match_type`, `trace_completeness_verdict.missing_spans[]` | `exit.x1.G`, `exit.x1.H`, `exit.x1.I` spans | `x1_verdict_bundle.json` | `validator: exit_replay_obs_validator` (release-gate) | `NC-EXIT-REPLAY-MISMATCH-PASS-001`: replay drift passes through | `replay_drift_passed_at_exit` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-X1J-WRITE-ELIGIBILITY-001` | Exit MUST run X1J write-eligibility before allowing CommitRequest emission to UWG; ineligible diffs trigger BLOCK_COMMIT. | 05.4 | ExitReviewPacket | x1J verdict + CommitRequest or BLOCK_COMMIT | `x1J_verdict.eligibility_codes[]` | `exit.x1.J` span | `x1J_verdict.json` | `validator: exit_x1j_validator` (release-gate) | `NC-EXIT-INELIGIBLE-COMMIT-001`: ineligible diff committed | `ineligible_commit_emitted` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-EXACTLY-ONE-DISPOSITION-001` | Exit MUST emit **exactly one** X3 disposition per run; multiple X3 dispositions are FAIL. | 05.5 | x1 verdicts | X3 disposition | one `x3_disposition.json` per `run_id` | `exit.x3_disposition` span | `x3_disposition.json` | `validator: exit_one_disposition_validator` (release-gate) | `NC-EXIT-DUAL-DISPOSITION-001`: emit X3A and X3B for same run | `dual_x3_disposition` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-EXIT-DISPOSITION-VOCAB-001` | The X3 disposition MUST be one of {`X3A_ALLOW_FINISH`, `X3B_DENY`, `X3C_COMMIT_REQUEST_TO_UWG`, `X3D_ESCALATE_HITL`, `X3E_SAFE_FALLBACK`}. | 05.5 | x1 verdicts | X3 disposition | `x3_disposition.kind` ∈ allowed set | `exit.x3_disposition` event | `x3_disposition.json` | `validator: exit_x3_vocabulary_validator` (release-gate) | `NC-EXIT-CUSTOM-DISPOSITION-001`: emit unknown disposition | `unknown_x3_disposition` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-AGGREGATION-MATRIX-001` | The X2 aggregation MUST be deterministic for a fixed set of x1 verdicts; severity escalation rules are enumerated. | 05.5 | x1 verdicts | X2 aggregate | `x2_aggregate.json` carries `severity`, `aggregate_class` | `exit.x2_aggregate` span | `x2_aggregate.json` | `validator: exit_aggregation_validator` (release-gate) | `NC-EXIT-AGG-DRIFT-001`: same x1 verdicts produce different X2 | `x2_aggregation_drift` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-COMMIT-REQUEST-001` | When disposition = `X3C_COMMIT_REQUEST_TO_UWG`, Exit MUST emit a `CommitRequest` carrying `clearance_proof_id`, `staged_diff`, `policy_hash`, `blueprint_hash`, `replay_key`. | 05.4, 05.5 | proposed_state_diff + clearance | `CommitRequest` | all 5 fields present | `exit.commit_request` span | `commit_request_<run_id>.json` | `validator: exit_commit_request_validator` (release-gate) | `NC-EXIT-COMMIT-NO-CLEARANCE-001`: emit CommitRequest without clearance proof | `commit_request_unclear` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-NO-DIRECT-L4-WRITE-001` | Exit MUST NOT mutate L4 directly; UWG is the sole admission path. | 05 | (governance) | (none) | trace shows no `l4.write` originating from Exit | NOT_APPLICABLE: anti-pattern detection | `compiler_anti_cheat_findings.json` | `validator: exit_no_direct_l4_write_validator` (release-gate) | `NC-EXIT-DIRECT-L4-WRITE-001`: Exit mutates L4 directly | `direct_l4_write_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-HITL-FREEZE-001` | When disposition = `X3D_ESCALATE_HITL`, Exit MUST freeze the run (no writes, no further execution), emit a HITL packet, and resume only after L5 reclearance. | 05.6 | escalation trigger | HITL packet | freeze receipt issued; `human_text_treated_as_data=true` | `exit.hitl_freeze` span | `hitl_freeze_packet.json` | `validator: exit_hitl_freeze_validator` (release-gate) | `NC-EXIT-FREEZE-WRITE-001`: write occurs during freeze | `write_during_hitl_freeze` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-HITL-RECLEAR-ROUNDTRIP-001` | After HITL response, Exit MUST round-trip through L5 reclearance before resuming; resume produces a single new X3 disposition for the same run_id. | 05.6 | HITL reply + L5 reclear | resumed X3 | resume preserves `run_id`; new X3 has `is_post_hitl=true` | `exit.hitl_resume` span | `x3_disposition.json` (post-HITL) | `validator: exit_hitl_reclear_validator` (release-gate) | `NC-EXIT-HITL-NO-RECLEAR-001`: resume without L5 reclear | `hitl_resume_without_reclear` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-RUNTIME-EXHAUST-001` | After every run, Exit MUST package a `RuntimeExhaustBundle` for L6 after boundary; the bundle is sealed and immutable. | 05.7 | completed run | `RuntimeExhaustBundle` | bundle has `sealed=true`, `content_hash` | `exit.runtime_exhaust` span | `runtime_exhaust_bundle.json` | `validator: exit_runtime_exhaust_validator` (release-gate) | `NC-EXIT-EXHAUST-MUTATE-001`: bundle mutated post-seal | `exhaust_bundle_mutated` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-RETURN-RESPONSE-001` | Exit MUST emit the sealed return response only after X3 disposition is finalized; pre-disposition responses are FAIL. | 05.7 | finalized X3 | return response | response carries `x3_disposition_id` | `exit.return_response` span | `return_response.json` | `validator: exit_return_response_validator` (release-gate) | `NC-EXIT-EARLY-RESPONSE-001`: response emitted before X3 | `response_before_disposition` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-OBSERVABILITY-001` | Exit MUST emit observability and anti-bypass signals on every X1A..X1J × X3A..X3E coverage cell. | 05.8 | every Exit transition | observability stream | every transition logged | `exit.observability` span | `exit_observability.json` | `validator: exit_observability_validator` (release-gate) | `NC-EXIT-DARK-DISPOSITION-001`: disposition not logged | `exit_dark_disposition` | `byte_identical` | DOC_ONLY |
| `REQ-EXIT-NO-L6-RESCUE-001` | Exit MUST NOT allow L6 to rescue the current run; L6 only fires after boundary on sealed exhaust. | 05 | (governance) | (none) | no `l6.*` spans inside `exit.*` parent | NOT_APPLICABLE: span ordering | `compiler_anti_cheat_findings.json` | `validator: exit_no_l6_rescue_validator` (release-gate) | `NC-EXIT-L6-RESCUE-001`: L6 mutates state mid-run | `l6_live_mutation_attempt` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`ExitReviewPacket` MUST carry: `exit_review_packet_id`, `request_id`, `run_id`, `trace_root`, `trace_id`, `span_id`, `input_kind` ∈ {`sealed_l2_artifact`, `l3_workflow_package`, `l0_ret_packet`}, `input_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `lineage`.

`X3 disposition` MUST carry: `x3_disposition_id`, `run_id`, `kind` ∈ {`X3A_ALLOW_FINISH`, `X3B_DENY`, `X3C_COMMIT_REQUEST_TO_UWG`, `X3D_ESCALATE_HITL`, `X3E_SAFE_FALLBACK`}, `severity`, `reason_codes[]`, `evidence_refs[]`, `replay_refs[]`, `is_post_hitl=bool`, `commit_request_id?`, `hitl_packet_id?`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans (children of `exit.run`): `exit.normalize`, `exit.x1.A`..`exit.x1.J` (10 spans), `exit.x2_aggregate`, `exit.x3_disposition`, `exit.commit_request` (when X3C), `exit.hitl_freeze` / `exit.hitl_resume` (when X3D), `exit.runtime_exhaust`, `exit.return_response`, `exit.observability`.

Required attributes: `req_id`, `request_id`, `run_id`, `exit_review_packet_id`, `x3_disposition_id`, `policy_hash`, `blueprint_hash`, `replay_key`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `exit_input_normalization_validator`, `exit_x1a_x1f_validator`, `exit_replay_obs_validator`, `exit_x1j_validator`, `exit_one_disposition_validator`, `exit_x3_vocabulary_validator`, `exit_aggregation_validator`, `exit_commit_request_validator`, `exit_no_direct_l4_write_validator`, `exit_hitl_freeze_validator`, `exit_hitl_reclear_validator`, `exit_runtime_exhaust_validator`, `exit_return_response_validator`, `exit_observability_validator`, `exit_no_l6_rescue_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-EXIT-*` row in §4 is mandatory. Critical-severity controls: `NC-EXIT-DUAL-DISPOSITION-001`, `NC-EXIT-DIRECT-L4-WRITE-001`, `NC-EXIT-FREEZE-WRITE-001`, `NC-EXIT-HITL-NO-RECLEAR-001`, `NC-EXIT-L6-RESCUE-001`, `NC-EXIT-INELIGIBLE-COMMIT-001`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(input artifact, policy_hash, blueprint_hash, replay_key)`, X1 verdict bundle, X2 aggregate, and X3 disposition `content_hash` MUST replay byte-identical. Allowed nondeterminism: ids, span_id, trace_id, timestamps.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 05 row's `Release Gate` is `PASS` only when: input normalized; all X1 checks emitted; X2 deterministic; exactly one X3; vocabulary respected; CommitRequest only with clearance; no direct L4 write; HITL freeze enforced; reclearance round-trip preserved; runtime exhaust sealed; return response post-disposition only; observability complete; no L6 rescue.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: Exit aggregation and X3 disposition invariants.

**Related files own**: per-stage detail in `05.1`..`05.8`; supporting `gap_analysis_v3_vs_industry_2026.md`, `grader_composition_spec.md`, `runtime_to_regression_dataset_flow.md`, `v4_hardening_addendum.md` are advisory and do not own runtime authority.

**Forbidden duplicated ownership**: Exit MUST NOT execute (L2), retrieve (C0), assemble prompts (PA), mutate L4 directly (UWG), or own G01–G29 (00C).

**Forbidden output vocabulary**: `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`. The tokens `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified` are allowed only inside an `X3 disposition.kind` field.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `05.1_Exit_Input_Normalization_and_Review_Packet.md` — `REQ-EXIT-NORMALIZE-*`
- `05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md` — `REQ-EXIT-X1A-*`..`REQ-EXIT-X1F-*`
- `05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md` — `REQ-EXIT-X1G-*`..`REQ-EXIT-X1I-*`
- `05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md` — `REQ-EXIT-X1J-*`, `REQ-EXIT-X3C-*`
- `05.5_Exit_Aggregation_and_X3_Disposition.md` — `REQ-EXIT-X2-*`, `REQ-EXIT-X3-*`
- `05.6_Exit_HITL_Freeze_Review_and_Reclearance.md` — `REQ-EXIT-HITL-*`
- `05.7_Exit_Return_Response_and_Runtime_Exhaust.md` — `REQ-EXIT-RETURN-*`, `REQ-EXIT-EXHAUST-*`
- `05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md` — `REQ-EXIT-OBS-*`, `REQ-EXIT-ANTIBYPASS-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 8 child files own per-stage REQ_IDs (deferred for full conversion).
- "Exactly one X3 disposition" rule is binding.
- "No L6 rescue" rule is binding.

END OF 05 — EXIT EVALUATION AND CONTROL PARENT
========================================================================================================================
