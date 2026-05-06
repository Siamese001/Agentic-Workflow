PA.1 LOAD / RESOLVE PROMPT BOM, ZERO-LOSS OVERWRITE
Example ask:
"Find the current pet policy in Amit's lease and cite the exact clause."

CORE DISTINCTION
================

PA.0 proves Prompt Assembly is allowed to run.
PA.1 resolves the Prompt BOM.
PA.2 composes authority-tiered slots.
PA.3 airlocks untrusted payloads.
PA.7 signs the final provider-ready artifact.

PA.1 = stable component selection and hash map.

PA.1 asks:
"Which prompt components are selected?"

PA.1 does not retrieve evidence.
PA.1 does not route.
PA.1 does not compose final slots.
PA.1 does not neutralize payloads.
PA.1 does not validate final slot authority.
PA.1 does not trim token budget.
PA.1 does not render provider payload.
PA.1 does not call a provider.
PA.1 does not execute tools.
PA.1 does not sign the compiled artifact.
PA.1 does not write L4.


INPUTS INTO PA.1
================

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0 PAAssemblyInput                                                         │
│ ROLE: boundary-cleared assembly input                                         │
│                                                                              │
│ assembly_input_id = pa_0_pet_policy_assembly_input                           │
│ status = PA_READY                                                             │
│                                                                              │
│ upstream refs:                                                                │
│ - l1_plan_ref                                                                 │
│ - l0_route_ref                                                                │
│ - c0_final_evidence_contract_ref                                              │
│ - l5_governance_refs                                                          │
│ - agent_spec_ref                                                              │
│ - response_schema_ref                                                         │
│ - provider_lane_ref                                                           │
│ - model_settings_ref                                                          │
│ - tool_schema_refs optional                                                   │
│                                                                              │
│ binding refs:                                                                 │
│ - request_id                                                                  │
│ - run_id                                                                      │
│ - trace_id                                                                    │
│ - policy_hash                                                                 │
│ - blueprint_hash                                                              │
│ - route_digest                                                                │
│ - replay_key                                                                  │
│                                                                              │
│ PA.1 may resolve prompt components only from these approved refs.             │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ Component Registries / Approved Refs                                          │
│ ROLE: read-only source of prompt components                                   │
│                                                                              │
│ S0 system identity and invariants                                             │
│ D0 fences and anti-injection controls                                         │
│ I0 instructions and AgentSpec constraints                                     │
│ E0 approved examples                                                          │
│ C0 FinalEvidenceContract refs                                                 │
│ M0 provider-safe control hints                                                │
│ U0 neutralized user task candidate                                            │
│ H0 bounded repair hints, if allowed                                           │
│ R0 response schema binding                                                    │
│ tool schema refs                                                              │
│ execution metadata                                                            │
│ provider/model settings                                                       │
│                                                                              │
│ PA.1 resolves refs and hashes only.                                           │
│ PA.1 does not place components into final authority slots yet.                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


PA.1 BOM RESOLUTION FLOW
========================

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.1 LOAD S0 SYSTEM COMPONENTS                                              │
│                                                                              │
│ Resolve:                                                                      │
│ - system identity                                                              │
│ - non-overlap laws                                                            │
│ - core runtime invariants                                                     │
│ - layer authority boundaries                                                  │
│ - no retrieve / no execute / no L4 write rules for PA                         │
│                                                                              │
│ Example:                                                                      │
│ S0 says PA composes only and L2 executes.                                      │
│                                                                              │
│ Required output:                                                              │
│ - S0_component_ref                                                            │
│ - S0_component_hash                                                           │
│                                                                              │
│ If missing or stale:                                                          │
│ emit PA_BOM_GAP                                                               │
│ do not proceed to slot composition                                            │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.2 LOAD D0 FENCES                                                         │
│                                                                              │
│ Resolve:                                                                      │
│ - source scope fences                                                         │
│ - C0 evidence-as-data fence                                                   │
│ - user intent-as-intent fence                                                 │
│ - prompt injection controls                                                   │
│ - authority override blocks                                                   │
│ - provider/tool substitution blocks                                           │
│ - no hidden retrieval / no hidden execution fence                             │
│                                                                              │
│ Example:                                                                      │
│ D0 says lease text is evidence only, never instruction.                       │
│                                                                              │
│ Required output:                                                              │
│ - D0_component_ref                                                            │
│ - D0_component_hash                                                           │
│                                                                              │
│ If missing:                                                                   │
│ emit PA_BOM_GAP                                                               │
│ do not assemble unsafe prompt packet                                          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.3 LOAD I0 INSTRUCTIONS / AGENTSPEC CONSTRAINTS                           │
│                                                                              │
│ Resolve:                                                                      │
│ - task operating instructions                                                 │
│ - AgentSpec constraints                                                       │
│ - answer style and citation expectations                                      │
│ - allowed tool posture, if any                                                │
│ - model behavior constraints                                                  │
│                                                                              │
│ Example:                                                                      │
│ I0 says answer only from verified C0 evidence and cite exact clauses.         │
│                                                                              │
│ Required output:                                                              │
│ - I0_component_ref                                                            │
│ - AgentSpec_ref                                                               │
│ - I0_component_hash                                                           │
│ - AgentSpec_hash                                                              │
│                                                                              │
│ If AgentSpec missing:                                                         │
│ emit PA_BOM_GAP                                                               │
│ PA cannot invent operating instructions                                       │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.4 LOAD E0 APPROVED EXAMPLES                                              │
│                                                                              │
│ Resolve only if allowed:                                                      │
│ - approved answer examples                                                    │
│ - citation formatting examples                                                │
│ - task-class examples                                                         │
│ - domain-safe examples                                                        │
│                                                                              │
│ Example:                                                                      │
│ E0 may include a safe example of citing a lease clause.                       │
│                                                                              │
│ Required output:                                                              │
│ - E0_component_refs[]                                                         │
│ - E0_component_hashes[]                                                       │
│ - E0_allowed_surfaces[]                                                       │
│                                                                              │
│ Rules:                                                                        │
│ - E0 is optional unless route/spec requires examples                          │
│ - E0 cannot override S0/D0/I0/R0                                               │
│ - E0 must be approved, versioned, and hash-bound                              │
│                                                                              │
│ If optional examples missing:                                                 │
│ continue with E0 empty                                                        │
│                                                                              │
│ If required examples missing:                                                 │
│ emit PA_BOM_GAP                                                               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.5 LOAD C0 EVIDENCE CONTRACT REFS                                         │
│                                                                              │
│ Resolve from C0FinalEvidenceContract:                                         │
│ - MUST_USE refs                                                               │
│ - SUPPORTING refs                                                             │
│ - CONTRADICTIONS / QUALIFICATIONS refs                                        │
│ - BACKGROUND refs                                                             │
│ - EXCLUDED refs, as exclusion metadata only                                   │
│ - GAPS / caveats                                                              │
│ - citation anchors                                                            │
│ - source lineage refs                                                         │
│                                                                              │
│ Example:                                                                      │
│ MUST_USE:                                                                     │
│ - current lease clause 12.1 no-pets clause                                    │
│ - current lease clause 12.2 service-animal exception                          │
│                                                                              │
│ SUPPORTING:                                                                   │
│ - fee/deposit clause only if needed                                           │
│                                                                              │
│ Required output:                                                              │
│ - C0_contract_ref                                                             │
│ - C0_contract_hash                                                            │
│ - evidence_ref_map                                                            │
│ - citation_ref_map                                                            │
│ - lineage_ref_map                                                             │
│                                                                              │
│ Rules:                                                                        │
│ - PA.1 loads refs only                                                        │
│ - PA.1 does not fetch missing chunks                                          │
│ - PA.1 does not rewrite C0 status                                             │
│ - PA.1 does not convert excluded evidence into support                        │
│                                                                              │
│ If grounding_required = true and C0 refs missing:                             │
│ emit PA_BOM_GAP                                                               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.6 LOAD M0 PROVIDER-SAFE CONTROL HINTS                                    │
│                                                                              │
│ Resolve if configured:                                                        │
│ - provider-safe formatting controls                                           │
│ - reasoning-depth controls                                                    │
│ - no-chain-of-thought-disclosure controls                                     │
│ - evidence-use reminders                                                      │
│                                                                              │
│ Example:                                                                      │
│ M0 may say produce concise answer with citations, but do not expose hidden    │
│ reasoning.                                                                    │
│                                                                              │
│ Required output:                                                              │
│ - M0_component_refs[]                                                         │
│ - M0_component_hashes[]                                                       │
│                                                                              │
│ Rules:                                                                        │
│ - M0 cannot contain private chain-of-thought                                  │
│ - M0 cannot override S0/D0/I0/R0                                               │
│ - M0 is optional unless required by route/provider policy                     │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.7 LOAD U0 USER TASK INTENT CANDIDATE                                     │
│                                                                              │
│ Resolve:                                                                      │
│ - normalized user task ref                                                    │
│ - user intent text                                                            │
│ - user constraints                                                            │
│ - requested output form                                                       │
│                                                                              │
│ Example:                                                                      │
│ U0 candidate = "Find the current pet policy in Amit's lease and cite clause." │
│                                                                              │
│ Required output:                                                              │
│ - U0_task_ref                                                                 │
│ - U0_task_hash                                                                │
│                                                                              │
│ Rules:                                                                        │
│ - U0 is user intent only                                                      │
│ - PA.1 does not yet airlock or neutralize payloads                            │
│ - PA.3 performs airlock/security pass later                                   │
│ - U0 cannot become system/developer/policy instruction                        │
│                                                                              │
│ If U0 task ref missing:                                                       │
│ emit PA_BOM_GAP or PA_INPUT_INCOMPLETE                                        │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.8 LOAD H0 BOUNDED REPAIR HINTS, IF ALLOWED                               │
│                                                                              │
│ Resolve only if route/spec allows:                                            │
│ - same-policy repair hints                                                    │
│ - response repair constraints                                                 │
│ - output schema repair hints                                                  │
│ - citation repair hints                                                       │
│                                                                              │
│ Example:                                                                      │
│ H0 may say if evidence has a qualification, include it.                       │
│                                                                              │
│ Required output:                                                              │
│ - H0_component_refs[]                                                         │
│ - H0_component_hashes[]                                                       │
│                                                                              │
│ Rules:                                                                        │
│ - H0 is bounded repair hint only                                              │
│ - H0 cannot add new facts                                                     │
│ - H0 cannot widen route scope                                                 │
│ - H0 cannot substitute provider/tool/model                                    │
│ - H0 can be empty if no repair hint is allowed                                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.9 LOAD R0 RESPONSE SCHEMA                                                │
│                                                                              │
│ Resolve:                                                                      │
│ - response schema ref                                                         │
│ - schema version                                                              │
│ - schema hash                                                                 │
│ - provider-native schema compatibility                                        │
│                                                                              │
│ Example fields if structured output required:                                 │
│ - answer_text                                                                 │
│ - citation_refs                                                               │
│ - caveats                                                                     │
│ - evidence_status                                                             │
│                                                                              │
│ Required output:                                                              │
│ - R0_schema_ref                                                               │
│ - R0_schema_hash                                                              │
│ - R0_provider_binding_hint                                                    │
│                                                                              │
│ Rules:                                                                        │
│ - R0 is schema binding, not loose prose when native schema exists             │
│ - R0 cannot be overridden by E0, C0, U0, or H0                                 │
│ - if structured output required and R0 missing, PA.1 stops                    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1.10 LOAD TOOL SCHEMAS / EXECUTION METADATA                                │
│                                                                              │
│ Resolve if tools are allowed:                                                 │
│ - tool schema refs                                                            │
│ - tool registry hashes                                                        │
│ - allowed tool names                                                          │
│ - tool argument schema refs                                                   │
│ - capability/sandbox refs if already bound upstream                           │
│                                                                              │
│ Resolve execution metadata:                                                   │
│ - provider lane                                                               │
│ - model settings                                                              │
│ - replay key                                                                  │
│ - route digest                                                                │
│ - policy_hash / blueprint_hash                                                │
│                                                                              │
│ Rules:                                                                        │
│ - tool schemas are structured bindings, not loose prose                       │
│ - PA.1 does not execute tools                                                 │
│ - PA.1 does not approve tool execution                                        │
│ - PA.1 does not select unregistered tools                                     │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


PROMPT BOM OUTPUT
=================

┌──────────────────────────────────────────────────────────────────────────────┐
│ PromptBOM                                                                    │
│                                                                              │
│ prompt_bom_id = pa_1_pet_policy_prompt_bom                                   │
│ assembly_input_ref = pa_0_pet_policy_assembly_input                          │
│ status = PA_BOM_RESOLVED                                                     │
│                                                                              │
│ component refs:                                                               │
│                                                                              │
│ S0:                                                                           │
│ - S0_component_ref                                                            │
│ - S0_component_hash                                                           │
│                                                                              │
│ D0:                                                                           │
│ - D0_component_ref                                                            │
│ - D0_component_hash                                                           │
│                                                                              │
│ I0:                                                                           │
│ - I0_component_ref                                                            │
│ - I0_component_hash                                                           │
│ - AgentSpec_ref                                                               │
│ - AgentSpec_hash                                                              │
│                                                                              │
│ E0:                                                                           │
│ - E0_component_refs[]                                                         │
│ - E0_component_hashes[]                                                       │
│ - optional unless required                                                    │
│                                                                              │
│ C0:                                                                           │
│ - C0FinalEvidenceContract_ref                                                 │
│ - C0FinalEvidenceContract_hash                                                │
│ - evidence_ref_map                                                            │
│ - citation_ref_map                                                            │
│ - lineage_ref_map                                                             │
│ - gaps_and_caveats_ref                                                        │
│                                                                              │
│ M0:                                                                           │
│ - M0_component_refs[]                                                         │
│ - M0_component_hashes[]                                                       │
│ - no chain-of-thought disclosure                                              │
│                                                                              │
│ U0:                                                                           │
│ - U0_task_ref                                                                 │
│ - U0_task_hash                                                                │
│                                                                              │
│ H0:                                                                           │
│ - H0_component_refs[]                                                         │
│ - H0_component_hashes[]                                                       │
│ - optional / bounded only                                                     │
│                                                                              │
│ R0:                                                                           │
│ - response_schema_ref                                                         │
│ - response_schema_hash                                                        │
│ - provider_native_binding_hint                                                │
│                                                                              │
│ Tools / execution metadata:                                                   │
│ - tool_schema_refs[]                                                          │
│ - tool_schema_hashes[]                                                        │
│ - provider_lane_ref                                                           │
│ - model_settings_ref                                                          │
│ - route_digest                                                                │
│ - replay_key                                                                  │
│ - policy_hash                                                                 │
│ - blueprint_hash                                                              │
│                                                                              │
│ component_hash_map:                                                           │
│ - stable hash for every component                                             │
│                                                                              │
│ missing_component_report:                                                     │
│ - empty if PA_BOM_RESOLVED                                                    │
│ - populated if any required component is missing/stale/mismatched             │
│                                                                              │
│ NEXT: PA.2 composes authority-tiered slots                                    │
│ PA.1 DOES NOT COMPOSE SLOTS, AIRLOCK PAYLOADS, VALIDATE SLOT CONTRACT,        │
│ TOKEN-TRIM, RENDER PROVIDER PAYLOAD, SIGN ARTIFACT, EXECUTE, OR WRITE L4      │
└──────────────────────────────────────────────────────────────────────────────┘


STOP AS BOM GAP
===============

┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 1: Missing S0 / D0 / I0                                             │
│                                                                              │
│ Problem:                                                                      │
│ required authority or fence components missing                                │
│                                                                              │
│ PA.1 result:                                                                  │
│ status = PA_BOM_GAP                                                           │
│ gap = missing required high-authority prompt components                       │
│                                                                              │
│ Rule: PA cannot assemble without system/fence/instruction refs.               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 2: Missing C0 evidence contract on grounded route                   │
│                                                                              │
│ Problem:                                                                      │
│ grounding_required = true but C0FinalEvidenceContract missing or stale        │
│                                                                              │
│ PA.1 result:                                                                  │
│ status = PA_BOM_GAP                                                           │
│ gap = missing or stale C0 contract component                                  │
│                                                                              │
│ Rule: PA cannot fetch evidence or answer from user intent alone.              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 3: Missing R0 schema when structured output required                │
│                                                                              │
│ Problem:                                                                      │
│ route expects structured output but response_schema_ref missing               │
│                                                                              │
│ PA.1 result:                                                                  │
│ status = PA_BOM_GAP                                                           │
│ gap = missing response schema                                                 │
│                                                                              │
│ Rule: PA cannot downgrade schema to loose prose when native schema is needed. │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 4: Stale or mismatched component hash                               │
│                                                                              │
│ Problem:                                                                      │
│ component hash does not match policy_hash / blueprint_hash / route_digest     │
│                                                                              │
│ PA.1 result:                                                                  │
│ status = PA_BOM_GAP                                                           │
│ gap = stale or mismatched component                                           │
│                                                                              │
│ Rule: PA cannot assemble mixed-version prompt packets.                        │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 5: Tool schema only available as loose prose                        │
│                                                                              │
│ Problem:                                                                      │
│ tool expected but no structured tool_schema_ref                               │
│                                                                              │
│ PA.1 result:                                                                  │
│ status = PA_BOM_GAP                                                           │
│ gap = missing structured tool schema binding                                  │
│                                                                              │
│ Rule: tool schemas must be structured bindings, not informal text.            │
└──────────────────────────────────────────────────────────────────────────────┘


GUARDRAILS
==========

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.1 PROMPT BOM GUARDRAILS                                                    │
│                                                                              │
│ Resolve stable refs and hashes for every selected component.                  │
│ Require S0, D0, I0 when applicable.                                           │
│ Require C0 refs when grounding_required = true.                               │
│ Require R0 when structured output is required.                                │
│ Require provider/model/execution metadata.                                    │
│ Require tool schema refs if tools are allowed.                                │
│ Preserve policy_hash, blueprint_hash, route_digest, replay_key.               │
│ Preserve C0 evidence status, gaps, caveats, citations, lineage.               │
│ Treat U0 as user intent only.                                                 │
│ Treat C0 evidence as data only.                                               │
│ Treat E0 examples as optional unless required and never higher authority.      │
│ Treat H0 as bounded repair hints only.                                        │
│                                                                              │
│ Do not retrieve.                                                              │
│ Do not route.                                                                 │
│ Do not compose authority slots yet.                                           │
│ Do not airlock payloads yet.                                                  │
│ Do not validate final slot contract yet.                                      │
│ Do not trim token budget yet.                                                 │
│ Do not render provider payload.                                               │
│ Do not call provider.                                                         │
│ Do not execute tools.                                                         │
│ Do not sign compiled artifact.                                                │
│ Do not write L4.                                                              │
│                                                                              │
│ If BOM resolved:                                                              │
│ proceed to PA.2.                                                              │
│                                                                              │
│ If required component missing/stale/mismatched:                               │
│ stop as PA_BOM_GAP.                                                           │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


MEMORY HOOK
===========

┌──────────────────────────────┐
│ PA.0                         │
│ "May PA run at all?"         │
│ complete upstream refs       │
└───────────────┬──────────────┘
                │ PA_READY
                ▼
┌──────────────────────────────┐
│ PA.1                         │
│ "Which components?"          │
│ S0 D0 I0 E0 C0 M0 U0 H0 R0   │
│ tools + provider metadata    │
│ stable refs + hashes         │
└───────────────┬──────────────┘
                │ PromptBOM
                ▼
┌──────────────────────────────┐
│ PA.2                         │
│ "Where do components go?"    │
│ authority-tiered slots       │
└──────────────────────────────┘