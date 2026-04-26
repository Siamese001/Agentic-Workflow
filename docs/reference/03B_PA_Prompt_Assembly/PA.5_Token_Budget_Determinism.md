========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03B_PA_Prompt_Assembly
Canonical file: PA.5_Token_Budget_Determinism.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: PA.5_Token_Budget_Determinism.md
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
CHILD FILE PA.5 TOKEN BUDGET / DETERMINISM
PA.5_Token_Budget_Determinism.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.5_Token_Budget_Determinism.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- token budgeting and deterministic prompt-packet shaping only

THIS FILE OWNS:
- TokenBudgetLedger, deterministic trimming receipt, stable prefix receipt, canonical hash input manifest, overflow gap reports

THIS FILE DOES NOT OWN:
- provider rendering, final signing, L2 replay execution/comparison, runtime budget gate dispositions

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
- Prompt_Assembly.md

ROLE:
- Detailed child file for PA.5 TOKEN BUDGET / DETERMINISM.
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
- "token budgeting and deterministic prompt-packet shaping only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. Token Budget Input
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- budget_request_id
- SlotValidationReceipt_ref
- structured_slots_id
- provider_lane
- symbolic_model_id
- max_context_tokens
- reserved_output_tokens
- response_schema_overhead_estimate
- tool_call_overhead_estimate
- stable_prefix_policy_ref
- route_budget_ref
- C0_priority_order_ref
- replay_key
- policy_hash
2. Token Budget Ledger
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- token_budget_ledger_id
- input_token_budget
- reserved_output_tokens
- schema_overhead_tokens
- tool_overhead_tokens
- available_prompt_tokens
- slot_token_estimates{}
- mandatory_token_total
- optional_token_total
- trimming_needed
- trimming_plan_ref
- overflow_status
- budget_hash

MUST CHECK:
- output token reserve exists.
- response schema reserve exists when structured output is required.
- tool overhead reserve exists when tool use is possible.
- S0/D0/I0 fit before optional content.
- R0 schema binding fits or provider supports out-of-band schema without prompt token impact.
- C0 must-use evidence fits for grounded answer or overflow is raised.
3. Deterministic Trimming Order
------------------------------------------------------------------------------------------------------------------------
Apply this order:
1. Remove/compress oldest optional conversation history if present.
2. Remove lowest-ranked optional E0 exemplars.
3. Remove lowest-ranked optional C0 chunks that are not must-use and not citation anchors.
4. Compress optional Y0/H0 hints if allowed.
5. Preserve S0/D0/I0 intact.
6. Preserve must-use evidence and citation anchors.
7. Preserve R0 binding.
8. If mandatory content still cannot fit, emit PA_BUDGET_OVERFLOW.

TRIMMING RECEIPT FIELDS:
- trimming_receipt_id
- removed_items[]
- compressed_items[]
- preserved_mandatory_items[]
- reason_codes[]
- before_token_estimate
- after_token_estimate
- deterministic_order_version
- trimming_hash
4. Canonical Hash Input Discipline
------------------------------------------------------------------------------------------------------------------------
Canonical prompt bytes include:
- selected slot IDs.
- canonical slot order.
- normalized slot payloads after trimming.
- schema binding refs.
- tool binding refs.
- provider lane metadata that affects rendered meaning.
- policy_hash / blueprint_hash / replay_key where required.

Canonical prompt bytes exclude:
- idempotency nonce.
- wall-clock created_at if not run-clock normalized.
- transient object memory addresses.
- provider request IDs not known until execution.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_BUDGET_FIT
- PA_BUDGET_TRIMMED
- PA_BUDGET_OVERFLOW
- PA_REQUIRES_UPSTREAM_REPAIR

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- TokenBudgetLedger
- deterministic_trimming_receipt
- stable_prefix_receipt
- overflow_gap_report
- canonical_hash_input_manifest
- budget_status_receipt

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
- Optional exemplar is removed before must-use C0 citation anchor.
- Required evidence overflow emits PA_BUDGET_OVERFLOW.
- Idempotency nonce does not change canonical manifest hash.
