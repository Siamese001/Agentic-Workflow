========================================================================================================================
CHILD FILE PA.2 SLOT COMPOSITION
PA.2_Slot_Composition_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.2_Slot_Composition_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- canonical authority-tiered slot construction only

THIS FILE OWNS:
- StructuredPromptSlots, canonical slot order, slot authority map, slot lineage map, slot conflict map

THIS FILE DOES NOT OWN:
- BOM resolution, security pass, validation, token budgeting, provider rendering, final signing, execution

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
- Detailed child file for PA.2 SLOT COMPOSITION.
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
- "canonical authority-tiered slot construction only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. StructuredPromptSlots
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- structured_slots_id
- prompt_bom_id
- slot_order[]
- S0_slot
- D0_slot
- I0_slot
- E0_slot
- C0_slot
- M0_slot
- U0_slot
- Y0_slot optional
- H0_slot optional
- R0_binding
- tool_bindings[]
- slot_authority_map
- slot_origin_map
- slot_lineage_map
- slot_hashes{}
- slot_conflict_map
- slot_omission_reasons{}
- structured_slots_hash

REQUIRED ORDER:
S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0
R0 is bound as schema, not loose prose where provider-native schema fields exist.
2. Slot Payload Requirements
------------------------------------------------------------------------------------------------------------------------
S0:
- system identity and invariant refs, system_version_hash, immutable authority label.

D0:
- role fences, scope limits, anti-injection controls, allowed/disallowed posture refs.

I0:
- task operating instructions, AgentSpec capability refs, procedure constraints.

E0:
- approved examples, style/format guidance, exemplar origin refs, conflict screening refs.

C0:
- verified evidence, citations, source lineage, support limits, contradictions, gaps, abstain recommendation metadata if present.

M0:
- private provider-safe control hints, reasoning discipline metadata, no chain-of-thought disclosure instructions.

U0:
- neutralized task intent candidate, user constraints, requested output, no policy authority.

Y0:
- approved prior patterns only if current policy permits, with promotion receipt refs.

H0:
- bounded repair hint only, same policy_hash / blueprint_hash requirement for same-run repair.

R0:
- schema binding object, provider-native response_schema / response_format target, not freeform prose where structured output exists.
3. Authority Composition Rules
------------------------------------------------------------------------------------------------------------------------
MUST CHECK:
- no lower-authority slot modifies higher-authority slot fields.
- no C0 text becomes instruction.
- no U0 text becomes policy.
- no E0 exemplar overrides schema or safety posture.
- no H0 hint changes route, provider, tool, scope, policy, or blueprint.
- no Y0 prior appears without promotion/evidence refs.
- R0 schema is not contradicted by examples or task prose.
- tool binding is not redefined by user or retrieved text.

SLOT CONFLICT TYPES:
- lower_authority_override_attempt
- c0_instruction_like_payload
- u0_policy_override_attempt
- exemplar_schema_conflict
- h0_scope_widening_attempt
- y0_missing_promotion_receipt
- r0_schema_conflict
- tool_binding_conflict
- slot_order_violation
- missing_origin_label


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_SLOTS_COMPOSED
- PA_SLOT_COMPOSITION_GAP
- PA_AUTHORITY_CONFLICT

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- StructuredPromptSlots
- slot_composition_receipt
- slot_authority_map
- slot_lineage_map
- slot_conflict_map
- structured_slots_hash_receipt

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
- User text saying ignore system remains in U0 and cannot alter S0/D0/I0.
- Retrieved chunk containing instructions remains C0 data and is flagged for PA.3 security handling.
- Same BOM produces same structured_slots_hash.
