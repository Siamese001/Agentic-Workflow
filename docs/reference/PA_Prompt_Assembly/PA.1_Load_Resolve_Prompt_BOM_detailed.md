========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: PA_Prompt_Assembly
Canonical file: PA.1_Load_Resolve_Prompt_BOM_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: PA.1_Load_Resolve_Prompt_BOM_detailed.md
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
CHILD FILE PA.1 LOAD / RESOLVE PROMPT BOM
PA.1_Load_Resolve_Prompt_BOM_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.1_Load_Resolve_Prompt_BOM_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- PromptBOM resolution only

THIS FILE OWNS:
- PromptBOM, component resolver receipts, selected component refs, system/fence/instruction/exemplar/context/schema/execution metadata inventory

THIS FILE DOES NOT OWN:
- slot ordering, airlock/security sanitization, token budgeting, provider rendering, final artifact signing, execution

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
- Detailed child file for PA.1 LOAD / RESOLVE PROMPT BOM.
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
- "PromptBOM resolution only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. PromptBOM Schema
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- prompt_bom_id
- assembly_request_id
- request_id / run_id / trace_id / route_id / plan_id
- system_component_ref
- system_version_hash
- fence_component_refs[]
- policy_posture_ref
- instruction_mixin_refs[]
- AgentSpec_ref
- exemplar_refs[]
- exemplar_selection_reason[]
- C0FinalEvidenceContract_ref
- context_component_refs[]
- response_schema_contract_ref
- tool_schema_refs[]
- execution_metadata_ref
- provider_target_ref
- model_settings_ref
- replay_key
- policy_hash
- blueprint_hash
- component_hashes{}
- bom_hash
- bom_gap_report_ref

MUST CHECK:
- every selected component has a stable ref.
- every selected component has a hash or immutable version.
- system component matches system_version_hash.
- fences match policy posture and route risk.
- instructions match AgentSpec and task class.
- exemplars are allowed for task class and budget posture.
- C0 context ref matches route grounding requirement.
- R0 schema ref exists when structured output is required.
- tool schema refs match allowed tool posture.
- execution metadata carries replay_key and policy_hash.
2. Resolution Steps
------------------------------------------------------------------------------------------------------------------------
PA.1.1 Resolve S0 system/state:
- Select by system_version_hash.
- Load constitution, identity floor, and safety invariants as references.
- Emit system_component_receipt.

PA.1.2 Resolve D0 fences:
- Select by policy posture, route risk, task class, tenant/region/data class, and tool posture.
- Bind injection fences, role boundaries, scope limits, and anti-injection controls.

PA.1.3 Resolve I0 instructional mixins:
- Select by AgentSpec, task type, artifact type, and route execution form.
- Bind capability instructions and operating manuals.

PA.1.4 Resolve E0 exemplars:
- Select only approved examples compatible with task class, schema, policy, and token budget.
- If examples are unsafe or unneeded, omit with reason, not silent drop.

PA.1.5 Resolve C0 context:
- Consume C0 FinalEvidenceContract only.
- Map verified chunks, citations, source limits, contradiction flags, and gap metadata into context refs.

PA.1.6 Resolve R0 output schema:
- Select from AgentSpec / task contract / route output target.
- Preserve provider-native schema binding intent.

PA.1.7 Resolve execution metadata:
- Bind replay_key, policy_hash, plan_id, idempotency nonce, model_id, temperature, thinking_level, provider lane.
3. BOM Gaps
------------------------------------------------------------------------------------------------------------------------
GAP TYPES:
- missing_system_component
- missing_fence_component
- missing_instruction_mixin
- exemplar_conflict
- c0_context_missing_for_grounded_route
- response_schema_missing
- tool_schema_missing
- execution_metadata_missing
- policy_hash_mismatch
- stale_component_ref
- unsupported_provider_target


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_BOM_RESOLVED
- PA_BOM_GAP
- PA_REQUIRES_UPSTREAM_REPAIR

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- PromptBOM
- bom_resolution_receipt
- component_inventory
- component_hash_map
- bom_gap_report
- bom_hash_receipt

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
- Same PAAssemblyInput resolves same PromptBOM and bom_hash.
- Grounded route without C0 contract produces bom_gap_report.
- Exemplar conflicting with R0 schema is excluded with reason.
