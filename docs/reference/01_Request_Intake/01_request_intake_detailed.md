========================================================================================================================
01_REQUEST_INTAKE_DETAILED.md
REQUEST INTAKE / U0 — FULL OVERWRITE
MECE WITH 00A L5, 00B L4/UWG, 00C RUNTIME GATES, AND 02-06 RUNTIME REQUIREMENTS
========================================================================================================================

PURPOSE
========================================================================================================================
This parent file defines Request Intake as the structural ingress and identity-stamping layer for the governed runtime.

Request Intake answers one narrow question:

"Is this inbound request structurally valid, attributable, bounded, quota-safe, traceable, and safe to hand to L1 for
semantic interpretation?"

The source invariant is strict:
- U0 validates transport, identity baseline, quotas, schema, and envelope.
- U0 emits validated_request or rejected_request.
- U0 assigns request_id, session_id, and trace_root.
- U0 does not reason, retrieve, route, call tools, call models, execute, or mutate.

This file intentionally removes whole-runtime responsibilities that belong to 00C Runtime Gates, 05 Exit, 00B L4/UWG,
00A L5, L2, C0, Prompt Assembly, and L6.

GLOBAL NO-OVERLAP LOCK
========================================================================================================================
- 00A_L5_Governance_Safety owns policy, authority, origin-trust, egress, HITL re-clearance, replay/audit certification evidence.
- 00B_L4_State_Archive_and_UWG owns durable state, read surfaces, and the only durable write admission path.
- 00C_Runtime_Gates_Current_Run_Mesh owns G01-G29 live current-run GateVerdict requirements and gate disposition vocabulary.
- U0 / 01 Request Intake owns request envelope validation, baseline identity/session/tenant stamping, structural schema normalization, quota/size limits, origin labels, and the ValidatedRequest or RejectedRequest handoff.
- 02_L1_Reasoning_Plan owns intent interpretation, task_spec, query_spec, ambiguity register, support expectation, and plan recommendation.
- 03_L0_Route_Decision_and_L3_Orchestration owns route selection, RouteContract authority, and managed workflow shaping.
- C0_Context_Engine owns evidence retrieval, shaping, verification, support score, and FinalEvidenceContract.
- PA_Prompt_Assembly owns signed provider-ready PromptEnvelope / CompiledPromptArtifact construction.
- 04_L2_Execute owns bounded execution, local repair, sealed artifacts, and proposed_state_diff only.
- 05_Exit_Eval_and_Control owns sealed-result checkout, X1/X2/X3 current-run disposition, HITL review flow, and CommitRequest handoff.
- 06_L6_Shadow_Evaluation_System_Learning owns completed-run evaluation, RCA, proposal drafting, gauntlet, and future-run learning promotion attempts.

U0 / 01 DOES NOT OWN:
- semantic planning
- route authority
- retrieval
- prompt assembly
- tool/model execution
- workflow expansion
- final output approval
- runtime GateVerdict schema
- L5 certification evidence
- UWG durable write admission
- L6 learning


U0 HARD BOUNDARY
========================================================================================================================
U0 / Request Intake validates whether a request is structurally admissible into the governed runtime.

U0 MAY:
- accept a transport envelope
- authenticate or classify caller baseline where available
- bind request_id, session_id, tenant_id, trace_root, and ingress_timestamp
- enforce channel, size, quota, duplicate, and envelope schema controls
- normalize raw payload into a structurally valid request object
- label origin_trust and data_boundary metadata
- emit ValidatedRequest or RejectedRequest
- emit local intake receipts and intake spans
- hand off to L1 only after the request is structurally valid

U0 MUST NOT:
- reason about the user's goal
- infer a route
- retrieve evidence
- assemble prompts
- call tools, models, browsers, connectors, scripts, or humans
- mutate durable state
- emit RouteContract
- emit FinalEvidenceContract
- emit PromptEnvelope
- emit SealedL2Artifact
- emit ExitDisposition
- emit LearningProposal
- directly write L4


WHY THIS OVERWRITE EXISTS
========================================================================================================================
Earlier 01 intake material carried whole-runtime implementation language:
- G01-G29 runtime gates
- full deterministic replay across every layer
- full OTEL proof across every layer
- evidence packet for the whole system
- anti-bypass checks for all layers

Those are valid requirements, but they are not U0 ownership.
They now belong to:
- 00C_Runtime_Gates_Current_Run_Mesh for G01-G29 and gate verdicts.
- 00B_L4_State_Archive_and_UWG for durable state and write sovereignty.
- 05_Exit_Eval_and_Control for X1/X2/X3 disposition.
- 06_L6_Shadow_Evaluation_System_Learning for completed-run evaluation and future learning.
- An optional E2E Proof Pack if a single sample run must prove all layers.

01 now owns only the intake surface.

CANONICAL CHILD FILE MAP
========================================================================================================================
01.1_Intake_Transport_Envelope_and_Channel_Validation_detailed.md
- Unique surface: accepted ingress channel, raw envelope, payload size, transport metadata, channel trust baseline.
- Owns: TransportEnvelope, RawIngressEnvelope, ChannelValidationReceipt.
- Does not own: semantic safety, task ambiguity, route selection, output policy.

01.2_Intake_Identity_Tenant_Session_and_Quota_Baseline_detailed.md
- Unique surface: caller baseline, tenant/session binding, quota envelope, duplicate admission baseline.
- Owns: CallerScopeBaseline, TenantSessionBinding, QuotaBaselineReceipt.
- Does not own: deep authorization policy, L5 certification, C0 ACL retrieval filtering, UWG write authority.

01.3_Intake_Schema_Normalization_and_Idempotency_detailed.md
- Unique surface: structural schema validation, canonical payload normalization, idempotency and request hash.
- Owns: NormalizedRequestPayload, IdempotencyReceipt, RequestDigestManifest.
- Does not own: L1 semantic parsing, L0 route digest, L2 attempt idempotency, replay of downstream artifacts.

01.4_Intake_Origin_Trust_Injection_Triage_and_Data_Labeling_detailed.md
- Unique surface: origin labels, quoted-content labeling, instruction/data boundary pre-labels, obvious injection triage.
- Owns: OriginTrustLabelSet, IngressDataBoundaryMap, InjectionTriageReceipt.
- Does not own: Prompt Assembly slot validation, C0 retrieved-content quarantine, L5 origin certification, final adversarial gate.

01.5_Intake_Rejection_ValidatedRequest_and_Handoff_to_L1_detailed.md
- Unique surface: ValidatedRequest, RejectedRequest, L1 handoff, fail-closed admission result.
- Owns: ValidatedRequestContract, RejectedRequestContract, L1HandoffReceipt.
- Does not own: L1PlanContract, RouteContract, ExitDisposition, user-facing final response policy.

01.6_Intake_Observability_Replay_and_Anti_Bypass_Tests_detailed.md
- Unique surface: intake-only spans, intake-only replay bindings, intake boundary anti-bypass tests.
- Owns: IntakeTraceReceipt, IntakeReplayBinding, U0BoundaryTestSuite.
- Does not own: whole-runtime OTEL, G01-G29 gate mesh, Exit trace completeness, L6 telemetry exhaust.

TOP-LEVEL FLOW
========================================================================================================================
[ inbound request ]
        |
        v
+-----------------------------+
| 01.1 TRANSPORT / ENVELOPE   |
| channel, size, envelope     |
+-------------+---------------+
              |
              v
+-----------------------------+
| 01.2 IDENTITY / QUOTA       |
| caller, tenant, session     |
+-------------+---------------+
              |
              v
+-----------------------------+
| 01.3 SCHEMA / NORMALIZE     |
| canonical request payload   |
+-------------+---------------+
              |
              v
+-----------------------------+
| 01.4 ORIGIN / DATA LABELS   |
| origin trust, intent-as-data|
+-------------+---------------+
              |
              v
+-----------------------------+
| 01.5 ADMISSION / HANDOFF    |
| ValidatedRequest or reject  |
+-------------+---------------+
              |
              v
[ 02 L1 Reasoning + Plan ]

If any required structural admission check fails:
[ RejectedRequest ] -> caller-safe rejection path
No L1, L0, C0, PA, L3, L2, Exit, UWG, or L6 runtime work may run from an invalid envelope.

PARENT CONTRACT SUMMARY
========================================================================================================================
RequestEnvelope
- request_id optional before U0, required after U0
- raw_channel
- raw_payload_ref
- received_at
- caller_presenting_identity optional
- client_metadata
- transport_metadata
- content_length
- attachment_refs
- connector_refs
- declared_operation if explicit
- channel_security_context

ValidatedRequest
- request_id
- session_id
- trace_root
- tenant_id or tenant_unknown marker
- caller_scope_baseline
- normalized_payload
- origin_trust_labels
- data_boundary_map
- quota_receipt
- schema_receipt
- idempotency_key
- normalized_request_hash
- intake_policy_snapshot_ref
- handoff_allowed = true
- target_next_surface = 02_L1_REASONING_PLAN

RejectedRequest
- request_id if available
- trace_root if available
- rejection_id
- rejection_stage
- rejection_reason_code
- structural_detail
- safe_user_message
- retryable
- missing_fields
- quota_status
- schema_status
- security_status
- handoff_allowed = false

U0 FORBIDDEN OUTPUTS
========================================================================================================================
U0 must not emit:
- L1PlanContract
- RouteContract
- RetrievalPlan
- FinalEvidenceContract
- PromptEnvelope
- L3WorkflowContract
- L2ExecutionRequest
- SealedL2Artifact
- ExitReviewPacket
- ExitDisposition
- CommitRequest
- UWGCommitReceipt
- RuntimeExhaustBundle
- ShadowEvalRecord
- LearningProposal

U0 may emit only:
- local intake receipts
- ValidatedRequest
- RejectedRequest
- L1HandoffReceipt
- intake spans
- intake replay binding

IMPLEMENTATION TARGETS
========================================================================================================================
Preferred logical module layout, adjust to existing repo conventions:

src/
  request_intake/
    contracts.py
    transport.py
    identity.py
    quota.py
    schema.py
    normalization.py
    origin_labels.py
    handoff.py
    otel.py
    replay.py

tests/
  request_intake/
    test_u0_transport_envelope.py
    test_u0_identity_quota.py
    test_u0_schema_normalization.py
    test_u0_origin_labels.py
    test_u0_handoff.py
    test_u0_replay_and_otel.py
    test_u0_negative_boundaries.py

DISCOVERY REQUIREMENT FOR WINDSURF
========================================================================================================================
Before editing code:
1. Inspect existing request/intake/router/app entrypoint code.
2. Identify current request envelope, session, auth, quota, and schema utilities.
3. Identify whether existing runtime gates already implement G01-G05 in 00C.
4. Identify OTEL helpers and replay/hash helpers.
5. Identify current tests that accidentally let L1/L0/L2 run from malformed input.
6. Produce a short implementation plan.
7. Implement the smallest coherent changes needed to make U0 enforceable and testable.

No broad refactors.
No unrelated renames.
No duplicate gate mesh.
No whole-runtime proof logic inside 01.

ACCEPTANCE CRITERIA
========================================================================================================================
This parent and its children are complete only when:
- malformed transport never reaches L1
- unbound identity/tenant/session state is explicitly marked or rejected
- quota and size failures fail closed
- schema normalization is deterministic
- idempotency key and normalized_request_hash are stable
- user content is labeled as intent/data, not authority
- injection-like content is labeled for downstream treatment, not executed or obeyed by U0
- ValidatedRequest contains the fields L1 expects
- RejectedRequest is safe, structured, and non-leaky
- U0 spans and replay bindings cover intake only
- tests fail if U0 reasons, routes, retrieves, calls tools/models, executes, mutates, or writes L4

END OF 01_REQUEST_INTAKE_DETAILED.md
