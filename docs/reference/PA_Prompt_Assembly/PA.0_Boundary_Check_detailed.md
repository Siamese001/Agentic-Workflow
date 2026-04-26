========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: PA_Prompt_Assembly
Canonical file: PA.0_Boundary_Check_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: PA.0_Boundary_Check_detailed.md
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
CHILD FILE PA.0 BOUNDARY CHECK
PA.0_Boundary_Check_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.0_Boundary_Check_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- Prompt Assembly eligibility and upstream input boundary only

THIS FILE OWNS:
- PAAssemblyInput, BoundaryCheckReceipt, required-input inventory, upstream reference map, assembly gap reports

THIS FILE DOES NOT OWN:
- PromptBOM resolution, slot composition, security pass, token budget, provider rendering, final signing, retrieval, routing, execution

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

END OVERWRITE RECONCILIATION HEADER
========================================================================================================================

PARENT:
- Prompt_Assembly_detailed.md

ROLE:
- Detailed child file for PA.0 BOUNDARY CHECK.
- Defines the implementation-grade requirements for its unique Prompt Assembly surface.
- Emits Prompt Assembly evidence only.
- Does not emit runtime dispositions.
- Does not retrieve, route, execute, call providers, write durable state, or promote learning.

WHY THIS FILE EXISTS
------------------------------------------------------------------------------------------------------------------------
- Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata,
  replay metadata, and output requirements into one packet that L2 will execute later.
- This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly
  mechanics by accident.
- This child is intentionally detailed enough for implementation, tests, traces, and replay evidence.

PRIMARY QUESTION
------------------------------------------------------------------------------------------------------------------------
- "Prompt Assembly eligibility and upstream input boundary only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. PAAssemblyInput
------------------------------------------------------------------------------------------------------------------------
PURPOSE:
- Normalize all upstream references into one assembly request.
- Preserve the difference between references and payloads.
- Prevent Prompt Assembly from being invoked as a hidden retriever, router, executor, or policy authority.

FIELDS:
- assembly_request_id
- request_id / run_id / trace_id
- route_id / plan_id
- L1PlanContract_ref
- L0RouteContract_ref
- C0FinalEvidenceContract_ref if grounding_required
- governance_artifact_refs[]
- AgentSpec_ref
- response_schema_contract_ref
- raw_user_task_ref
- neutralized_user_task_candidate_ref if already available
- provider_target_ref
- model_policy_ref
- replay_key
- policy_hash
- blueprint_hash
- route_digest
- idempotency_nonce
- expected_artifact_type
- assembly_budget_hint

MUST CHECK:
- request_id, run_id, trace_id exist.
- L1PlanContract_ref exists.
- L0RouteContract_ref exists.
- route_id matches RouteContract.
- plan_id matches PlanContract.
- policy_hash is present.
- replay_key is present when route requires replay.
- provider lane is declared when model execution is expected.
- response schema contract exists when structured output is required.
- C0FinalEvidenceContract_ref exists when grounding_required = true.
- C0FinalEvidenceContract_ref is absent or marked not_applicable when route is terminal R1/R5.
2. Boundary Checklist
------------------------------------------------------------------------------------------------------------------------
CHECKS:
- C0 already retrieved if grounding is required.
- L0 already selected the route.
- L1 already produced the task/plan contract.
- L5 evidence refs are present where the RouteContract requires them.
- PA is not being asked to retrieve, route, execute, write, or approve output.
- Terminal short-circuit routes do not accidentally enter model prompt assembly unless explicitly converted by a governed contract.
- Managed workflow steps include current step context but not authority to expand the workflow.
3. Gap Handling
------------------------------------------------------------------------------------------------------------------------
If PA.0 cannot prove eligibility:
- emit PA_INPUT_INCOMPLETE or PA_BOUNDARY_MISMATCH.
- attach missing_required_refs[].
- attach mismatched_refs[].
- attach upstream_owner_hint = L1 | L0 | C0 | L5 | AgentSpec | unknown.
- do not fill gaps from user text.
- do not fetch missing evidence.
- do not proceed to PA.1.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_READY
- PA_INPUT_INCOMPLETE
- PA_BOUNDARY_MISMATCH
- PA_REQUIRES_UPSTREAM_REPAIR

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- PAAssemblyInput
- BoundaryCheckReceipt
- required_input_inventory
- upstream_reference_map
- assembly_gap_report
- boundary_status_receipt

MUST NOT
------------------------------------------------------------------------------------------------------------------------
- retrieve evidence
- route or reroute
- call a model provider
- execute a tool
- approve the final answer
- commit durable state
- emit runtime dispositions
- silently drop mandatory evidence, authority, schema, or replay metadata

ACCEPTANCE TESTS
------------------------------------------------------------------------------------------------------------------------
- No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition.
- All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available.
- All gap conditions are explicit and replayable.
- Missing L0 RouteContract produces PA_INPUT_INCOMPLETE.
- grounding_required=true without C0FinalEvidenceContract_ref produces PA_INPUT_INCOMPLETE.
- RouteContract terminal short-circuit plus provider prompt request produces PA_BOUNDARY_MISMATCH.
