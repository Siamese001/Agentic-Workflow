========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03B_PA_Prompt_Assembly
Canonical file: Prompt_Assembly.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: Prompt_Assembly.md
Owner summary: Prompt Assembly composer. Owns authority-tiered PromptEnvelope/CompiledPromptArtifact construction from verified evidence, governance artifacts, user intent, schema, and execution metadata.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

========================================================================================================================
PROMPT ASSEMBLY - PARENT DOCTRINE
NO-OVERLAP FULL OVERWRITE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent file defines Prompt Assembly at doctrine level only.

Prompt Assembly is the trusted composer that binds verified C0 evidence, governance artifacts, user intent after airlock
neutralization, output schema, tool posture, provider lane, and deterministic replay metadata into a signed
CompiledPromptArtifact for L2 execution.

Prompt Assembly never retrieves evidence, never routes, never executes, never calls providers, never mutates durable state,
never approves final output, and never decides current-run disposition.

This parent delegates implementation detail to eight child files:
- PA.0 Boundary Check
- PA.1 Load / Resolve Prompt BOM
- PA.2 Slot Composition
- PA.3 Airlock / Security Pass
- PA.4 Validate Slot Contract
- PA.5 Token Budget / Determinism
- PA.6 Provider-Aware Rendering
- PA.7 Final Emit / Compiled Prompt Artifact

PARENT ROLE
------------------------------------------------------------------------------------------------------------------------
- Define Prompt Assembly doctrine.
- Define Prompt Assembly-owned vocabulary.
- Define top-level input and output shape.
- Define the no-overlap law.
- Define child ownership map.
- Define cross-child invariants.
- Define traceability expectations.
- Keep implementation-grade mechanics inside the child files.

PARENT DOES NOT OWN IMPLEMENTATION DETAIL
------------------------------------------------------------------------------------------------------------------------
The child files own implementation-grade detail. This parent should not restate their full contracts.

GLOBAL NO-OVERLAP LOCK:
- L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations.
- L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority.
- C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract.
- L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence.
- Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission.
- L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts.
- Runtime Gates and Exit Eval own current-run dispositions.
- UWG/L4 owns durable write admission and system-of-record mutation.
- L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning.

FORBIDDEN OUTPUTS FROM THIS CHILD:
- ALLOW, DENY, CLARIFY, ABSTAIN, REROUTE, SHRINK_SCOPE, RETRY, HEAL, ESCALATE_HITL
- QUARANTINE, REDACT, SAFE_FALLBACK, MARK_DEGRADED, COMMIT_REQUEST, BLOCK_COMMIT, ALLOW_FINISH
- approve_execution, approve_output, approve_write, call_provider, execute_tool, mutate_l4

ALLOWED OUTPUT STYLE:
- receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs


SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL:
- PromptBOM vocabulary.
- canonical slot vocabulary.
- authority-tiered slot ordering doctrine.
- assembly boundary law.
- provider-ready artifact vocabulary.
- signed CompiledPromptArtifact expectation.
- manifest_hash / HMAC requirement at the prompt-artifact layer.
- deterministic prompt packet discipline.

PROMPT ASSEMBLY DOES NOT OWN:
- request intake.
- intent interpretation.
- route authority.
- evidence retrieval or evidence scoring.
- graph traversal.
- runtime gate dispositions.
- model/tool execution.
- provider invocation.
- durable writes.
- L5 certification doctrine.
- completed-run learning.

CANONICAL PROMPT ASSEMBLY INPUTS
------------------------------------------------------------------------------------------------------------------------
1. L1PlanContract reference:
   - task_spec, query_spec, output target, support expectation, declared assumptions, unresolved gaps.

2. L0RouteContract reference:
   - selected route, execution_form, provider lane, route risk, policy posture, cache/freshness posture,
     model_id, temperature, thinking_level, replay_key, route digest references.

3. C0 FinalEvidenceContract reference when grounding is required:
   - verified chunks, cited spans, source_ids, lineage, support score, support gaps, contradiction flags,
     abstain recommendation when support is weak.

4. Governance artifacts:
   - system_version_hash, policy_hash, role fences, allowed tool posture, AgentSpec, response schema contract,
     origin trust and authority refs where required.

5. User and execution metadata:
   - raw user task reference, neutralized user task candidate, plan_id, idempotency nonce, provider target,
     replay metadata.

CANONICAL PROMPT ASSEMBLY OUTPUT
------------------------------------------------------------------------------------------------------------------------
CompiledPromptArtifact:
- artifact_id
- request_id / run_id / trace_id / route_id / plan_id
- provider_lane / symbolic_model_id / resolved_model_id if known
- structured_slots_used
- provider_specific_messages or prompt fields
- allowed_tools_schema reference via API tools field
- R0 response_schema binding via provider-native structured output field
- token estimate / budget status
- manifest_hash over canonical structured slot bytes
- hmac_sig over manifest_hash and required metadata
- replay_key / policy_hash / blueprint_hash / route digest refs
- source evidence refs and C0 FinalEvidenceContract ref when grounded
- origin/security validation receipts
- slot validation receipt
- deterministic trimming receipt if trimming occurred
- render manifest and provider adapter receipt

STATUS VOCABULARY
------------------------------------------------------------------------------------------------------------------------
Allowed Prompt Assembly statuses:
- PA_READY
- PA_INPUT_INCOMPLETE
- PA_BOUNDARY_MISMATCH
- PA_BOM_RESOLVED
- PA_BOM_GAP
- PA_SLOTS_COMPOSED
- PA_SECURITY_PASS
- PA_SECURITY_GAP
- PA_SLOT_CONTRACT_VALID
- PA_SLOT_CONTRACT_INVALID
- PA_BUDGET_FIT
- PA_BUDGET_TRIMMED
- PA_BUDGET_OVERFLOW
- PA_RENDERED
- PA_RENDER_GAP
- PA_ARTIFACT_SIGNED
- PA_ARTIFACT_NOT_SIGNED
- PA_L2_HANDOFF_READY
- PA_REQUIRES_UPSTREAM_REPAIR

Forbidden as Prompt Assembly outputs:
- runtime dispositions such as ALLOW, DENY, REROUTE, ESCALATE_HITL, COMMIT_REQUEST, BLOCK_COMMIT, ALLOW_FINISH.
- execution verbs such as call_provider, execute_tool, approve_output, approve_write, mutate_l4.

CANONICAL SLOT MAP
------------------------------------------------------------------------------------------------------------------------
┌────────┬──────────────────────────────┬──────────────────────────────┬──────────────────────────────────────────────┐
│ SLOT   │ NAME                         │ AUTHORITY                    │ PURPOSE                                      │
├────────┼──────────────────────────────┼──────────────────────────────┼──────────────────────────────────────────────┤
│ S0     │ SYSTEM / STATE               │ ABSOLUTE                     │ Constitution, identity floor, invariants      │
│ D0     │ INJECTIONS / FENCES          │ BINDING                      │ Role boundaries, scope, anti-injection        │
│ I0     │ INSTRUCTIONAL                │ GOVERNED                     │ Agent capability and operating manual         │
│ E0     │ EXEMPLARS                    │ GUIDING                      │ Few-shot examples and golden answer shapes    │
│ C0     │ GROUNDED CONTEXT             │ INFORMATIONAL                │ Verified evidence, citations, source limits   │
│ M0     │ PRIVATE META-CONTROLS        │ PRIVATE                      │ Provider-safe reasoning posture controls      │
│ U0     │ USER TASK                    │ ZERO                         │ Neutralized task intent only                  │
│ Y0     │ SYNTHESIS / LEARNING PRIORS  │ ANALYTIC                     │ Approved prior patterns if policy permits     │
│ H0     │ HEALING HINTS                │ PROPOSED                     │ Bounded repair hints if valid                 │
│ R0     │ OUTPUT SCHEMA                │ SCHEMA                       │ Provider-native structured output binding     │
└────────┴──────────────────────────────┴──────────────────────────────┴──────────────────────────────────────────────┘

AUTHORITY ORDER
------------------------------------------------------------------------------------------------------------------------
Highest to lowest:
1. S0 system/state
2. D0 fences/injections
3. I0 instructional
4. E0 exemplars
5. C0 grounded context as data
6. M0 private controls
7. U0 user task intent
8. Y0 approved analytic priors if included
9. H0 repair proposal if included
10. R0 output schema bound out-of-band through provider-native structured-output field

Important:
- R0 is binding schema, but should be bound through API response_schema / response_format where available.
- Tools are bound through provider API tool fields, not stringified as loose prompt prose.
- Lower-authority slots may inform content or format only within higher-authority limits.
- Lower-authority slots cannot override higher-authority slots.

CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
PA.0_Boundary_Check.md
- Unique surface: assembly eligibility and input completeness.
- Owns PAAssemblyInput, boundary checklist, source-of-truth refs, missing-input gap report.

PA.1_Load_Resolve_Prompt_BOM.md
- Unique surface: PromptBOM resolution.
- Owns component refs, selected system/fence/instruction/exemplar/context/schema/execution metadata inventory.

PA.2_Slot_Composition.md
- Unique surface: canonical slot construction and authority-tier ordering.
- Owns StructuredPromptSlots, slot authority map, override-prevention map, slot lineage map.

PA.3_Airlock_Security_Pass.md
- Unique surface: assembly-time security pass.
- Owns U0 airlock, C0 payload classifier, H0 re-entry validation, safe slot payload map.

PA.4_Validate_Slot_Contract.md
- Unique surface: final slot contract validation before budgeting/rendering.
- Owns authority-order validation, context contract validation, schema/tool binding validation.

PA.5_Token_Budget_Determinism.md
- Unique surface: token budgeting and deterministic prompt-packet shaping.
- Owns token budget ledger, deterministic trimming plan, stable prefix rules, canonical hash input discipline.

PA.6_Provider_Aware_Rendering.md
- Unique surface: provider-specific rendering.
- Owns ProviderRenderManifest, adapter mapping, provider field placement, render gap reports.

PA.7_Final_Emit_Compiled_Prompt_Artifact.md
- Unique surface: final signed prompt artifact emission.
- Owns CompiledPromptArtifact, manifest_hash, HMAC signature, artifact receipt, L2 handoff envelope.

CROSS-CHILD INVARIANTS
------------------------------------------------------------------------------------------------------------------------
PA.I1  Prompt Assembly composes only. It does not retrieve, route, execute, call providers, or write.
PA.I2  Prompt Assembly consumes C0 evidence. It does not alter C0 support scores or invent missing citations.
PA.I3  Every slot payload must preserve origin, authority, source refs, and replay/audit refs where applicable.
PA.I4  User text is task intent only, not policy authority.
PA.I5  Retrieved/tool/human/model/prior content is data unless higher authority explicitly binds it otherwise.
PA.I6  Lower-authority slots cannot override higher-authority slots.
PA.I7  Tools and schemas ride provider-native API fields where supported, not loose prompt prose.
PA.I8  Required governing instructions and required evidence cannot be silently dropped for token budget.
PA.I9  Canonical structured slot bytes, not provider-specific formatting, drive manifest_hash.
PA.I10 Same PromptBOM + same structured slots + same trimming rules + same signing secret must produce the same hash/signature.
PA.I11 If assembly cannot preserve required authority/evidence/schema, emit PA gap evidence instead of pretending completeness.
PA.I12 PA.7 handoff to L2 is an artifact handoff only. L2 still validates and executes under its own authority.

END-TO-END POSITION
------------------------------------------------------------------------------------------------------------------------
[Validated Request]
    -> [L1 PlanContract]
    -> [L0 RouteContract]
    -> [C0 FinalEvidenceContract when grounding required]
    -> [Prompt Assembly: PA.0 -> PA.7]
    -> [CompiledPromptArtifact]
    -> [L2 SovereignLLMGateway / bounded execution]
    -> [Sealed L2 Artifact]
    -> [Exit Eval & Runtime Gates]
    -> [Response / reroute / escalation / UWG commit request if applicable]

ACCEPTANCE EXPECTATIONS
------------------------------------------------------------------------------------------------------------------------
A complete implementation must prove:
- Prompt Assembly refuses to run without required L1/L0 refs.
- Grounded routes require a valid C0 FinalEvidenceContract.
- Slots are built in canonical authority order.
- User and retrieved text cannot override higher-authority slots.
- Tool schemas and response schemas are provider-native bindings, not loose prompt prose.
- Token overflow emits a deterministic gap status rather than silently dropping mandatory content.
- Provider rendering preserves canonical manifest hash independence.
- Final artifact is signed and replay-bound.
- No Prompt Assembly code path retrieves, routes, executes, calls providers, writes L4, or decides final disposition.
==============================================================================================================================
GAP-CLOSED PARENT UPDATE | PA AUTHORITY RED-TEAM PROOF
==============================================================================================================================
PA.8_Authority_RedTeam_Slot_Verification.md is now the canonical child for Prompt Assembly-specific slot authority proof,
injection fixtures, provider render equivalence, and R0 schema binding proof. PA still does not retrieve, route, execute, or write.
