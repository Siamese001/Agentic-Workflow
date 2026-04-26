========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03B_PA_Prompt_Assembly
Canonical file: Prompt Assembly_exec.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: Prompt Assembly_exec.md
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

==============================================================================================================================
                         PROMPT ASSEMBLY — END-TO-END COMPACT VIEW
        trusted composer | no retrieval | no execution | no durable write | emits signed prompt artifact
==============================================================================================================================

CORE IDEA
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Prompt Assembly is the packet builder between C0 retrieval and L2 execution.

It does NOT:
- retrieve evidence
- choose the route
- execute tools
- call the model for work
- mutate L4 state

It DOES:
- load system / policy / instruction blocks
- bind grounded evidence
- neutralize user task text
- apply slot authority ordering
- bind output schema
- budget tokens deterministically
- emit a signed CompiledPromptArtifact for L2 / provider dispatch


==============================================================================================================================
END-TO-END FLOW
==============================================================================================================================

 [1] INTAKE
     validated_request
     request_id / trace_root / caller_scope
          │
          ▼
 [2] L1 REASONING + PLAN
     task_spec / query_spec / grounding_required / output_target
          │
          ▼
 [3] L0 ROUTING
     route_contract / selected route / model lane / policy posture
          │
          ├──────────────────────────────────────────────────────────────────────────────────────┐
          │                                                                                      │
          ▼                                                                                      ▼
 [R1/R5 TERMINAL ROUTES]                                                            [R3 GROUNDED READ ROUTE]
 exact cache / semantic cache / fallback                                            factual support required
          │                                                                                      │
          ▼                                                                                      ▼
 [RET TO EXIT CONTROL]                                                    [C0 CONTEXT ENGINE / RETRIEVAL]
                                                                             verified chunks / citations
                                                                             evidence contract / support score
                                                                                      │
                                                                                      ▼
                                                                        [PROMPT ASSEMBLY / PACKET BUILDER]
                                                                                      │
                                                                                      ▼
                                                                        [L2 SOVEREIGN LLM GATEWAY]
                                                                                      │
                                                                                      ▼
                                                                        [MODEL / TOOL / FINAL OUTPUT]
                                                                                      │
                                                                                      ▼
                                                                        [SEALED L2 ARTIFACT]
                                                                                      │
                                                                                      ▼
                                                                        [EXIT EVAL & CONTROL]
                                                                                      │
                                                                                      ▼
                                                                        [RESPONSE OR COMMIT REQUEST]


==============================================================================================================================
PROMPT ASSEMBLY COMPACT PIPELINE
==============================================================================================================================

 [L1 plan] + [L0 route] + [C0 evidence] + [L4 governed refs]
        │
        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLY                                                                                                           │
│ trusted composer only                                                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. LOAD BOM                                                                                                               │
│    S0 system | D0 fences | I0 instructions | E0 exemplars | R0 schema                                                      │
│                                                                                                                            │
│ 2. COMPOSE SLOTS                                                                                                          │
│    C0 grounded context | M0 private controls | U0 neutralized task | Y0 priors | H0 healing hints                            │
│                                                                                                                            │
│ 3. VALIDATE                                                                                                               │
│    authority order | injection neutralization | context contract | healer re-entry                                           │
│                                                                                                                            │
│ 4. BUDGET                                                                                                                 │
│    provider tokenizer | reserve output | deterministic eviction | stable prompt prefix                                      │
│                                                                                                                            │
│ 5. EMIT                                                                                                                   │
│    CompiledPromptArtifact | HMAC | manifest_hash | replay metadata | provider adapter packet                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
 [L2 SovereignLLMGateway]
        │
        ▼
 [sealed L2 output]
        │
        ▼
 [Exit Eval & Control]


==============================================================================================================================
RICHER PROMPT PACKET
==============================================================================================================================

Canonical composition order:

    S0 ─► D0 ─► I0 ─► E0 ─► C0 ─► M0 ─► U0 ─► H0
                                          │
                                          └────────► R0 bound to API response_schema, not inlined as prose


┌──────┬──────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
│ SLOT │ NAME                         │ COMPACT PURPOSE                                                                      │
├──────┼──────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
│ S0   │ SYSTEM / STATE               │ Hard constitution, global invariants, non-negotiable safety directives              │
│ D0   │ INJECTIONS / FENCES          │ Role boundaries, scope limits, tool constraints, anti-injection rules                │
│ I0   │ INSTRUCTIONAL                │ Agent identity, capability mixins, task operating instructions                       │
│ E0   │ EXEMPLARS                    │ Few-shot examples, approved answer shapes, golden patterns                           │
│ C0   │ GROUNDED CONTEXT             │ Verified chunks, citations, graph facts, source lineage                              │
│ M0   │ PRIVATE META-CONTROLS        │ Provider-safe internal reasoning posture and answer discipline                       │
│ U0   │ USER TASK                    │ Actual user request after airlock / injection neutralization                         │
│ Y0   │ SYNTHESIS / LEARNING PRIORS  │ Approved learning priors, telemetry summaries, rubric hints                          │
│ H0   │ HEALING HINTS                │ Repair proposal or retry guidance after healer re-entry validation                   │
│ R0   │ OUTPUT SCHEMA                │ Structured response contract bound through provider API field                        │
└──────┴──────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘


==============================================================================================================================
KEY INVARIANTS
==============================================================================================================================

1. C0 retrieves. Prompt Assembly packages. L2 executes.
2. Lower-authority slots can never override higher-authority slots.
3. U0 has zero authority. It expresses task intent only.
4. Retrieved C0 content is data, not instruction.
5. R0 schema rides the API response_schema / response_format field, not prompt prose.
6. Tool schemas ride the API tools field, not prompt prose.
7. Prompt Assembly is deterministic for the same BOM, slot contents, and secret key.
8. S0 + D0 + I0 remain stable for cache-prefix discipline.
9. H0 healing hints are proposed authority only and must pass re-entry validation.
10. The final output is a frozen, signed CompiledPromptArtifact.


==============================================================================================================================
COMPACT MENTAL MODEL
==============================================================================================================================

Shelves / C0 retrieve evidence
        │
        ▼
Packet Builder / Prompt Assembly binds evidence + rules + task + schema
        │
        ▼
Stack Staff / L2 execute one bounded model/tool step
        │
        ▼
Exit Desk checks whether the sealed result can leave, reroute, escalate, or request commit