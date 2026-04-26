========================================================================================================================
01_REQUEST_INTAKE_DETAILED.md
PARENT U0 / REQUEST INTAKE DOCTRINE
NO-OVERLAP FULL OVERWRITE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent file defines U0 / Request Intake at doctrine level only.

Request Intake is the governed front door. It receives raw inbound requests from approved transports, validates the envelope,
binds caller/session/tenant baseline, enforces entry quotas and duplicate controls, validates structural schema, assigns
correlation identifiers, and emits exactly one normalized handoff object:

- ValidatedRequest, when the request is structurally safe enough for L1 to interpret.
- RejectedRequest, when the request cannot enter runtime.

Request Intake does not reason, retrieve, route, call models, call tools, execute, mutate, approve output, approve egress, or
write durable state.

PARENT ROLE
------------------------------------------------------------------------------------------------------------------------
- Define Intake authority doctrine.
- Define Intake-owned receipt language.
- Define no-overlap law.
- Define source ownership boundaries.
- Define child file map.
- Define canonical Intake outputs.
- Define traceability expectations.
- Define the handoff contract into L1.

PARENT DOES NOT OWN IMPLEMENTATION DETAIL
------------------------------------------------------------------------------------------------------------------------
The child files own implementation-grade detail. This parent should not restate their full contracts.

Child details are intentionally moved into:
- 01.1 through 01.6 below.

========================================================================================================================
SOURCE OWNERSHIP BOUNDARY
========================================================================================================================

U0 / INTAKE OWNS AT DOCTRINE LEVEL:
- raw ingress acceptance
- transport and envelope validation
- caller identity evidence capture
- tenant/session/region baseline binding
- entry quota, size, and duplicate controls
- structural request schema validation
- raw payload preservation and normalized payload emission
- origin labels attached to inbound content as intake evidence
- request_id, session_id, trace_root, and ingress replay seed assignment
- ValidatedRequest / RejectedRequest emission
- IntakeAuditReceipt and handoff evidence to L1

U0 / INTAKE DOES NOT OWN:
- semantic intent interpretation
- ambiguity resolution beyond structural "cannot parse" or missing required fields
- route choice
- retrieval or evidence scoring
- prompt slot assembly
- tool/model execution
- current-run final disposition
- policy certification as sovereign L5 evidence
- durable writes
- completed-run learning

SOURCE OWNERS:
- 02_L1_Reasoning_Plan_Generation_detailed.md = semantic interpretation, plan, ambiguity register, support requirements.
- 03_L0_Route_Decision_Switching_L3_detailed.md = route authority and RouteContract.
- C0_Context_Engine_detailed.md = retrieval, evidence scoring, FinalEvidenceContract.
- Prompt_Assembly_detailed.md = prompt slots, authority ordering, and signed prompt artifact.
- 04_L2_Execute_detailed.md = bounded execution and sealed artifacts.
- 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md = final current-run checkout and sealed-result disposition.
- Evaluation_Runtime_Gates_detailed.md = G01-G29 runtime gate decisions and live dispositions.
- 00_L5_Governance_Safety_detailed.md = policy / authority / origin / egress / replay certification evidence.
- 06_Shadow_Evaluation_System_Learning_detailed.md = completed-run evaluation and future-run learning.
- UWG/L4 state files = durable write admission and system-of-record mutation.

========================================================================================================================
CANONICAL CHILD FILE MAP
========================================================================================================================

01.1_Transport_Envelope_Ingress_detailed.md
- Unique surface: raw transport acceptance and envelope validation.
- Owns: RawIngressEnvelope, TransportEnvelopeReceipt, transport allowlist, content-type/encoding checks, attachment handle inventory, malformed envelope report.
- Does not own: identity authority, quota policy, semantic interpretation, route, retrieval, prompt assembly, execution, or final disposition.

01.2_Identity_Tenant_Session_Baseline_detailed.md
- Unique surface: caller, tenant, session, and region baseline binding.
- Owns: CallerIdentityClaim, CallerScopeBaseline, TenantBoundaryReceipt, SessionBindingReceipt, auth evidence capture.
- Does not own: deep resource authorization, L5 certification, route authorization, memory access decision, or final runtime disposition.

01.3_Quota_Size_Duplicate_Controls_detailed.md
- Unique surface: entry quota, size, rate, and duplicate/idempotency controls before L1.
- Owns: QuotaReceipt, DuplicateRequestFingerprint, EntryBudgetReceipt, IngressThrottleReceipt, duplicate suppression evidence.
- Does not own: L0 cost tier, L2 execution budget, provider token accounting, or runtime regression gates.

01.4_Schema_Normalization_and_Ingress_Security_detailed.md
- Unique surface: structural schema validation, payload normalization, raw preservation, and ingress security findings.
- Owns: RequestSchemaValidationReceipt, NormalizedUserPayload, IngressOriginLabelManifest, PayloadSecurityFinding, SanitizationReceipt.
- Does not own: Prompt Assembly airlock, L5 origin-trust certification, C0 retrieved-content classification, or semantic planning.

01.5_Trace_Replay_Correlation_Binding_detailed.md
- Unique surface: request identifiers, trace root, normalized request hash, and ingress replay seed.
- Owns: RequestCorrelationReceipt, TraceRootReceipt, IngressReplaySeed, NormalizedRequestHash, IntakeManifestHash.
- Does not own: route_digest, prompt_hash, evidence_contract_hash, L2 attempt_seed, or completed-run replay comparison.

01.6_Validated_Request_Handoff_detailed.md
- Unique surface: final Intake emission and closed handoff into L1.
- Owns: ValidatedRequest, RejectedRequest, IntakeAuditReceipt, L1HandoffEnvelope, IngressRejectionReport.
- Does not own: L1PlanContract, RouteContract, FinalEvidenceContract, PromptEnvelope, execution packets, ExitDisposition, or durable commit requests.

========================================================================================================================
CANONICAL U0 FLOW
========================================================================================================================

 [ raw inbound request ]
          │
          ▼
 ┌────────────────────────────────────┐
 │ 01.1 TRANSPORT / ENVELOPE          │
 │ accept channel, parse frame,        │
 │ preserve raw hash, reject malformed │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 01.2 IDENTITY / TENANT / SESSION   │
 │ bind caller baseline, tenant,       │
 │ session, region, actor class        │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 01.3 QUOTA / SIZE / DUPLICATE      │
 │ enforce entry limits, detect replay │
 │ and duplicate ingress requests      │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 01.4 SCHEMA / NORMALIZATION        │
 │ validate structure, normalize       │
 │ payload, attach origin labels       │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 01.5 TRACE / REPLAY / CORRELATION  │
 │ assign IDs, trace root, hashes,     │
 │ deterministic ingress manifest      │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 01.6 HANDOFF / REJECTION           │
 │ emit ValidatedRequest or            │
 │ RejectedRequest with audit receipt  │
 └──────────────┬─────────────────────┘
                ▼
          [ L1 reads only ValidatedRequest ]

========================================================================================================================
CANONICAL OUTPUT VOCABULARY
========================================================================================================================

Allowed terminal Intake statuses:
- VALIDATED_FOR_L1
- REJECTED_AT_TRANSPORT
- REJECTED_AT_IDENTITY_BASELINE
- REJECTED_AT_QUOTA
- REJECTED_AT_SCHEMA
- REJECTED_AT_SECURITY_PRECHECK
- REJECTED_AT_CORRELATION_BINDING
- REJECTED_AT_HANDOFF_COMPLETENESS

These are Intake statuses, not Runtime Gate or Exit dispositions.

Canonical receipts:
- RawIngressEnvelope
- TransportEnvelopeReceipt
- CallerScopeBaseline
- TenantBoundaryReceipt
- SessionBindingReceipt
- QuotaReceipt
- DuplicateRequestFingerprint
- RequestSchemaValidationReceipt
- NormalizedUserPayload
- IngressOriginLabelManifest
- RequestCorrelationReceipt
- TraceRootReceipt
- IntakeManifestHash
- ValidatedRequest
- RejectedRequest
- IntakeAuditReceipt

========================================================================================================================
NON-NEGOTIABLE INVARIANTS
========================================================================================================================

1. Intake accepts only supported transports and structurally valid envelopes.
2. Intake preserves raw payload hash before normalization.
3. Intake binds caller, tenant, session, and region baseline before L1 sees the request.
4. Intake enforces quota, size, and duplicate controls before semantic planning.
5. Intake validates request schema before any L1 interpretation.
6. Intake labels inbound content by origin, but does not promote it into authority.
7. Intake assigns request_id, session_id, trace_root, and deterministic ingress hashes.
8. Intake emits either ValidatedRequest or RejectedRequest.
9. Intake never calls a model or tool.
10. Intake never retrieves evidence.
11. Intake never routes.
12. Intake never writes durable state.
13. Intake never approves final output or current-run disposition.
14. Downstream layers must not accept raw inbound payloads that bypass Intake.

========================================================================================================================
GLOBAL NO-OVERLAP LOCK:
- U0 / Intake owns raw ingress, transport envelope, caller/session baseline, quota/duplicate checks, structural schema validation, correlation IDs, trace root, normalized payload handoff, and intake rejection receipts only.
- L1 owns semantic intent interpretation, task_spec, query_spec, ambiguity register, plan contract, and proposed route recommendations.
- L0 owns route selection, RouteContract, grounding_required, execution_form, fallback_chain, and route authority.
- C0 owns retrieval planning, fetching, graph expansion, shaping, final evidence scoring, FinalEvidenceContract, and weak-support refinement.
- Prompt Assembly owns authority-tiered prompt slots, U0 task slot placement, retrieved-content packing, tool/schema binding, and signed provider-ready prompt artifacts.
- L3 owns managed workflow expansion, step dependencies, joins, retries, pause/resume shape, and L3StepContract.
- L2 owns bounded execution, tool/model/script invocation inside capability and sandbox, repair, and sealed work artifacts.
- Runtime Gates and Exit Eval own current-run dispositions and final checkout decisions.
- L5 owns governance certification evidence, origin-trust certification, authority context, provider/egress certification, HITL re-clearance evidence, and replay/audit certification evidence.
- L4/UWG owns durable write admission and system-of-record mutation.
- L6 owns completed-run evaluation, RCA, learning proposals, replay proving, and future-run promotion only.

FORBIDDEN OUTPUTS FROM U0 / INTAKE FILES:
- L1PlanContract
- RouteContract
- RetrievalPlan
- FinalEvidenceContract
- PromptEnvelope
- CompiledPromptArtifact
- L3WorkflowContract
- L3StepContract
- L2ExecutionRequest
- SealedL2Artifact
- ExitReviewPacket
- ExitDisposition
- GateVerdict as final runtime disposition
- CommitRequest
- UWGCommitReceipt
- ShadowEvalRecord
- LearningProposal
- ALLOW
- DENY
- CLARIFY
- ABSTAIN
- REROUTE
- SHRINK_SCOPE
- RETRY
- HEAL
- ESCALATE_HITL
- QUARANTINE
- REDACT
- SAFE_FALLBACK
- MARK_DEGRADED
- COMMIT_REQUEST
- BLOCK_COMMIT
- ALLOW_FINISH
- approve_execution
- approve_output
- approve_write

ALLOWED OUTPUT STYLE:
- intake receipts
- validation manifests
- normalized request envelopes
- caller/session/tenant baselines
- quota and duplicate receipts
- trace/correlation receipts
- rejected_request packets
- validated_request packets
- hashes, evidence refs, reason codes, and non-authoritative hints only

========================================================================================================================
