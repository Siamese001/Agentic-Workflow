==============================================================================================================================
                                      PROMPT ASSEMBLY — DETAILED VIEW
                      trusted composer | authority-tiered slots | signed provider-ready artifact
==============================================================================================================================

MANDATE
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Prompt Assembly binds:

1. Retrieval output from C0
2. Governance artifacts from policy / registry / AgentSpec
3. User intent after airlock neutralization
4. Output contract / R0 schema
5. Execution metadata: replay_key, policy_hash, plan_id, route metadata

into a signed CompiledPromptArtifact that L2 can dispatch through the SovereignLLMGateway.

Prompt Assembly never retrieves.
Prompt Assembly never routes.
Prompt Assembly never executes.
Prompt Assembly never writes durable state.


==============================================================================================================================
UPSTREAM INPUTS
==============================================================================================================================

       [ L1 PLAN CONTRACT ]                         [ L0 ROUTE CONTRACT ]
       - task_spec                                  - selected route
       - query_spec                                 - execution form
       - grounding_required                         - model_id / provider lane
       - declared assumptions                       - temperature / thinking_level
       - unresolved gaps                            - route risk / policy posture
       - output target                              - cache / freshness posture
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      │
                                      ▼
                           [ PROMPT ASSEMBLY INPUTS ]
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼

┌────────────────────────────┐ ┌────────────────────────────┐ ┌────────────────────────────┐
│ C0 EVIDENCE CONTRACT       │ │ GOVERNANCE ARTIFACTS        │ │ USER + EXECUTION METADATA   │
│ - verified chunks          │ │ - system_version_hash       │ │ - raw user task             │
│ - cited spans              │ │ - policy_hash               │ │ - neutralized user task     │
│ - source_ids / lineage     │ │ - role fences               │ │ - replay_key                │
│ - support score            │ │ - allowed tool posture      │ │ - plan_id                   │
│ - coverage gaps            │ │ - AgentSpec                 │ │ - idempotency nonce         │
│ - abstain recommendation   │ │ - response schema contract  │ │ - provider target           │
└─────────────┬──────────────┘ └─────────────┬──────────────┘ └─────────────┬──────────────┘
              │                              │                              │
              └──────────────────────────────┴──────────────┬───────────────┘
                                                             │
                                                             ▼
==============================================================================================================================
                                      PA.0 BOUNDARY CHECK
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.0 BOUNDARY CHECK                                                                                                      │
│ Confirms this is assembly work only.                                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Boundary laws:                                                                                                             │
│ - C0 already retrieved evidence. PA does not fetch more.                                                                    │
│ - L0 already selected the route. PA does not reroute.                                                                       │
│ - L2 will execute later. PA does not perform task execution.                                                                │
│ - UWG owns durable writes. PA cannot mutate L4.                                                                             │
│ - L5 policy can constrain assembly, but PA itself is not the policy authority.                                              │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼

==============================================================================================================================
                                      PA.1 LOAD / RESOLVE PROMPT BOM
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.1 LOAD / RESOLVE                                                                                                      │
│ Builds the PromptBOM, which is the bill of materials for the final compiled prompt packet.                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Resolution steps:                                                                                                         │
│                                                                                                                            │
│ 1. Resolve S0 system/state                                                                                                 │
│    - selected by system_version_hash                                                                                        │
│    - loads constitution, identity floor, safety invariants                                                                   │
│                                                                                                                            │
│ 2. Resolve D0 fences                                                                                                       │
│    - selected by policy posture, route risk, and task class                                                                  │
│    - loads injection fences, role boundaries, tool limits, scope constraints                                                 │
│                                                                                                                            │
│ 3. Resolve I0 instructional mixins                                                                                          │
│    - selected by AgentSpec and task type                                                                                     │
│    - loads capability instructions and operating manuals                                                                     │
│                                                                                                                            │
│ 4. Resolve E0 exemplars                                                                                                     │
│    - selected by task class and allowed exemplar bank                                                                        │
│    - loads few-shot examples only when helpful and budget-safe                                                               │
│                                                                                                                            │
│ 5. Resolve C0 context                                                                                                       │
│    - consumes EvidenceContract                                                                                               │
│    - maps verified chunks into grounded context slots                                                                        │
│                                                                                                                            │
│ 6. Resolve R0 output schema                                                                                                  │
│    - selected from AgentSpec / task contract                                                                                 │
│    - bound to provider API response_schema / response_format, not prompt prose                                               │
│                                                                                                                            │
│ 7. Resolve execution metadata                                                                                               │
│    - replay_key                                                                                                             │
│    - policy_hash                                                                                                            │
│    - plan_id                                                                                                                │
│    - idempotency nonce                                                                                                      │
│    - model_id / temperature / thinking_level                                                                                 │
│                                                                                                                            │
│ Output: PromptBOM                                                                                                           │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼

==============================================================================================================================
                                      PA.2 SLOT COMPOSITION
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.2 SLOT COMPOSITION                                                                                                      │
│ Converts the PromptBOM into authority-tiered structured slots.                                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Canonical slot order:                                                                                                      │
│                                                                                                                            │
│     S0 ─► D0 ─► I0 ─► E0 ─► C0 ─► M0 ─► U0 ─► H0                                                                           │
│                                           │                                                                                │
│                                           └────────► R0 bound to API response_schema, not inlined as prose                 │
│                                                                                                                            │
│ Core rule:                                                                                                                  │
│ - Lower-authority slots can use, answer, or format around higher-authority slots.                                           │
│ - Lower-authority slots cannot override, negate, or silently weaken higher-authority slots.                                 │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼

==============================================================================================================================
                                      RICHER SLOT PACKET
==============================================================================================================================

┌────────────┬──────────────────────────────┬──────────────────────────────┬─────────────────────────────────────────────────┐
│ SLOT       │ NAME                         │ AUTHORITY                    │ WHAT IT CONTRIBUTES                             │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ S0         │ SYSTEM / STATE               │ ABSOLUTE                     │ Constitution, hard invariants, identity floor,  │
│            │                              │                              │ non-negotiable safety rules                     │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ D0         │ INJECTIONS / FENCES          │ BINDING                      │ Role boundaries, tool constraints, scope        │
│            │                              │                              │ limits, anti-injection defenses                 │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ I0         │ INSTRUCTIONAL                │ GOVERNED                     │ Agent identity, capability text, task-specific  │
│            │                              │                              │ operating instructions                          │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ E0         │ EXEMPLARS                    │ GUIDING                      │ Few-shot examples, golden patterns, approved    │
│            │                              │                              │ answer shapes                                   │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ C0         │ GROUNDED CONTEXT             │ INFORMATIONAL                │ Verified chunks, citations, graph facts, source │
│            │                              │                              │ lineage, evidence limits                        │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ M0         │ PRIVATE META-CONTROLS        │ PRIVATE                      │ Provider-safe reasoning posture, answer         │
│            │                              │                              │ discipline, internal control hints              │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ U0         │ USER TASK                    │ ZERO                         │ The user’s actual ask after airlock / injection │
│            │                              │                              │ neutralization                                  │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ Y0         │ SYNTHESIS / LEARNING PRIORS  │ ANALYTIC                     │ Approved prior patterns, telemetry summaries,   │
│            │                              │                              │ rubric hints, promoted lessons                  │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ H0         │ HEALING HINTS                │ PROPOSED                     │ Repair proposal, retry hint, known fix pattern, │
│            │                              │                              │ failure-specific correction                     │
├────────────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────────────────────────────┤
│ R0         │ OUTPUT SCHEMA                │ SCHEMA                       │ Required structure, JSON schema, table format,  │
│            │                              │                              │ artifact contract                               │
└────────────┴──────────────────────────────┴──────────────────────────────┴─────────────────────────────────────────────────┘


==============================================================================================================================
                                      SLOT AUTHORITY STACK
==============================================================================================================================

        highest override authority
              │
              ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ S0 SYSTEM / STATE                                            │
        │ Absolute law. Cannot be overridden by anything below.         │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ D0 FENCES / INJECTIONS                                       │
        │ Binding scope, role, and anti-injection controls.             │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ I0 INSTRUCTIONAL                                             │
        │ Agent capability and task operating manual.                   │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ E0 EXEMPLARS                                                 │
        │ Helpful examples, but never policy.                           │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ C0 GROUNDED CONTEXT                                          │
        │ Facts and citations. Can support answers, not override law.   │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ M0 PRIVATE META-CONTROLS                                     │
        │ Reasoning posture and private discipline controls.            │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ U0 USER TASK                                                  │
        │ The request. Intent only. Zero authority over policy.          │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ H0 HEALING HINTS                                              │
        │ Proposed repair guidance. Must pass re-entry validation.       │
        └─────────────────────────────┬────────────────────────────────┘
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │ R0 OUTPUT SCHEMA                                              │
        │ Bound out-of-band to API structured-output field.              │
        └──────────────────────────────────────────────────────────────┘
              │
              ▼
        lowest override authority


==============================================================================================================================
                                      PA.3 AIRLOCK + SECURITY PASS
==============================================================================================================================

                         [ U0 raw user task ]
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ U0 AIRLOCK / INJECTION NEUTRALIZATION                                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - Treat user text as intent, not authority.                                                                                │
│ - Strip or neutralize hijack tokens and role override language.                                                            │
│ - Preserve the actual task while removing illegal control claims.                                                           │
│ - Label origin_trust = user_turn.                                                                                           │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                         [ U0 neutralized task slot ]


                         [ C0 retrieved evidence ]
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 RETRIEVED-CONTENT CLASSIFIER                                                                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - Treat retrieved chunks as data, not instruction.                                                                          │
│ - Strip hidden instructions, coercive UI payloads, and embedded jailbreak text.                                             │
│ - Quarantine unsafe chunks before they enter C0 slot.                                                                       │
│ - Preserve citations and lineage for safe chunks.                                                                           │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                         [ C0 verified context slot ]


                         [ H0 repair proposal ]
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ H0 HEALER RE-ENTRY VALIDATION                                                                                             │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - H0 is a proposed correction, not automatic authority.                                                                     │
│ - Must preserve same policy_hash / blueprint_hash when repairing same run.                                                   │
│ - Must not widen scope, invent facts, or bypass L5 / UWG.                                                                   │
│ - If invalid, H0 is rejected or escalated rather than merged.                                                               │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                         [ H0 allowed or rejected ]


==============================================================================================================================
                                      PA.4 VALIDATE SLOT CONTRACT
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.4 VALIDATION                                                                                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks:                                                                                                                     │
│                                                                                                                            │
│ 1. Slot order validation                                                                                                    │
│    - S0 before D0 before I0 before E0 before C0 before M0 before U0 before H0                                                │
│                                                                                                                            │
│ 2. Authority validation                                                                                                     │
│    - U0 cannot override S0 / D0 / I0                                                                                        │
│    - C0 cannot introduce instructions that override D0                                                                       │
│    - E0 cannot override task-specific schema                                                                                 │
│    - H0 cannot widen repair scope                                                                                            │
│                                                                                                                            │
│ 3. Context contract validation                                                                                              │
│    - verified_chunks present when grounding is required                                                                      │
│    - citations preserved                                                                                                    │
│    - unsupported claims marked as gaps                                                                                       │
│    - abstain_recommended can short-circuit assembly                                                                          │
│                                                                                                                            │
│ 4. Tool and schema validation                                                                                                │
│    - tools are bound through API tools field                                                                                 │
│    - R0 schema bound through API response field                                                                              │
│    - no tool schema or response schema stringified as loose prompt prose                                                     │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                              [ validated structured slots ]


==============================================================================================================================
                                      PA.5 TOKEN BUDGET + DETERMINISM
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.5 TOKEN BUDGETER                                                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Stable prefix discipline:                                                                                                  │
│ - S0 + D0 + I0 remain stable to improve provider prompt-cache hits and replay consistency.                                  │
│                                                                                                                            │
│ Token reserve:                                                                                                             │
│ - reserve output tokens                                                                                                    │
│ - reserve response schema overhead                                                                                          │
│ - reserve tool-call overhead where applicable                                                                               │
│                                                                                                                            │
│ Deterministic trimming order:                                                                                              │
│ 1. Compress or remove oldest conversation history if present                                                                │
│ 2. Trim lowest-ranked optional C0 chunks                                                                                    │
│ 3. Preserve must-use evidence and citation anchors                                                                          │
│ 4. Preserve S0 / D0 / I0 intact                                                                                             │
│ 5. Preserve R0 schema binding                                                                                                │
│                                                                                                                            │
│ Overflow behavior:                                                                                                          │
│ - If required content cannot fit, mark OVERFLOW / REFINE / ABSTAIN.                                                        │
│ - Do not silently drop mandatory evidence or governing instructions.                                                        │
│ - Do not proceed with fake completeness.                                                                                    │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                              [ budgeted structured slots ]


==============================================================================================================================
                                      PA.6 PROVIDER-AWARE RENDERING
==============================================================================================================================

                         [ structured slot payload ]
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROVIDER ADAPTER                                                                                                          │
│ Renders the same logical slots differently per model provider.                                                             │
│ Manifest hash stays based on canonical structured slot payload, not provider-specific rendered strings.                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Anthropic lane:                                                                                                            │
│ - system= carries high-authority instructions                                                                               │
│ - context may use document containers                                                                                       │
│ - long-context order may hoist data and tail-repeat task reminder                                                           │
│                                                                                                                            │
│ OpenAI GPT lane:                                                                                                           │
│ - system / developer / user roles used according to provider rules                                                          │
│ - headings may separate Role, Instructions, Context, Examples, Final Instructions                                           │
│                                                                                                                            │
│ OpenAI reasoning lane:                                                                                                     │
│ - avoid exposed chain-of-thought instructions                                                                               │
│ - thinking controls ride provider-native routing metadata where supported                                                   │
│                                                                                                                            │
│ Gemini lane:                                                                                                               │
│ - data-first or instruction-after-data patterns may be used for long context                                                │
│ - structured outputs ride response_schema field                                                                             │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                         [ provider-ready prompt packet ]


==============================================================================================================================
                                      PA.7 FINAL EMIT
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.7 COMPILED PROMPT ARTIFACT                                                                                             │
│ Frozen signed output from Prompt Assembly.                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Carries:                                                                                                                    │
│ - final_system / final_user or provider-specific message fields                                                             │
│ - structured slots_used                                                                                                     │
│ - allowed_tools_schema via API tools field, not inline prose                                                                │
│ - R0 response_schema via API response_format / response_schema field                                                        │
│ - token estimate / budget status                                                                                            │
│ - manifest_hash over canonical structured slot bytes                                                                        │
│ - HMAC-SHA256 signature                                                                                                     │
│ - replay_key / policy_hash / plan_id                                                                                        │
│ - model_id / temperature / thinking_level                                                                                   │
│ - idempotency nonce carried separately from deterministic hash inputs                                                       │
└──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                                      [ DISPATCH TO L2 SOVEREIGN LLM GATEWAY ]
                                                               │
                                                               ▼
                                      [ PROVIDER MODEL / TOOL CALL / FINAL ANSWER ]
                                                               │
                                                               ▼
                                      [ SEALED L2 OUTPUT ]
                                                               │
                                                               ▼
                                      [ EXIT EVAL & CONTROL ]


==============================================================================================================================
                                      DETAILED END-TO-END ASCII
==============================================================================================================================

 [Validated Request]
        │
        ▼
 [L1 Reasoning + Plan]
        │
        │  produces:
        │  - task_spec
        │  - query_spec
        │  - grounding_required
        │  - output target
        ▼
 [L0 Route Decision]
        │
        │  produces:
        │  - route_contract
        │  - provider lane
        │  - route risk
        │  - thinking_level / temperature
        │
        ├───────────────────────────────────────────────────────────────┐
        │                                                               │
        ▼                                                               ▼
 [Terminal Route: R1/R5]                                      [Grounded Route: R3]
 exact cache / semantic cache / fallback                       needs evidence
        │                                                               │
        ▼                                                               ▼
 [RET to Exit Control]                                      [C0 Context Engine]
                                                                │
                                                                │ produces:
                                                                │ - EvidenceContract
                                                                │ - verified chunks
                                                                │ - citations
                                                                │ - support gaps
                                                                ▼
                                                     ┌──────────────────────────────┐
                                                     │ PROMPT ASSEMBLY              │
                                                     │                              │
                                                     │ PA.0 Boundary Check          │
                                                     │ PA.1 Load / Resolve BOM      │
                                                     │ PA.2 Compose Slots           │
                                                     │ PA.3 Airlock / Security      │
                                                     │ PA.4 Validate Slot Contract  │
                                                     │ PA.5 Budget / Determinism    │
                                                     │ PA.6 Provider Rendering      │
                                                     │ PA.7 Emit Signed Artifact    │
                                                     └──────────────┬───────────────┘
                                                                    │
                                                                    ▼
                                                     [CompiledPromptArtifact]
                                                                    │
                                                                    │ carries:
                                                                    │ - structured slots
                                                                    │ - response_schema binding
                                                                    │ - allowed tools binding
                                                                    │ - replay_key / policy_hash
                                                                    │ - manifest_hash / HMAC
                                                                    ▼
                                                     [L2 SovereignLLMGateway]
                                                                    │
                                                                    ▼
                                                     [Provider Model / Tool Call]
                                                                    │
                                                                    ▼
                                                     [Sealed L2 Artifact]
                                                                    │
                                                                    ▼
                                                     [Exit Eval & Control]
                                                                    │
                        ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
                        │                                           │                                           │
                        ▼                                           ▼                                           ▼
                  [Allow / Finish]                            [Deny / Reroute]                            [Escalate / HITL]
                        │                                           │                                           │
                        ▼                                           ▼                                           ▼
                  [Response]                              [Return to safe path]                    [Bounded human review]
                        │                                                                                       │
                        └───────────────────────────────────────────┬───────────────────────────────────────────┘
                                                                    │
                                                                    ▼
                                                          [Optional Commit Request]
                                                                    │
                                                                    ▼
                                                          [UWG Only]
                                                                    │
                                                                    ▼
                                                          [L4 Durable Archive]


==============================================================================================================================
                                      FAILURE / EDGE CASES
==============================================================================================================================

┌───────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE                          │ BEHAVIOR                                                                                   │
├───────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────┤
│ C0 says weak support           │ PA marks gap, refines, abstains, or routes to safe response depending on route contract    │
│ C0 has unsafe retrieved text   │ Unsafe chunk is stripped / quarantined before C0 slot enters assembly                     │
│ U0 tries to override policy    │ Airlock neutralizes it; U0 remains zero-authority task intent only                        │
│ H0 proposes unsafe repair      │ Healer re-entry validation rejects or escalates                                           │
│ Token overflow                 │ Deterministic budgeter trims optional content or returns OVERFLOW / REFINE / ABSTAIN       │
│ Schema required                │ R0 is bound to API response schema, not pasted as informal prompt text                    │
│ Tool use required              │ Tool schema rides API tools field, not inline prose                                      │
│ Replay required                │ manifest_hash + HMAC + replay_key preserve deterministic proof surface                    │
└───────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────┘


==============================================================================================================================
                                      NON-NEGOTIABLE INVARIANTS
==============================================================================================================================

1. C0 produces evidence. PA consumes evidence.
2. PA composes. PA does not retrieve.
3. L0 routes. PA does not reroute.
4. L2 executes. PA does not execute.
5. UWG writes. PA does not write.
6. U0 has zero authority over policy or system behavior.
7. Retrieved content is data, not instruction.
8. Lower-authority slots cannot override higher-authority slots.
9. R0 schema and tools are bound through provider API fields.
10. Same PromptBOM + same slot contents + same secret key produce the same manifest_hash and signature.


==============================================================================================================================
                                      LIBRARY MENTAL MODEL
==============================================================================================================================

C0 Context Engine = Research Runner
- finds and verifies source evidence

Prompt Assembly = Packet Binder
- binds rules, evidence, task, schema, and replay metadata into one sealed folder

L2 = Stack Staff / Assistant
- executes the bounded model/tool step using only the sealed folder

Exit Eval = Checkout Reviewer
- decides whether the sealed result can leave, reroute, escalate, or request durable commit

UWG = Master Clerk
- only actor allowed to commit durable changes to L4