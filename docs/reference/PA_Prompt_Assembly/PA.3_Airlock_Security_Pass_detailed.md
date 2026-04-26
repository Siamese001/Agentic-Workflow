========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: PA_Prompt_Assembly
Canonical file: PA.3_Airlock_Security_Pass_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: PA.3_Airlock_Security_Pass_detailed.md
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
CHILD FILE PA.3 AIRLOCK / SECURITY PASS
PA.3_Airlock_Security_Pass_detailed.md
========================================================================================================================

========================================================================================================================
OVERWRITE RECONCILIATION HEADER
Canonical filename: PA.3_Airlock_Security_Pass_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade child contract
Parent: Prompt_Assembly_detailed.md
========================================================================================================================

UNIQUE OWNERSHIP SURFACE:
- assembly-time airlock and slot payload security pass only

THIS FILE OWNS:
- U0 airlock receipts, C0 payload classifier receipts, H0 re-entry validation receipts, safe slot payload map, rejected payload reports

THIS FILE DOES NOT OWN:
- L5 origin-trust doctrine, C0 retrieval/scoring, Runtime Gate security decisions, L2 execution validation, Exit final safety decision

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
- Detailed child file for PA.3 AIRLOCK / SECURITY PASS.
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
- "assembly-time airlock and slot payload security pass only?"

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
- This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface.
- This file must not fetch missing data.
- This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state.
- This file must not approve L2 execution. It only prepares evidence for L2 validation.

1. Security Pass Input
------------------------------------------------------------------------------------------------------------------------
FIELDS:
- security_pass_id
- structured_slots_id
- origin_trust_manifest_ref if available
- slot_origin_map
- slot_authority_map
- slot_payload_hashes
- policy_hash
- blueprint_hash
- route_id
- task_class
- data_class
- provider_lane
- security_profile_ref

MUST CHECK:
- every slot has origin label.
- every lower-authority content item has data/intent/proposal label.
- every C0 payload has source lineage and citation/gap labels.
- every H0 payload has repair scope and same-run hash refs.
- every tool/schema payload is separated from prose content.
- no slot contains unreviewed instruction-like text from untrusted content.
2. U0 Airlock
------------------------------------------------------------------------------------------------------------------------
PURPOSE:
- Preserve actual user task while neutralizing illegal control claims.

CHECKS:
- role override language.
- policy override language.
- system/developer instruction override attempts.
- tool/provider/credential authority claims.
- durable write claims.
- hidden target/action ambiguity.
- malicious delimiter or instruction smuggling.

OUTPUTS:
- neutralized_user_task.
- u0_airlock_receipt.
- stripped_control_claims[].
- preserved_task_intent_summary.
- u0_security_notes[].
3. C0 Retrieved-Content Classifier
------------------------------------------------------------------------------------------------------------------------
PURPOSE:
- Ensure retrieved chunks enter as evidence, not instructions.

CHECKS:
- instruction-like payloads in retrieved text.
- coercive UI text.
- embedded jailbreak text.
- credential exfiltration language.
- tool-call imitation.
- fake policy text presented as live system authority.
- stale or contradicted evidence flags from C0.

OUTPUTS:
- c0_payload_security_receipt.
- safe_c0_payload_map.
- rejected_c0_payload_report.
- safe_extraction_receipts[].
- citation_preservation_receipt.
4. H0 Healer Re-entry Validation
------------------------------------------------------------------------------------------------------------------------
CHECKS:
- same policy_hash.
- same blueprint_hash.
- same route/step scope.
- no provider/tool/model substitution.
- no scope widening.
- no new facts without C0 support.
- no bypass of L5/UWG/Exit.

OUTPUTS:
- h0_reentry_validation_receipt.
- h0_allowed_payload_map.
- h0_rejected_payload_report.
5. Tool / Schema Text Safety
------------------------------------------------------------------------------------------------------------------------
CHECKS:
- tool definitions are structured bindings, not untrusted text.
- schema definitions are structured bindings, not loose prose.
- user/retrieved text cannot define tools or schema fields.
- provider-specific tool/schema fields are not polluted by U0/C0 content.


STATUS VALUES
------------------------------------------------------------------------------------------------------------------------
- PA_SECURITY_PASS
- PA_SECURITY_GAP
- PA_SAFE_EXTRACTION_PARTIAL
- PA_SLOT_PAYLOAD_REJECTED
- PA_REQUIRES_UPSTREAM_REPAIR

MUST EMIT
------------------------------------------------------------------------------------------------------------------------
- AssemblySecurityPassReceipt
- safe_slot_payload_map
- rejected_slot_payload_report
- prompt_like_payload_report
- safe_extraction_map
- security_gap_report

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
- U0 injection attempt is neutralized without losing legitimate task intent.
- Retrieved text containing ignore prior instructions remains data or is rejected from C0 slot.
- H0 repair hint trying to change provider or tool is rejected.
