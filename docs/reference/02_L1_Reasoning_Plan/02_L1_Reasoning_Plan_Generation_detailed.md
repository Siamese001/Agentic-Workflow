========================================================================================================================
02_L1_REASONING_PLAN_GENERATION_DETAILED.md
PARENT L1 REASONING + PLAN GENERATION DOCTRINE
NO-OVERLAP FULL OVERWRITE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent file defines L1 Reasoning + Plan Generation at doctrine level only.

L1 is the governed Research Desk. It reads a structurally valid ValidatedRequest from Intake, understands the user goal,
separates user intent from system authority, loads approved planning references from L4 read surfaces, and emits a bounded,
replayable L1PlanContract that L0 may use for routing.

L1 does not retrieve final evidence, route with authority, execute tools, call external providers for work, mutate durable
state, approve egress, approve HITL, commit through UWG, or learn into the current run.

PARENT ROLE
------------------------------------------------------------------------------------------------------------------------
- Define L1 authority doctrine.
- Define L1-owned planning language.
- Define no-overlap law.
- Define source ownership boundaries.
- Define canonical child file map.
- Define the high-level L1 flow.
- Define the canonical L1PlanContract vocabulary.
- Define traceability and replay expectations.

PARENT DOES NOT OWN IMPLEMENTATION DETAIL
------------------------------------------------------------------------------------------------------------------------
The child files own implementation-grade detail. This parent should not restate their full contracts.

Child details are intentionally moved into:
- 02.1 through 02.6 below.

========================================================================================================================
SOURCE OWNERSHIP BOUNDARY
========================================================================================================================

L1 OWNS AT DOCTRINE LEVEL:
- semantic intent interpretation over a ValidatedRequest
- constraint extraction and deliverable framing
- ambiguity and assumptions register
- approved planning-prior reads from L4
- rule-aware planning frame
- internal contextual refinement for planning only
- advisory decomposition into work units
- advisory route hints, never route authority
- support expectation and grounding need marker
- action expectation, HITL hint, UWG hint, sandbox/capability hints
- validation of the plan as a plan
- lowest viable agency recommendation
- L1PlanContract emission

L1 DOES NOT OWN:
- transport/envelope validation
- identity/tenant/session baseline binding
- quota and ingress duplicate controls
- route authority
- retrieval or evidence scoring
- prompt slot assembly
- managed workflow execution plan authority after route selection
- tool/model execution
- live runtime gate dispositions
- governance certification evidence
- durable writes
- completed-run learning

SOURCE OWNERS:
- 01_Request_Intake_detailed.md = ValidatedRequest / RejectedRequest and ingress trace_root.
- 03_L0_Route_Decision_Switching_L3_detailed.md = authoritative RouteContract and selected route.
- C0_Context_Engine_detailed.md = retrieval, evidence verification, weak-support refinement, and FinalEvidenceContract.
- Prompt_Assembly_detailed.md = prompt slots, PromptBOM, PromptEnvelope, CompiledPromptArtifact, and provider rendering.
- 04_L2_Execute_detailed.md = bounded execution and sealed artifacts.
- 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md = final current-run checkout and sealed-result disposition.
- Evaluation_Runtime_Gates_detailed.md = G01-G29 runtime gate decisions and live dispositions.
- 00_L5_Governance_Safety_detailed.md = policy, authority, origin, egress, replay, audit certification evidence.
- 06_Shadow_Evaluation_System_Learning_detailed.md = completed-run evaluation and future-run learning.
- UWG/L4 state files = durable write admission and system-of-record mutation.

========================================================================================================================
CANONICAL CHILD FILE MAP
========================================================================================================================

02.1_Intent_Frame_and_Ambiguity_Register_detailed.md
- Unique surface: parse the patron slip into intent, constraints, details, job class, ambiguity, assumptions, and first
  safety/authority reading.
- Owns: IntentFrame, AmbiguityRegister, FirstSafetyAuthorityReading, ParsedRequestReceipt.
- Does not own: planning priors, route decision, retrieval, execution, final answer, or durable write.

02.2_Planning_Priors_and_Rule_Bundle_detailed.md
- Unique surface: read approved planning references from L4 and build a rule-aware planning bundle.
- Owns: PlanningPriorReadPlan, PlanBundle, PlanningReferenceManifest, RuleAwarePlanningFrame.
- Does not own: answer evidence retrieval, C0 source retrieval, L5 certification, or runtime gate disposition.

02.3_Contextual_Refinement_Reasoning_Loop_detailed.md
- Unique surface: internal planning-only contextual refinement and bounded reasoning loop.
- Owns: PlanningReasoningTraceSummary, RefinementPassReceipt, InternalPlanState, PlanningLoopBudgetReceipt.
- Does not own: chain-of-thought exposure, external model calls, retrieval, route authority, execution, or durable learning.

02.4_Draft_Plan_and_Route_Hints_detailed.md
- Unique surface: convert interpreted intent into advisory work units, sequencing, route hints, support expectations, and
  action expectations.
- Owns: DraftPlan, WorkUnitSet, DependencySketch, RouteHintSet, SupportExpectation, ActionExpectation.
- Does not own: RouteContract, C0 RetrievalPlan, L3WorkflowContract, L2ExecutionRequest, or final disposition.

02.5_Plan_Validation_Self_Repair_detailed.md
- Unique surface: validate the plan as a plan, apply lowest viable agency, and run bounded self-repair or abstain/clarify markers.
- Owns: PlanValidationReport, PlanConsistencyAudit, LowestViableAgencyReceipt, L1SelfRepairLedger.
- Does not own: runtime retry/HEAL, Exit disposition, C0 weak-support refinement, or L2 repair.

02.6_L1PlanContract_Handoff_detailed.md
- Unique surface: freeze and emit the canonical L1PlanContract to L0.
- Owns: L1PlanContract, PlanDigest, L1HandoffReceipt, PlanTelemetryKeys, NonAuthorityAssertion.
- Does not own: downstream route, retrieval, prompt, execution, checkout, commit, or learning artifacts.

========================================================================================================================
CANONICAL L1 FLOW
========================================================================================================================

 [ ValidatedRequest from U0 ]
          │
          ▼
 ┌────────────────────────────────────┐
 │ 02.1 INTENT FRAME / AMBIGUITY      │
 │ parse goal, deliverable, constraints│
 │ details, job class, gaps, risk hints│
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 02.2 PLANNING PRIORS / RULE BUNDLE │
 │ read L4 planning references only;   │
 │ build rule-aware plan frame         │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 02.3 CONTEXTUAL REFINEMENT LOOP    │
 │ planning-only refinement; no tools, │
 │ no C0, no route commitment          │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 02.4 DRAFT PLAN / ROUTE HINTS      │
 │ work units, order, support target,  │
 │ action expectation, advisory route  │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 02.5 VALIDATE / SELF-REPAIR        │
 │ did we listen, safe, coherent, low- │
 │ agency, clarify/abstain if needed  │
 └──────────────┬─────────────────────┘
                ▼
 ┌────────────────────────────────────┐
 │ 02.6 CONTRACT / HANDOFF            │
 │ freeze L1PlanContract and hand to   │
 │ L0 as advisory input only           │
 └──────────────┬─────────────────────┘
                ▼
          [ L0 reads L1PlanContract ]

========================================================================================================================
CANONICAL OUTPUT VOCABULARY
========================================================================================================================

L1PlanContract carries:
- identity
- intent_frame
- query_spec
- task_spec
- route_hint
- support_expectation
- action_expectation
- assumptions_and_gaps
- validation_summary
- downstream_notes
- plan_digest
- replay metadata
- non-authority assertion

L1 status vocabulary:
- L1_PLAN_READY
- L1_PLAN_CLARIFY_RECOMMENDED
- L1_PLAN_ABSTAIN_RECOMMENDED
- L1_PLAN_SAFE_FALLBACK_RECOMMENDED
- L1_PLAN_POLICY_REVIEW_NEEDED
- L1_PLAN_INVALID_INPUT_REFERENCE
- L1_PLAN_UNSUPPORTED_DELIVERABLE

These are plan statuses and recommendations only. They are not runtime dispositions.

========================================================================================================================
GLOBAL NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
- U0 / Request Intake owns transport, envelope, identity baseline, quota, duplicate, structural schema, request IDs,
  trace_root assignment, and ValidatedRequest / RejectedRequest emission.
- L1 owns semantic interpretation, advisory planning, ambiguity register, support expectation, risk hints, route hints,
  and the L1PlanContract only.
- L0 owns authoritative route selection, RouteContract, route_digest, hmac_sig, grounding_required as route authority,
  execution_form, fallback_chain, and route telemetry.
- C0 owns retrieval planning, evidence fetch, graph expansion, shaping, verification, scoring, weak-support refinement,
  cited spans, source lineage, and FinalEvidenceContract.
- Prompt Assembly owns authority-tiered slot construction, PromptBOM, PromptEnvelope / CompiledPromptArtifact,
  provider-aware rendering, response schema binding, and prompt signature.
- L3 owns managed workflow expansion, step DAG, joins, retries, pause/resume, and L3StepContract emission when L0
  selected a managed workflow route.
- L2 owns bounded execution, model/tool invocation inside granted capability, E1-E5 lifecycle, proposed_state_diff,
  and SealedL2Artifact.
- Exit Eval and Runtime Gates own current-run dispositions, final checkout, egress decision, escalation decision,
  and commit-request decision.
- L5 owns governance certification evidence, authority context, origin trust, policy/registry/capability/sandbox/egress,
  replay/audit certification, HITL reclearance evidence, and static governance drift evidence.
- UWG / L4 owns durable write admission, commit receipt, system-of-record mutation, archive surfaces, cache promotion,
  and durable state.
- L6 owns completed-run exhaust ingestion, evaluation, calibration, RCA, learning proposals, replay proof for future-run
  changes, and promotion requests through UWG only.

FORBIDDEN AUTHORITATIVE OUTPUTS FROM L1
------------------------------------------------------------------------------------------------------------------------
L1 must not emit or claim authority over:
- RouteContract
- route_digest
- hmac_sig
- FinalEvidenceContract
- PromptEnvelope
- CompiledPromptArtifact
- L3WorkflowContract
- L3StepContract
- L2ExecutionRequest
- SealedL2Artifact
- ExitReviewPacket
- ExitDisposition
- GateDisposition
- CommitRequest
- UWGCommitReceipt
- durable memory update
- final answer approval
- tool/model execution approval
- current-run learning promotion

ALLOWED L1 OUTPUT STYLE
------------------------------------------------------------------------------------------------------------------------
L1 may emit only:
- intent frames
- ambiguity registers
- task specs
- query specs
- support expectations
- action expectations
- advisory route hints
- risk markers
- assumptions and gaps
- validation summaries
- downstream notes
- L1PlanContract receipts, hashes, and trace metadata

========================================================================================================================
ACCEPTANCE CRITERIA
========================================================================================================================

A compliant implementation proves:
- L1 consumes only ValidatedRequest or an explicit RejectedRequest summary.
- L1 emits an L1PlanContract, not an answer and not a RouteContract.
- L1 preserves request_id, trace_root, policy_hash, instruction_hash, and source_envelope_id.
- L1 separates user intent from authority.
- L1 marks grounding need when citations, files, code, policy, freshness, or evidence-backed claims are required.
- L1 marks action and write risk without executing.
- L1 marks HITL and UWG hints without approving or committing.
- L1 can choose direct-answer recommendation when safe, avoiding fake workflow complexity.
- L1 self-repair is bounded and cannot call tools or retrieve evidence.
- L1 OTEL spans prove parse -> priors -> reason -> draft -> validate -> handoff.
- L1 deterministic digest proves replay of the same input produces the same plan fields, except allowed volatile metadata.

========================================================================================================================
END OF PARENT L1 REASONING + PLAN GENERATION DOCTRINE
========================================================================================================================
