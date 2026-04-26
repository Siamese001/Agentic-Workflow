========================================================================================================================
CHILD FILE PA.6 PROVIDER-AWARE RENDERING
PA.6_Provider_Aware_Rendering_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.6_Provider_Aware_Rendering_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- provider-specific rendering of canonical slots only

THIS FILE OWNS:
- ProviderRenderRequest, ProviderRenderManifest, provider adapter mappings, provider field placement, render gap reports

THIS FILE DOES NOT OWN:
- provider invocation, L5 egress certification, model/tool execution, final artifact signing, output approval

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
- Detailed child file for PA.6 PROVIDER-AWARE RENDERING.
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
- "provider-specific rendering of canonical slots only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. Provider Render Request
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- render_request_id
- TokenBudgetLedger_ref
- canonical_hash_input_manifest_ref
- structured_slots_ref
- provider_lane
- symbolic_model_id
- resolved_model_id if known
- provider_capabilities_ref
- tool_binding_refs[]
- response_schema_binding_ref
- policy_hash
- replay_key
2. Provider Render Manifest
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- render_manifest_id
- provider_lane
- adapter_version
- canonical_slot_hashes{}
- rendered_message_refs[]
- system_field_ref if applicable
- developer_field_ref if applicable
- user_field_ref if applicable
- document_container_refs[] if applicable
- tools_field_ref if applicable
- response_schema_field_ref if applicable
- thinking_control_ref if applicable
- render_warnings[]
- unsupported_feature_reports[]
- render_hash
3. Anthropic Lane
------------------------------------------------------------------------------------------------------------------------
MAPPING EXPECTATIONS:
- system field carries high-authority instructions.
- document containers may carry context/evidence where supported.
- long-context ordering may hoist data and tail-repeat bounded task reminder when adapter policy allows.
- tool definitions use provider-native tool structure.
- schema requirements use available structured-output/tool patterns where supported.
- hidden reasoning guidance is not exposed as chain-of-thought request.
4. OpenAI GPT Lane
------------------------------------------------------------------------------------------------------------------------
MAPPING EXPECTATIONS:
- system/developer/user roles are used according to provider rules.
- headings may separate Role, Instructions, Context, Examples, Final Instructions.
- tool schemas ride API tools field.
- response schema rides response_format / structured output field where available.
- C0 is not placed in a higher-authority instruction slot.
5. OpenAI Reasoning Lane
------------------------------------------------------------------------------------------------------------------------
MAPPING EXPECTATIONS:
- thinking controls ride provider-native reasoning metadata where supported.
- do not ask the model to reveal chain-of-thought.
- preserve concise answer discipline and private control hints in safe form.
- reasoning effort / temperature metadata matches RouteContract.
6. Gemini Lane
------------------------------------------------------------------------------------------------------------------------
MAPPING EXPECTATIONS:
- data-first or instruction-after-data patterns may be used for long context if adapter policy requires it.
- structured outputs ride response_schema field where available.
- authority labels must remain clear when provider roles differ.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_RENDERED
- PA_RENDER_GAP
- PA_PROVIDER_FEATURE_GAP
- PA_SCHEMA_RENDER_GAP
- PA_TOOL_RENDER_GAP

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- ProviderRenderManifest
- rendered_prompt_packet
- provider_field_mapping_receipt
- provider_feature_gap_report
- schema_render_receipt
- tool_render_receipt

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
- Same canonical slots render differently per provider but preserve same canonical hash input manifest.
- C0 evidence is never rendered as system/developer instruction.
- Unsupported provider feature emits PA_PROVIDER_FEATURE_GAP.
