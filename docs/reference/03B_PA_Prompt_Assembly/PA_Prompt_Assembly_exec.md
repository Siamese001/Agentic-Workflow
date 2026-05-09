====================================================================================================
                         PA PROMPT ASSEMBLY EXEC FLOWCHART
====================================================================================================

                         ┌────────────────────────────────────────────────────────────┐
                         │ UPSTREAM CONTRACTS                                         │
                         │                                                            │
                         │ L1PlanContract                                             │
                         │ L0RouteContract                                            │
                         │ C0FinalEvidenceContract, if grounded                       │
                         │ L5 governance refs                                         │
                         │ AgentSpec                                                  │
                         │ response schema                                            │
                         │ provider lane / model settings                             │
                         │ replay_key / policy_hash / blueprint_hash                  │
                         └─────────────────────────────┬──────────────────────────────┘
                                                       │
                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.0 BOUNDARY CHECK                                                                              │
│ "Is Prompt Assembly allowed to run with complete upstream refs?"                                  │
│                                                                                                  │
│ Checks:                                                                                          │
│ - L1 plan exists                                                                                 │
│ - L0 route exists                                                                                │
│ - C0 contract exists when grounding_required = true                                               │
│ - provider lane exists when model execution is expected                                           │
│ - response schema exists when structured output required                                          │
│ - policy_hash / replay_key / route_digest are bound                                               │
│ - PA is not being asked to retrieve, route, execute, write, or approve                            │
│                                                                                                  │
│ Emits: PAAssemblyInput | BoundaryCheckReceipt | assembly_gap_report                              │
└───────────────────────┬──────────────────────────────────────────────────────────────┬───────────┘
                        │                                                              │
                        │ PA_READY                                                     │ gap / mismatch
                        ▼                                                              ▼
┌──────────────────────────────────────────────┐                    ┌──────────────────────────────────┐
│ PA.1 LOAD / RESOLVE PROMPT BOM               │                    │ STOP AS PA GAP                   │
│ "Which prompt components are selected?"      │                    │ no fetch                         │
│                                              │                    │ no route                         │
│ Resolves refs for:                           │                    │ no provider call                 │
│ S0 system                                    │                    │ no execution                     │
│ D0 fences                                    │                    │ no runtime disposition           │
│ I0 instructions                              │                    └──────────────────────────────────┘
│ E0 examples                                  │
│ C0 evidence contract refs                    │
│ R0 schema                                    │
│ tool schemas                                 │
│ execution metadata                           │
│ provider/model settings                      │
│                                              │
│ Emits: PromptBOM | component_hash_map        │
│ Key rule: every component has stable ref/hash │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.2 SLOT COMPOSITION                                                                            │
│ "How do we place each component into the correct authority slot?"                                │
│                                                                                                  │
│ Canonical slot order:                                                                            │
│ S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0                                                     │
│ R0 is bound as schema, not loose prose when provider-native schema fields exist                   │
│ Y0 optional only with approved promotion refs                                                     │
│                                                                                                  │
│ Slot meanings:                                                                                   │
│ S0 = system identity and invariants                                                              │
│ D0 = fences, scope limits, anti-injection controls                                                │
│ I0 = operating instructions and AgentSpec constraints                                             │
│ E0 = approved examples                                                                           │
│ C0 = verified evidence, citations, contradictions, gaps                                           │
│ M0 = provider-safe control hints, no chain-of-thought disclosure                                  │
│ U0 = neutralized user task intent                                                                │
│ H0 = bounded repair hints only                                                                   │
│ R0 = response schema binding                                                                     │
│                                                                                                  │
│ Emits: StructuredPromptSlots | slot_authority_map | slot_lineage_map | slot_conflict_map          │
│ Key rule: lower-authority content cannot modify higher-authority slots                            │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.3 AIRLOCK / SECURITY PASS                                                                     │
│ "Can untrusted slot payloads enter safely without becoming instructions?"                         │
│                                                                                                  │
│ U0 airlock:                                                                                      │
│ - neutralizes role override, policy override, system/developer override, tool/provider claims     │
│ - preserves legitimate user task intent                                                          │
│                                                                                                  │
│ C0 payload classifier:                                                                           │
│ - retrieved chunks remain evidence, not instructions                                             │
│ - flags jailbreaks, fake policy text, credential exfiltration, tool-call imitation                │
│ - preserves citations and lineage                                                                │
│                                                                                                  │
│ H0 re-entry validation:                                                                          │
│ - same policy_hash / blueprint_hash / route scope                                                │
│ - no provider/tool/model substitution                                                            │
│ - no new facts without C0 support                                                                │
│                                                                                                  │
│ Emits: AssemblySecurityPassReceipt | safe_slot_payload_map | rejected_slot_payload_report        │
│ Key rule: C0, U0, H0, human text, and tool output are data/intent/proposal, not authority          │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.4 VALIDATE SLOT CONTRACT                                                                      │
│ "Do the composed slots obey authority, evidence, schema, and tool-binding contracts?"             │
│                                                                                                  │
│ Validates:                                                                                       │
│ - slot order intact                                                                              │
│ - U0 cannot override S0/D0/I0                                                                     │
│ - C0 cannot introduce instructions                                                               │
│ - E0 cannot override R0 schema                                                                   │
│ - H0 cannot widen repair scope                                                                   │
│ - Y0 cannot appear without promotion refs                                                        │
│ - C0 status is not inflated by PA                                                                │
│ - citations, support gaps, contradictions, and lineage are preserved                             │
│ - tools and schemas are structured bindings, not loose prose when native fields exist             │
│                                                                                                  │
│ Emits: SlotValidationReceipt | authority_order_receipt | context_contract_receipt                │
│ Key rule: PA validates packet structure, but does not approve L2 execution                        │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.5 TOKEN BUDGET / DETERMINISM                                                                  │
│ "Can the prompt fit deterministically without dropping mandatory authority or must-use evidence?" │
│                                                                                                  │
│ Preserves first:                                                                                 │
│ - S0 / D0 / I0                                                                                   │
│ - R0 schema binding                                                                              │
│ - must-use C0 evidence and citation anchors                                                       │
│                                                                                                  │
│ Trims in deterministic order:                                                                    │
│ 1. optional old conversation history                                                             │
│ 2. lowest-ranked optional E0 examples                                                            │
│ 3. lowest-ranked optional C0 chunks, never must-use citation anchors                              │
│ 4. optional Y0/H0 hints if allowed                                                               │
│                                                                                                  │
│ Emits: TokenBudgetLedger | deterministic_trimming_receipt | canonical_hash_input_manifest        │
│ Key rule: if mandatory content cannot fit, emit PA_BUDGET_OVERFLOW                               │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.6 PROVIDER-AWARE RENDERING                                                                    │
│ "How do the canonical slots map into this provider's fields without changing meaning?"            │
│                                                                                                  │
│ Provider lanes:                                                                                  │
│ - Anthropic                                                                                      │
│ - OpenAI GPT                                                                                     │
│ - OpenAI Reasoning                                                                               │
│ - Gemini                                                                                         │
│                                                                                                  │
│ Maps:                                                                                            │
│ - high-authority instructions to provider authority fields                                        │
│ - C0 evidence to data/document/context containers, never system/developer instruction             │
│ - tool schemas to provider-native tool fields                                                     │
│ - response schema to provider-native response schema / response format                            │
│ - reasoning controls to provider metadata where supported                                         │
│                                                                                                  │
│ Emits: ProviderRenderManifest | rendered_prompt_packet | provider_field_mapping_receipt          │
│ Key rule: same canonical slots may render differently per provider, but must preserve meaning      │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────── PA.8 red-team required? ────────────────────┐
              │                                                                  │
              │ yes                                                              │ no, only if policy permits
              ▼                                                                  ▼
┌──────────────────────────────────────────────┐                    ┌──────────────────────────────────┐
│ PA.8 AUTHORITY RED-TEAM / FORMAL VERIFY      │                    │ CONTINUE WITH REQUIRED RECEIPTS   │
│ "Can known injections break slot authority?" │                    │                                  │
│                                              │                    │ PA.8 may still run as audit proof  │
│ Tests:                                       │                    └─────────────────┬────────────────┘
│ - C0 instruction promotion                   │                                      │
│ - human text as authority                    │                                      │
│ - U0 override attempts                       │                                      │
│ - provider render slot reorder               │                                      │
│ - schema only in prose                       │                                      │
│ - token trim dropping authority slots        │                                      │
│ - hidden retrieval or execution              │                                      │
│                                              │                                      │
│ Emits: SlotAuthorityProof                    │                                      │
│ Key rule: prompt injection stays bounded     │                                      │
└───────────────────────┬──────────────────────┘                                      │
                        │                                                             │
                        └──────────────────────────────┬──────────────────────────────┘
                                                       │
                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.7 FINAL EMIT / COMPILED PROMPT ARTIFACT                                                        │
│ "Can we sign one provider-ready artifact for L2 handoff?"                                        │
│                                                                                                  │
│ Final artifact includes:                                                                         │
│ - compiled_prompt_artifact_id                                                                    │
│ - PromptBOM ref                                                                                  │
│ - structured slots ref                                                                           │
│ - provider render manifest ref                                                                   │
│ - final provider payload ref                                                                     │
│ - allowed tool schema refs via provider tools field                                               │
│ - response schema refs via provider response_schema / response_format                             │
│ - C0FinalEvidenceContract ref if grounded                                                        │
│ - source lineage refs                                                                            │
│ - security pass receipt                                                                          │
│ - slot validation receipt                                                                        │
│ - token budget ledger                                                                            │
│ - deterministic trimming receipt when trimming occurred                                           │
│ - policy_hash / blueprint_hash / route_digest / replay_key                                       │
│ - manifest_hash                                                                                  │
│ - HMAC signature                                                                                 │
│                                                                                                  │
│ Emits: CompiledPromptArtifact | manifest_hash_receipt | hmac_signature_receipt                   │
│        L2HandoffEnvelope                                                                          │
│                                                                                                  │
│ Key rule: unsigned artifact cannot be marked L2 handoff ready                                     │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HANDOFF TO L2 EXECUTE                                                                            │
│ L2 receives:                                                                                     │
│ - signed CompiledPromptArtifact                                                                  │
│ - L2HandoffEnvelope                                                                              │
│ - provider lane and model settings                                                               │
│ - response schema ref                                                                            │
│ - tool schema refs                                                                               │
│ - capability / sandbox refs if already bound upstream                                             │
│ - manifest_hash / HMAC / replay_key                                                              │
│                                                                                                  │
│ L2, not PA, performs provider/model/tool execution.                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘


====================================================================================================
                         PA CONTROL AND PROOF SPINE
====================================================================================================

Runtime Gates around PA:
  G10 Prompt Assembly
  G13 Content Trust
  G17 Privacy / Cross-context
  G21 Schema readiness
  G23 Security / Leakage

Required PA spans:
  pa.run
    -> pa.boundary_check
    -> pa.bom_resolve
    -> pa.slot_compose
    -> pa.airlock
    -> pa.slot_validate
    -> pa.token_budget
    -> pa.render
    -> pa.emit_envelope
    -> pa.red_team_scan

Must prove:
  authority order intact
  retrieved/tool/human content stayed data
  deterministic BOM
  slot contract validated
  token budget deterministic
  provider rendering deterministic
  exactly one signed envelope/artifact
  red-team scan completed where required
  no retrieval
  no route change
  no provider call
  no tool execution
  no L4 write
  no final answer


====================================================================================================
                         PA CHILD MAP
====================================================================================================

  PA.0 Boundary Check
  - proves PA is eligible to run and has all required upstream refs
  - catches missing RouteContract, missing C0 contract for grounded route, terminal route mismatch

  PA.1 Prompt BOM
  - resolves stable component refs and hashes
  - catches stale/missing system, fences, instructions, schema, tools, execution metadata

  PA.2 Slot Composition
  - builds canonical authority-tiered slots
  - catches lower-authority override attempts and slot order violations

  PA.3 Airlock Security Pass
  - neutralizes U0, classifies C0 payloads, validates H0 repair hints
  - catches prompt injection, fake policy, tool-call imitation, provider/tool substitution

  PA.4 Validate Slot Contract
  - validates authority order, C0 context contract, schema/tool bindings
  - catches missing citations, flattened lineage, schema conflicts, loose tool/schema prose

  PA.5 Token Budget / Determinism
  - makes prompt fit deterministically
  - catches required evidence overflow and non-deterministic prompt hashing

  PA.6 Provider Rendering
  - maps canonical slots to provider-specific fields
  - catches C0 rendered as instruction, unsupported provider features, schema/tool render gaps

  PA.7 Final Emit
  - emits signed CompiledPromptArtifact and L2 handoff envelope
  - catches missing manifest hash, missing HMAC, raw secrets/client handles in handoff

  PA.8 Authority Red-Team
  - proves slot authority against adversarial fixtures
  - catches injection promotion, human-as-authority, provider reorder, schema-only-in-prose


====================================================================================================
                         PA ONE-LINE ARROW
====================================================================================================

  Upstream contracts
      -> PA.0 boundary check
      -> PA.1 resolve prompt BOM
      -> PA.2 compose authority slots
      -> PA.3 airlock untrusted payloads
      -> PA.4 validate slot contract
      -> PA.5 fit deterministic token budget
      -> PA.6 render for provider
      -> PA.8 red-team authority where required
      -> PA.7 sign compiled artifact
      -> L2 executes