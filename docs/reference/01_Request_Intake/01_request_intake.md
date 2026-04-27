========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 01_request_intake.md
Layer / subsystem: 01 — Request Intake / U0 (parent)
Parent file: docs/reference/README.md
Ownership surface: Request envelope validation; identity/tenant/session/quota baseline; schema normalization and idempotency; origin-trust injection triage and data labeling; rejection vs ValidatedRequest emission; intake observability and anti-bypass.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: Intake validates and stamps. It does not reason (L1), retrieve (C0), route (L0), execute (L2), mutate (L4 / UWG), approve (L5), evaluate (L6), or decide final disposition (Exit).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `01_request_intake.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the envelope-validation contract (`ValidatedRequest` vs `RejectedRequest`)
- the request_id/session_id/trace_root stamping invariant
- the identity/tenant/quota baseline contract
- the schema normalization & idempotency rules
- the origin-trust labeling at intake
- the intake observability/anti-bypass invariants

It does **not** own:
- planning, routing, retrieval, execution, durable writes, gates, certification, or learning

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: raw transport request (HTTP/grpc/queue).

**Downstream outputs**: `ValidatedRequest` (handed to L1) OR `RejectedRequest` (terminal).

**Forbidden behaviors**: any reasoning, retrieval, routing, execution, mutation, approval; the only allowed verbs are `validate`, `stamp`, `normalize`, `label`, `emit`, `reject`.

**Allowed outputs only**: `ValidatedRequest`, `RejectedRequest`, intake observability stream.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-U0-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-U0-INGRESS-ENVELOPE-001` | Intake MUST validate the request envelope (transport, schema, headers, payload type) before any downstream processing. | 01.1 | raw request | `ValidatedRequest` or `RejectedRequest` | `ValidatedRequest.envelope_validated=true` with envelope schema hash | `u0.envelope_validate` parent span | `validated_request_<request_id>.json` or `rejected_request_<request_id>.json` | `validator: u0_envelope_validator` (release-gate) | `NC-U0-MALFORMED-ENVELOPE-001`: send malformed payload | `envelope_schema_violation` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-U0-IDENTITY-STAMP-001` | Intake MUST stamp `request_id`, `session_id`, `trace_root`, `caller_scope_baseline` on the validated request. | 01.2 | validated envelope | `ValidatedRequest` | all 4 fields present and uuid-valid | `u0.identity_stamp` span | `validated_request.json` carries fields | `validator: u0_identity_stamp_validator` (release-gate) | `NC-U0-MISSING-STAMP-001`: missing `trace_root` | `intake_stamp_missing` | `byte_identical` | DOC_ONLY |
| `REQ-U0-QUOTA-BASELINE-001` | Intake MUST enforce per-tenant/per-caller quota at baseline; over-quota requests emit `RejectedRequest` with `reason_code=quota_exceeded`. | 01.2 | validated envelope + tenant ledger | `ValidatedRequest` or `RejectedRequest` | quota check receipt linked to `caller_scope_baseline` | `u0.quota_check` span | `quota_check_receipt.json` | `validator: u0_quota_validator` (release-gate) | `NC-U0-QUOTA-BYPASS-001`: over-quota request admitted | `quota_bypass` | `byte_identical` | DOC_ONLY |
| `REQ-U0-SCHEMA-NORMALIZE-001` | Intake MUST normalize the request payload to the canonical schema before emitting `ValidatedRequest`; normalization is deterministic. | 01.3 | validated envelope | normalized payload | `validated_request.payload_schema_hash` matches canonical schema | `u0.schema_normalize` span | `validated_request.json` | `validator: u0_schema_normalize_validator` (release-gate) | `NC-U0-SCHEMA-DRIFT-001`: payload not normalized | `schema_normalize_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-U0-IDEMPOTENCY-001` | Intake MUST detect duplicate requests by canonical `idempotency_key` and emit a `RejectedRequest` (or replay receipt) for duplicates. | 01.3 | normalized payload | `RejectedRequest` or replay | duplicate detection receipt | `u0.idempotency_check` span | `idempotency_receipt.json` | `validator: u0_idempotency_validator` (release-gate) | `NC-U0-DUP-ADMIT-001`: duplicate request runs twice | `duplicate_request_admitted` | `byte_identical` | DOC_ONLY |
| `REQ-U0-ORIGIN-TRIAGE-001` | Intake MUST inject an origin-trust label and triage data labeling before handoff. | 01.4 | validated payload | labeled payload | `validated_request.origin_trust_class` and `data_labels[]` populated | `u0.origin_triage` span | `validated_request.json` | `validator: u0_origin_triage_validator` (release-gate) | `NC-U0-MISLABEL-001`: untrusted origin labeled trusted | `origin_trust_mislabel_at_intake` | `byte_identical` | DOC_ONLY |
| `REQ-U0-REJECTION-TERMINAL-001` | A `RejectedRequest` MUST be terminal: it MUST NOT be forwarded to L1; it MUST emit a sealed rejection receipt. | 01.5 | rejection decision | `RejectedRequest` | rejection sealed; no L1 invocation in trace | `u0.reject` span | `rejected_request.json` | `validator: u0_rejection_terminal_validator` (release-gate) | `NC-U0-REJECT-FORWARD-001`: rejected request reaches L1 | `rejected_request_forwarded` | `byte_identical` | DOC_ONLY |
| `REQ-U0-VALIDATED-HANDOFF-001` | A `ValidatedRequest` MUST be the sole entry into L1; L1 MUST refuse any input that is not a `ValidatedRequest`. | 01.5 | `ValidatedRequest` | (handoff to L1) | L1 plan span has `parent_contract_id` = validated_request id | `u0.handoff_to_l1` span | `validated_request.json` | `validator: u0_handoff_validator` (release-gate) | `NC-U0-RAW-TO-L1-001`: raw request reaches L1 | `l1_received_unvalidated_input` | `byte_identical` | DOC_ONLY |
| `REQ-U0-OBSERVABILITY-001` | Intake MUST emit observability and anti-bypass signals on every request (admitted or rejected). | 01.6 | every request | observability stream | every request logged with `request_id` and outcome | `u0.observability` span | `intake_observability.json` | `validator: u0_observability_validator` (release-gate) | `NC-U0-DARK-INTAKE-001`: request silently dropped without observability entry | `intake_dark_drop` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`ValidatedRequest` MUST carry: `request_id`, `session_id`, `trace_root`, `caller_scope_baseline`, `payload_schema_hash`, `idempotency_key`, `origin_trust_class`, `data_labels[]`, `envelope_validated=true`, `received_at_utc`, `policy_hash`, `blueprint_hash`, `replay_key`.

`RejectedRequest` MUST carry: `request_id`, `trace_root`, `reason_code`, `evidence_refs[]`, `received_at_utc`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Span tree: `u0.intake [trace_root]` → {`u0.envelope_validate`, `u0.identity_stamp`, `u0.quota_check`, `u0.schema_normalize`, `u0.idempotency_check`, `u0.origin_triage`, `u0.handoff_to_l1` | `u0.reject`, `u0.observability`}.

Required attributes: `req_id`, `request_id`, `trace_root`, `caller_scope_baseline`, `policy_hash`, `blueprint_hash`, `replay_key`. Status code: `OK` for admitted, `ERROR` for rejected with `attributes.fail_reason_code`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `u0_envelope_validator` (release-gate)
- `u0_identity_stamp_validator` (release-gate)
- `u0_quota_validator` (release-gate)
- `u0_schema_normalize_validator` (release-gate)
- `u0_idempotency_validator` (release-gate)
- `u0_origin_triage_validator` (release-gate)
- `u0_rejection_terminal_validator` (release-gate)
- `u0_handoff_validator` (release-gate)
- `u0_observability_validator` (release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-U0-*` row in §4 is mandatory; each MUST trip the matching validator with `reason_code` equal to the row's `Expected Fail Reason`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed input, `ValidatedRequest` content MUST replay byte-identical (modulo `request_id`, `received_at_utc`). The `payload_schema_hash`, `idempotency_key`, `origin_trust_class`, and `data_labels[]` MUST be deterministic.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 01 row's `Release Gate` is `PASS` only when intake validates, stamps, normalizes, labels, and routes correctly with all negative controls tripping with matching reason codes.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: U0 envelope validation, identity stamping, schema normalization, idempotency, origin labeling, rejection emission, intake observability.

**Related files own**: per-stage detail in `01.1`..`01.6`.

**Forbidden duplicated ownership**: Intake MUST NOT plan (L1), route (L0), retrieve (C0), execute (L2), mutate (UWG), approve (L5), or evaluate (L6).

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `01.1_Intake_Transport_Envelope_Channel_Validation.md` — `REQ-U0-ENVELOPE-*`
- `01.2_Intake_Identity_Tenant_Session_Quota_Baseline.md` — `REQ-U0-IDENTITY-*`, `REQ-U0-QUOTA-*`
- `01.3_Intake_Schema_Normalization_and_Idempotency.md` — `REQ-U0-SCHEMA-*`, `REQ-U0-IDEMPOTENCY-*`
- `01.4_Intake_Origin_Trust_Injection_Triage_Data_Labeling.md` — `REQ-U0-ORIGIN-*`
- `01.5_Intake_Rejection_ValidatedRequest_and_Handoff_to_L1.md` — `REQ-U0-REJECT-*`, `REQ-U0-HANDOFF-*`
- `01.6_Intake_Observability_Replay_Anti_Bypass_Tests.md` — `REQ-U0-OBS-*`, `REQ-U0-REPLAY-*`, `REQ-U0-ANTIBYPASS-*`

NOTE: Duplicate filenames `01.1_Intake_Transport_Envelope_and_Channel_Validation.md`, `01.2_Intake_Identity_Tenant_Session_and_Quota_Baseline.md`, `01.4_Intake_Origin_Trust_Injection_Triage_and_Data_Labeling.md`, `01.6_Intake_Observability_Replay_and_Anti_Bypass_Tests.md` are deduped: the canonical files are the ones listed above (no `_and_` infix). The duplicates are flagged for archive in `00X §13 superseded ledger`.

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- The 6 child files own their per-stage REQ_IDs (deferred for full conversion).
- The duplicate filename pairs are de-duplicated.
- Forbidden output vocabulary in §11 reproduces the global ban list.

END OF 01 — REQUEST INTAKE / U0 PARENT
========================================================================================================================
