========================================================================================================================
CHILD FILE PA.4 VALIDATE SLOT CONTRACT
PA.4_Validate_Slot_Contract_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.4_Validate_Slot_Contract_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- assembled slot contract validation only

THIS FILE OWNS:
- SlotValidationReceipt, authority-order validation, context contract validation, schema/tool binding validation, validation gap reports

THIS FILE DOES NOT OWN:
- token budgeting, provider rendering, final signing, L2 execution validation, Exit/Runtimes Gates final output validation

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
- Detailed child file for PA.4 VALIDATE SLOT CONTRACT.
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
- "assembled slot contract validation only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. Validation Input
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- validation_id
- structured_slots_id
- security_pass_receipt_ref
- PromptBOM_ref
- PAAssemblyInput_ref
- slot_hashes{}
- policy_hash
- blueprint_hash
- replay_key
- provider_lane
- response_schema_contract_ref
- tool_schema_refs[]
- C0FinalEvidenceContract_ref if applicable
2. Slot Order Validation
------------------------------------------------------------------------------------------------------------------------
MUST CHECK:
- canonical slot order is preserved.
- S0 before D0 before I0 before E0 before C0 before M0 before U0 before H0.
- Y0 only included where policy permits and with promotion refs.
- R0 exists as a binding outside loose prose where possible.
- no slot is duplicated.
- no required slot is missing for the route class.
3. Authority Validation
------------------------------------------------------------------------------------------------------------------------
MUST CHECK:
- U0 cannot override S0/D0/I0.
- C0 cannot introduce instructions that override D0/I0.
- E0 cannot override R0 schema.
- H0 cannot widen repair scope.
- Y0 cannot override current policy or route.
- tool/schema definitions cannot be supplied by lower-authority text.
- all authority labels are present.
4. Context Contract Validation
------------------------------------------------------------------------------------------------------------------------
MUST CHECK WHEN GROUNDING REQUIRED:
- C0FinalEvidenceContract_ref exists.
- verified chunks are present unless C0 status allows abstain/gap output.
- citations are preserved.
- support gaps are preserved.
- contradiction flags are preserved.
- abstain recommendation is preserved if present.
- source lineage is not flattened.
- C0 status is not inflated by PA.
5. Tool and Schema Validation
------------------------------------------------------------------------------------------------------------------------
MUST CHECK:
- tools are bound through provider tools field or equivalent structured binding.
- R0 schema is bound through response_schema / response_format or equivalent structured binding.
- tool schema is not inline prose when provider-native field is available.
- response schema is not contradicted by examples or U0 task text.
- required output fields are present in schema binding.
- prohibited output fields are represented where required.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_SLOT_CONTRACT_VALID
- PA_SLOT_CONTRACT_INVALID
- PA_CONTEXT_CONTRACT_GAP
- PA_AUTHORITY_INVERSION_GAP
- PA_SCHEMA_BINDING_GAP
- PA_TOOL_BINDING_GAP

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- SlotValidationReceipt
- validation_gap_report
- authority_order_receipt
- context_contract_receipt
- tool_schema_binding_receipt
- validation_hash_receipt

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
- Wrong slot order fails validation.
- C0 evidence missing on grounded route fails context contract validation.
- Tool schema included as loose prose when provider tool field exists fails tool binding validation.
