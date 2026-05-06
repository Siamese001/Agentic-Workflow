PA.0 BOUNDARY CHECK, ZERO-LOSS OVERWRITE
Example ask:
"Find the current pet policy in Amit's lease and cite the exact clause."

CORE DISTINCTION
================

C0 produced the evidence contract.
PA packages verified upstream material into a prompt artifact.
PA.0 checks whether Prompt Assembly is allowed to run at all.

PA.0 = boundary check / assembly eligibility.
PA.1 = Prompt BOM resolution.
PA.2 = authority slot composition.
PA.7 = signed CompiledPromptArtifact for L2.

PA.0 asks:
"Is Prompt Assembly allowed to run with complete upstream refs?"

PA.0 does not retrieve evidence.
PA.0 does not route.
PA.0 does not execute.
PA.0 does not call a provider.
PA.0 does not assemble prompt slots.
PA.0 does not sign the artifact.
PA.0 does not approve L2 execution.
PA.0 does not approve final output.
PA.0 does not write L4.


INPUTS INTO PA.0
================

┌──────────────────────────────────────────────────────────────────────────────┐
│ L1 PlanContract                                                              │
│ ROLE: semantic task and user intent reference                                 │
│                                                                              │
│ task_spec = answer lease pet-policy question                                  │
│ query_spec = current lease pet-policy clause                                  │
│ user intent = find and cite exact clause                                      │
│ output_target = answer with citation                                          │
│ assumptions / ambiguity = current lease must be used                          │
│                                                                              │
│ PA.0 checks L1 exists.                                                        │
│ PA.0 does not treat L1 as authority to retrieve, route, or execute.           │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ L0 RouteContract                                                             │
│ ROLE: authoritative route and execution boundary                              │
│                                                                              │
│ route_id = R3_SIMPLE_GROUNDED_READ                                            │
│ grounding_required = true                                                     │
│ execution_form = SINGLE_STEP                                                  │
│ provider_lane = model execution expected                                      │
│ source_scope = lease_docs only                                                │
│ policy_hash = bound                                                           │
│ blueprint_hash = bound                                                        │
│ route_digest = bound                                                          │
│ replay_key = bound                                                            │
│                                                                              │
│ PA.0 checks L0 exists and route expects PA.                                   │
│ PA.0 does not change the route.                                               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ C0 FinalEvidenceContract, required because grounding_required = true          │
│ ROLE: verified evidence refs only                                             │
│                                                                              │
│ evidence_status = PASS                                                        │
│ support_target = POLICY_CLAUSE / EXACT_QUOTE                                  │
│ MUST_USE = current lease pet-policy clauses                                   │
│ SUPPORTING = optional fee/deposit clause                                      │
│ CONTRADICTIONS / QUALIFICATIONS = service-animal exception preserved          │
│ GAPS = none for base pet-policy clause                                        │
│ citation anchors = present                                                    │
│ source lineage = present                                                      │
│                                                                              │
│ PA.0 checks C0 contract exists when grounding is required.                    │
│ PA.0 does not fetch missing evidence.                                         │
│ PA.0 does not inflate C0 status.                                              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ L5 Governance Refs                                                           │
│ ROLE: policy, origin, authority, replay, and boundary evidence refs           │
│                                                                              │
│ policy_hash                                                                  │
│ blueprint_hash                                                               │
│ origin_trust_manifest_ref                                                     │
│ authority_context_ref                                                         │
│ registry_digest_set                                                           │
│ egress posture refs if applicable                                             │
│                                                                              │
│ PA.0 checks governance refs are bound.                                        │
│ PA.0 does not certify L5 evidence itself.                                     │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ AgentSpec / Provider / Schema Inputs                                         │
│ ROLE: prompt assembly dependencies                                            │
│                                                                              │
│ AgentSpec = allowed operating constraints                                     │
│ response_schema = required if structured output required                      │
│ provider_lane = Anthropic / OpenAI / Gemini / configured lane                 │
│ model_settings = symbolic model / temperature / reasoning controls            │
│ tool_schema_refs = present if tools are allowed                               │
│ replay_key = bound                                                            │
│                                                                              │
│ PA.0 checks required inputs exist.                                            │
│ PA.0 does not render provider payload yet.                                    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


PA.0 BOUNDARY FLOW
==================

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.1 CHECK PA IS EXPECTED FOR THIS ROUTE                                    │
│                                                                              │
│ Required:                                                                     │
│ - L0 RouteContract exists                                                     │
│ - route expects model/prompt execution                                        │
│ - route is not terminal cache/fallback that bypasses PA                       │
│                                                                              │
│ Example pass:                                                                 │
│ route_id = R3_SIMPLE_GROUNDED_READ                                            │
│ execution_form = SINGLE_STEP                                                  │
│ provider lane expected                                                        │
│                                                                              │
│ If route is terminal [RET]:                                                   │
│ PA.0 blocks.                                                                  │
│ No prompt assembly is needed.                                                 │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.2 CHECK L1 PLAN EXISTS                                                   │
│                                                                              │
│ Required:                                                                     │
│ - L1PlanContract ref is present                                               │
│ - task_spec exists                                                            │
│ - user intent has been normalized                                             │
│ - ambiguity/gap fields are carried forward                                    │
│                                                                              │
│ Example pass:                                                                 │
│ L1 says task is to answer lease pet-policy question with exact citation       │
│                                                                              │
│ If missing:                                                                   │
│ PA.0 emits PA_INPUT_INCOMPLETE.                                               │
│ PA cannot invent the task spec.                                               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.3 CHECK L0 ROUTE EXISTS                                                  │
│                                                                              │
│ Required:                                                                     │
│ - RouteContract ref is present                                                │
│ - route_digest is bound                                                       │
│ - provider/model expectation is clear                                         │
│ - policy_hash / blueprint_hash / replay_key are present                       │
│                                                                              │
│ Example pass:                                                                 │
│ L0 selected grounded-read route with bound route digest                       │
│                                                                              │
│ If missing:                                                                   │
│ PA.0 emits PA_BOUNDARY_MISMATCH or PA_INPUT_INCOMPLETE.                       │
│ PA cannot route for itself.                                                   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.4 CHECK C0 CONTRACT WHEN GROUNDING IS REQUIRED                           │
│                                                                              │
│ Required when grounding_required = true:                                      │
│ - C0 FinalEvidenceContract ref exists                                         │
│ - evidence_status is present                                                  │
│ - must_use/supporting/contradictions/gaps are preserved                       │
│ - citation refs and lineage refs exist                                        │
│                                                                              │
│ Example pass:                                                                 │
│ C0FinalEvidenceContract exists with current lease clauses and citation refs   │
│                                                                              │
│ If missing:                                                                   │
│ PA.0 stops as PA gap.                                                         │
│ PA cannot retrieve missing evidence.                                          │
│ PA cannot answer from user intent alone.                                      │
│ PA cannot treat C0 as optional on grounded routes.                            │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.5 CHECK PROVIDER LANE / MODEL SETTINGS                                   │
│                                                                              │
│ Required when model execution is expected:                                    │
│ - provider_lane exists                                                        │
│ - symbolic model or resolved model ref exists                                 │
│ - model settings are bound by route/registry                                  │
│ - no unapproved provider/model substitution                                   │
│                                                                              │
│ Example pass:                                                                 │
│ provider_lane = configured LLM lane                                            │
│ model settings = bound                                                        │
│                                                                              │
│ If missing or mismatched:                                                     │
│ PA.0 emits PA_RENDER_GAP or PA_BOUNDARY_MISMATCH.                             │
│ PA cannot choose an ad hoc provider.                                          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.6 CHECK RESPONSE SCHEMA REQUIREMENT                                      │
│                                                                              │
│ Required when structured output is expected:                                  │
│ - response_schema ref exists                                                  │
│ - schema version/hash is bound                                                │
│ - schema is compatible with route/provider                                    │
│                                                                              │
│ Example:                                                                      │
│ If answer must include citation fields, response schema must be available.    │
│                                                                              │
│ If missing:                                                                   │
│ PA.0 emits PA_INPUT_INCOMPLETE or PA_BOM_GAP.                                 │
│ PA cannot put schema only in loose prose when native schema binding is needed.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.7 CHECK POLICY / REPLAY / ROUTE DIGEST BINDINGS                          │
│                                                                              │
│ Required:                                                                     │
│ - policy_hash present                                                         │
│ - blueprint_hash present                                                      │
│ - route_digest present                                                        │
│ - replay_key present                                                          │
│ - upstream refs are from same request/run/trace                               │
│                                                                              │
│ Example pass:                                                                 │
│ L1, L0, C0, L5 refs all bind to same request/run/trace                        │
│                                                                              │
│ If mismatch:                                                                  │
│ PA.0 emits PA_BOUNDARY_MISMATCH.                                              │
│ PA cannot assemble across mixed runs or stale contracts.                      │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.8 CHECK PA IS NOT BEING ASKED TO CROSS ITS BOUNDARY                      │
│                                                                              │
│ PA.0 rejects requests asking PA to:                                           │
│ - retrieve evidence                                                           │
│ - route or reroute                                                            │
│ - call provider                                                               │
│ - execute tool                                                                │
│ - approve final answer                                                        │
│ - approve L2 execution                                                        │
│ - mutate L4                                                                   │
│ - bypass C0 on grounded route                                                 │
│ - treat user/retrieved/human/tool text as authority                           │
│                                                                              │
│ Example pass:                                                                 │
│ PA is asked only to assemble from complete upstream refs.                     │
│                                                                              │
│ If boundary violation:                                                        │
│ PA.0 emits assembly_gap_report.                                               │
│ No prompt artifact is created.                                                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


PA.0 DECISION
=============

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0.9 EMIT PA BOUNDARY STATUS                                                │
│                                                                              │
│ PA_READY                                                                      │
│ - all required upstream refs are complete                                     │
│ - PA may proceed to PA.1 Prompt BOM                                           │
│                                                                              │
│ PA_INPUT_INCOMPLETE                                                           │
│ - required upstream input missing                                             │
│ - stop as PA gap                                                              │
│                                                                              │
│ PA_BOUNDARY_MISMATCH                                                          │
│ - refs do not agree across route/run/policy/replay                            │
│ - stop as PA gap                                                              │
│                                                                              │
│ PA_REQUIRES_UPSTREAM_REPAIR                                                   │
│ - PA cannot repair this locally                                               │
│ - upstream must fix missing contract/evidence/schema/route                    │
│                                                                              │
│ Example decision:                                                             │
│ status = PA_READY                                                             │
│ reason = L1, L0, C0, L5, AgentSpec, schema, provider lane, policy_hash,       │
│          blueprint_hash, route_digest, and replay_key are bound               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


OUTPUT
======

┌──────────────────────────────────────────────────────────────────────────────┐
│ PAAssemblyInput                                                              │
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
│ boundary receipts:                                                            │
│ - l1_plan_presence_receipt                                                    │
│ - l0_route_presence_receipt                                                   │
│ - c0_contract_presence_receipt                                                │
│ - provider_lane_receipt                                                       │
│ - response_schema_receipt                                                     │
│ - policy_replay_binding_receipt                                               │
│ - no_retrieval_receipt                                                        │
│ - no_route_change_receipt                                                     │
│ - no_provider_call_receipt                                                    │
│ - no_execution_receipt                                                        │
│ - no_l4_write_receipt                                                         │
│                                                                              │
│ assembly_gap_report:                                                          │
│ - empty if PA_READY                                                           │
│ - populated if missing/mismatched refs                                        │
│                                                                              │
│ NEXT: PA.1 resolves PromptBOM                                                 │
│ PA.0 DOES NOT RESOLVE BOM, COMPOSE SLOTS, AIRLOCK PAYLOADS, VALIDATE SLOTS,   │
│ TOKEN-TRIM, RENDER PROVIDER PAYLOAD, SIGN ARTIFACT, EXECUTE, OR WRITE L4      │
└──────────────────────────────────────────────────────────────────────────────┘


STOP AS PA GAP
==============

┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 1: Grounded route but missing C0 contract                           │
│                                                                              │
│ L0 says:                                                                      │
│ grounding_required = true                                                     │
│                                                                              │
│ But:                                                                          │
│ C0FinalEvidenceContract is missing                                            │
│                                                                              │
│ PA.0 result:                                                                  │
│ status = PA_INPUT_INCOMPLETE                                                  │
│ gap = missing C0 contract for grounded route                                  │
│                                                                              │
│ Rule: PA cannot retrieve evidence or answer from intent alone.                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 2: Terminal route tries to enter PA                                 │
│                                                                              │
│ L0 says:                                                                      │
│ route_id = R1A_EXACT_CACHE or R5_FALLBACK                                     │
│ execution_form = TERMINAL_SHORTCIRCUIT                                        │
│                                                                              │
│ But:                                                                          │
│ PA is invoked                                                                 │
│                                                                              │
│ PA.0 result:                                                                  │
│ status = PA_BOUNDARY_MISMATCH                                                 │
│ gap = route does not require prompt assembly                                  │
│                                                                              │
│ Rule: terminal [RET] routes go to Exit, not PA.                               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 3: Missing provider lane                                            │
│                                                                              │
│ L0 expects model execution.                                                   │
│ provider_lane is missing.                                                     │
│                                                                              │
│ PA.0 result:                                                                  │
│ status = PA_INPUT_INCOMPLETE                                                  │
│ gap = missing provider lane/model settings                                    │
│                                                                              │
│ Rule: PA cannot select an ad hoc provider.                                    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 4: Policy/replay mismatch                                           │
│                                                                              │
│ L0 policy_hash != C0 policy_hash                                              │
│ or route_digest does not match                                                │
│ or replay_key missing                                                         │
│                                                                              │
│ PA.0 result:                                                                  │
│ status = PA_BOUNDARY_MISMATCH                                                 │
│ gap = upstream refs not bound to same run/policy/replay                       │
│                                                                              │
│ Rule: PA cannot assemble mixed-contract packets.                              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP CASE 5: Boundary violation                                               │
│                                                                              │
│ Request into PA says:                                                         │
│ "Search more docs, call the model, and approve the answer."                  │
│                                                                              │
│ PA.0 result:                                                                  │
│ status = PA_REQUIRES_UPSTREAM_REPAIR                                          │
│ gap = PA asked to retrieve/execute/approve outside its authority              │
│                                                                              │
│ Rule: PA composes only.                                                       │
└──────────────────────────────────────────────────────────────────────────────┘


GUARDRAILS
==========

┌──────────────────────────────────────────────────────────────────────────────┐
│ PA.0 BOUNDARY CHECK GUARDRAILS                                                │
│                                                                              │
│ Require L1PlanContract.                                                       │
│ Require L0RouteContract.                                                      │
│ Require C0FinalEvidenceContract when grounding_required = true.               │
│ Require provider lane when model execution is expected.                       │
│ Require response schema when structured output is required.                   │
│ Require policy_hash, blueprint_hash, route_digest, replay_key.                │
│ Require upstream refs to bind to same request/run/trace.                      │
│ Stop terminal [RET] routes from entering PA.                                  │
│ Stop grounded routes without C0 evidence contract.                            │
│ Stop mixed-policy, mixed-run, stale, or mismatched refs.                      │
│                                                                              │
│ Do not retrieve.                                                              │
│ Do not route or reroute.                                                      │
│ Do not call provider.                                                         │
│ Do not execute tools.                                                         │
│ Do not approve final answer.                                                  │
│ Do not approve L2 execution.                                                  │
│ Do not assemble prompt slots yet.                                             │
│ Do not sign artifact.                                                         │
│ Do not write L4.                                                              │
│                                                                              │
│ If PA_READY:                                                                  │
│ proceed to PA.1.                                                              │
│                                                                              │
│ If gap or mismatch:                                                           │
│ stop as PA gap.                                                               │
│ no fetch, no route, no provider call, no execution, no runtime disposition.   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       ▼


MEMORY HOOK
===========

┌──────────────────────────────┐
│ Upstream                     │
│ L1 + L0 + C0 + L5 + schema   │
│ provider lane + replay refs  │
└───────────────┬──────────────┘
                │ upstream contracts
                ▼
┌──────────────────────────────┐
│ PA.0                         │
│ "May PA run at all?"         │
│ complete refs, same run,     │
│ right route, no boundary ask │
└───────────────┬──────────────┘
                │ PA_READY
                ▼
┌──────────────────────────────┐
│ PA.1                         │
│ "Which prompt components?"   │
│ resolve PromptBOM refs       │
└──────────────────────────────┘