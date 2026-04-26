========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: PA_Prompt_Assembly
Canonical file: PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md
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
CHILD FILE PA.7 FINAL EMIT / COMPILED PROMPT ARTIFACT
PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- final signed prompt artifact emission only

THIS FILE OWNS:
- CompiledPromptArtifact, manifest_hash, HMAC signature, artifact receipt, L2 handoff envelope

THIS FILE DOES NOT OWN:
- provider dispatch, model/tool execution, output approval, durable writes, completed-run learning

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
- Detailed child file for PA.7 FINAL EMIT / COMPILED PROMPT ARTIFACT.
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
- "final signed prompt artifact emission only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. CompiledPromptArtifact Schema
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- compiled_prompt_artifact_id
- assembly_request_id
- prompt_bom_id
- structured_slots_id
- render_manifest_id
- request_id / run_id / trace_id / route_id / plan_id
- step_id if workflow step
- provider_lane
- symbolic_model_id
- resolved_model_id if known
- model_settings.temperature
- model_settings.thinking_level
- model_settings.max_output_tokens
- model_settings.tool_choice if applicable
- final_provider_payload_ref
- structured_slots_used[]
- allowed_tools_schema_ref via provider tools field
- response_schema_ref via provider response_schema / response_format field
- C0FinalEvidenceContract_ref if grounded
- source_lineage_refs[]
- security_pass_receipt_ref
- slot_validation_receipt_ref
- token_budget_ledger_ref
- deterministic_trimming_receipt_ref if trimming occurred
- provider_render_manifest_ref
- policy_hash
- blueprint_hash
- route_digest
- replay_key
- canonical_hash_input_manifest_ref
- manifest_hash
- hmac_sig
- idempotency_nonce
- created_at_run_clock_offset
- artifact_status
2. Manifest Hash
------------------------------------------------------------------------------------------------------------------------
MUST INCLUDE:
- canonical structured slot bytes after PA.5 trimming.
- provider lane and render-affecting metadata.
- schema binding refs.
- tool binding refs.
- policy_hash.
- blueprint_hash.
- route_digest.
- replay_key when required.
- C0 evidence contract ref when grounded.
- security/validation receipt refs.

MUST EXCLUDE:
- idempotency nonce when designated non-deterministic by PA.5.
- wall-clock created_at unless normalized as run-clock offset.
- provider runtime response IDs.
- L2 execution receipts not yet created.
3. HMAC Signature
------------------------------------------------------------------------------------------------------------------------
MUST CHECK:
- signing secret / key ref is available through approved signing mechanism.
- manifest_hash exists.
- required metadata is included.
- signature algorithm is declared.
- signature is reproducible for same canonical inputs and same signing key.
- artifact cannot be mutated without invalidating signature.

FIELDS:
- signature_algorithm = HMAC-SHA256 or approved equivalent.
- signing_key_ref.
- signed_fields[].
- hmac_sig.
- signature_receipt.
4. L2 Handoff Envelope
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- l2_handoff_envelope_id
- compiled_prompt_artifact_ref
- route_id
- execution_form
- provider_lane
- model_settings_ref
- tool_schema_refs[]
- response_schema_ref
- capability_token_ref if already bound upstream
- sandbox_envelope_ref if already bound upstream
- policy_hash
- blueprint_hash
- replay_key
- prompt_hash / manifest_hash
- hmac_sig
- handoff_notes[]

MUST NOT INCLUDE:
- direct provider client handle.
- raw secret material.
- authority invented by user/retrieved/tool/model/human text.
- durable write command.
- final output disposition.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_ARTIFACT_SIGNED
- PA_ARTIFACT_NOT_SIGNED
- PA_SIGNATURE_GAP
- PA_MANIFEST_HASH_GAP
- PA_L2_HANDOFF_READY
- PA_L2_HANDOFF_GAP

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- CompiledPromptArtifact
- compiled_prompt_artifact_receipt
- manifest_hash_receipt
- hmac_signature_receipt
- l2_handoff_envelope
- final_artifact_gap_report

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
- Same canonical inputs and signing key produce same manifest_hash and HMAC.
- Changing C0 evidence ref changes manifest_hash.
- Changing idempotency nonce alone does not change manifest_hash when excluded by PA.5.
- Unsigned artifact cannot be marked PA_L2_HANDOFF_READY.
- L2 handoff envelope contains no provider client handle or raw secret.
