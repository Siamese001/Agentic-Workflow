# [PA] Prompt Assembly — Reference

> **Status**: Refreshed 2026-04-23 to reflect code reality. Supersedes the legacy
> PA.1–PA.4 ASCII macro-flow (retained in `Archive/` for historical reference).
>
> **SSOT for code**: `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/core/prompt_assembler.py`,
> `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py`,
> `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/prompt_envelope.py`,
> `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/contracts/slot_contracts.py`.
>
> **Cross-refs**: `C5_Retrieval_Prompt_Assembly.md` (C0 retrieval → Envelope),
> `ADR-PROMPT-ASSEMBLY-001` (provider-aware rendering),
> `ADR-PROMPT-ASSEMBLY-002` (uncovered-gap rectification — agentic reminders,
> token counter, history compressor, eviction, idempotency nonce, thinking-depth,
> cache prefix discipline).

## 1. Mandate

Prompt Assembly is the **trusted composer** that binds:

1. Retrieval output (verified chunks + citations) from C0,
2. Governance artifacts (S0 system prompt, D0 injection fences, I0 mixins),
3. User intent (U0, neutralized), and
4. Output contract (R0 schema) + execution metadata (routing meta, replay key)

into a signed `CompiledPromptArtifact` the gateway can dispatch to the model
provider. Assembly never retrieves; Retrieval never composes.

## 2. Slot Taxonomy (10 slots, authority-tiered)

Defined in `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/contracts/slot_contracts.py`.

| Slot | Name | Authority | Purpose |
|------|------|-----------|---------|
| `S0` | SYSTEM / STATE | ABSOLUTE | Constitution, invariants, hard-coded safety directives |
| `D0` | INJECTIONS | BINDING | Role fences, tool constraints, scope boundaries |
| `M0` | META-COGNITIVE | PRIVATE | Chain-of-thought scaffolds, `<thinking>`/`<answer>` shape |
| `I0` | INSTRUCTIONAL | GOVERNED | Identity and mixin capability text (per AgentSpec) |
| `E0` | EXEMPLARS | GUIDING | Golden Context, few-shot examples |
| `C0` | DEPENDENCY | INFORMATIONAL | Validated RAG context (chunks + citations) |
| `Y0` | SYNTHESIS | ANALYTIC | Pattern analysis, telemetry summary, meta-learning proposals |
| `U0` | USER PROMPT | ZERO | Raw user intent — MUST pass Airlock before entering assembly |
| `H0` | HEALING PROPOSAL | PROPOSED | L2.3 healing corrections; requires re-entry validation |
| `R0` | OUTPUT FORMAT | SCHEMA | Response schema / structural requirements |

Canonical composition order (post ADR-PROMPT-ASSEMBLY-001):

```
S0 → D0 → I0 → E0 → C0 → M0 → U0 → H0
                                    │
                                    └─► R0 (bound to API response_schema, not inlined)
```

Slot-order validator: `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/scripts/validate_assembly.py`.

## 3. Pipeline (module-cited)

```
┌─────────────────────────────────────────────────────────────────────┐
│  INGRESS                                                             │
│  • Query intent vector        (L0 router)                           │
│  • Verified chunks + cites    (C0 retrieval → PromptEnvelope)       │
│  • Entity subgraph / triples  (knowledge graph)                     │
│  • Evidence contract          (EvidenceContract)                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [PA.1]  LOAD                                                        │
│  prompt_envelope.PromptEnvelopeFactory.from_contract(...)           │
│  • Seals replay_key + policy_hash + plan_id                         │
│  • Sets PromptAssemblyStatus (READY | OVERFLOW | ABSTAIN | ...)      │
│  • Emits immutable PromptEnvelope                                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [PA.2]  RESOLVE                                                     │
│  PromptBOMBuilder(...) → PromptBOM                                  │
│  • system_version_hash selects S0 + D0 fences from TemplateRegistry │
│  • mixins_required → sorted I0 mixin IDs                            │
│  • template_args.intent_class → C0 JIT load path                    │
│  • response_schema from AgentSpec                                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [PA.3]  COMPOSE                                                     │
│  AirlockAssembler.assemble_from_bom(bom, secret_key, ...)           │
│  • Loads S0 (override or registry), D0 fences, I0 mixins            │
│  • ElevatorShaft JIT load → C0 content                              │
│  • Wraps U0 → AssemblyInjectionNeutralizer.neutralize               │
│  • validate_slot_order (S0→D0→I0→C0→U0 minimum; E0/M0/H0 optional)  │
│  • Produces structured slots for provider adapter (ADR-PA-001)      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [PA.4]  BUDGET  (token counter + deterministic eviction)            │
│  (ADR-PROMPT-ASSEMBLY-002 — currently: char/4 estimate only)        │
│  • Provider-aware tokenizer (tiktoken / anthropic / gemini)         │
│  • Reserve output tokens                                             │
│  • Deterministic eviction:                                           │
│      P1 — oldest convo-history turns (history_compressor)           │
│      P2 — lowest-ranked optional chunks (must-use preserved)        │
│  • Cache-prefix stability: S0 + D0 + I0 retained intact             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [PA.5]  EMIT                                                        │
│  CompiledPromptArtifact (frozen) with:                              │
│  • final_system / final_user strings (per provider adapter)         │
│  • slots_used list                                                   │
│  • allowed_tools_schema (from API tools field, not inline text)     │
│  • response_schema (bound; passed to API response_format)           │
│  • tokens estimate                                                   │
│  • HMAC-SHA256 signature over canonical slot bytes                   │
│  • manifest_hash (deterministic) + idempotency nonce (ADR-PA-002)    │
│  • routing meta: model_id, temperature, thinking_level              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
            [Dispatch to L2 SovereignLLMGateway → provider adapter]
```

## 4. Provider-aware rendering (ADR-PROMPT-ASSEMBLY-001)

`CompiledPromptArtifact` carries **structured slots** to the gateway. Each
provider adapter renders per vendor:

| Provider | Delimiter strategy | Long-context rule | Tool channel |
|----------|---------------------|---------------------|--------------|
| Anthropic (Claude 4.6+) | `<instructions>`, `<context>`, `<examples>`, `<thinking>`, `<document>/<document_content>/<source>`; role string → `system=` | Hoist C0 to top when ≥ threshold; tail-repeat task reminder | API `tools=` |
| OpenAI GPT-4.1 | Markdown headings: `# Role`, `# Instructions`, `# Context`, `# Examples`, `# Reasoning Steps`, `# Final instructions`; system + user roles | Keep order; append condensed I0+U0 as `# Final instructions` at tail | API `tools=` |
| OpenAI o-series (reasoning) | `developer` role for D0; optional `Formatting re-enabled`; avoid CoT prompts (reasoning is internal) | Same as GPT-4.1 | API `tools=` |
| Gemini 3 | Markdown + Identity/Constraints/Output sections; `thinking_level` via API; structured outputs via `response_schema` field | Instructions **after** data; anchor with "Based on the above…" | API `functionDeclarations` |

Replay determinism: `manifest_hash` is computed over the **structured slot
payload**, not the rendered string. Idempotency nonce (ADR-PA-002) is carried
alongside but excluded from hash inputs.

## 5. Security & Integrity

- **Injection neutralization** on `U0`:
  `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/security/assembly_injection_neutralizer.py`.
- **Slot integrity** — `validate_slot_order` rejects payloads that violate the
  canonical order; `validate_context_contract` enforces C0 shape.
- **Healer re-entry** — any `H0`-bearing payload passes `validate_healer_reentry`
  before assembly continues.
- **Airlock sanitization** — `AirlockAssembler._sanitize` strips hijack tokens
  (`[SYSTEM]`, `[ADMIN]`, `[ROOT]`, `[ESCALATE]`, `[BYPASS]`, `[OVERRIDE]`).
- **HMAC signing** — `CompiledPromptArtifact.signature = HMAC-SHA256(secret_key,
  canonical_slot_bytes)`. Verifiers reject unsigned or tampered artifacts.
- **Replay** — `replay_key`, `policy_hash`, `plan_id` sealed by
  `PromptEnvelope` at C0 → PA handoff; downstream must not mutate.

## 6. Invariants

1. **C0 produces envelope; PA consumes it.** No layer besides C0 writes to
   `PromptEnvelope` fields.
2. **Slot authority is hierarchical.** Lower-authority slots (C0, U0, Y0, H0)
   MAY NOT override higher-authority slots (S0, D0, I0).
3. **U0 is ZERO authority.** Injection neutralizer runs on every U0 before any
   gateway dispatch — no bypass.
4. **Response schema rides the API field**, never stringified into the prompt
   body (ADR-PROMPT-ASSEMBLY-001 Q4).
5. **Tool schemas ride the API `tools` field**, never inlined as prose.
6. **Assembly is deterministic.** Identical `PromptBOM` + `secret_key` + slot
   contents ⇒ identical `manifest_hash` and signature.
7. **Cache-prefix stability.** `S0 + D0 + I0` block order is stable across
   replays so provider prompt-caches hit (ADR-PROMPT-ASSEMBLY-002).
8. **Eviction is deterministic.** Same inputs + same budget ⇒ same post-trim
   slot payload (hash-stable).
9. **Thinking controls ride routing meta**, not the prompt body, where the
   provider supports a native `thinking_level` / interleaved-thinking channel.
10. **Envelope `abstain_recommended=True` short-circuits PA.** No assembly, no
    dispatch; route to HITL / refine.

## 7. Status of Rectification Work

| Concern | State | Reference |
|---------|-------|-----------|
| 10-slot taxonomy documented | ✅ this file | §2 |
| Code ↔ doc cross-links | ✅ this file | all sections |
| Provider-aware rendering | 📐 designed | ADR-PROMPT-ASSEMBLY-001 |
| `<document>` container + long-context reorder | 📐 designed | ADR-PROMPT-ASSEMBLY-001 Q3 |
| Structured outputs via API | 📐 designed | ADR-PROMPT-ASSEMBLY-001 Q4 |
| Grounding-in-quotes directive | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §3 |
| Agentic standing reminders (persistence/tool-first/plan-first) | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §4 |
| Model self-knowledge mixin | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §5 |
| Provider-aware tokenizer | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §6 |
| Conversation-history compressor | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §7 |
| Deterministic token-budget eviction | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §8 |
| Idempotency nonce | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §9 |
| Prompt-cache prefix discipline | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §10 |
| Thinking-depth knob on routing meta | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §11 |
| Tuning-context-reliance directive | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §12 |
| Parallel-tool-call caveat switch | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §13 |
| Apply-patch convention for code-editing agents | 📐 spec'd | ADR-PROMPT-ASSEMBLY-002 §14 |
| Provider-matrix golden tests | 📐 spec'd | `docs/reports/plans/prompt-assembly-gap-b4e1c2/test_plan_matrix.md` |

Legend: ✅ done · 📐 designed, implementation in queued wave · ⏳ active ·
❌ not started.

## 8. Related plans

- `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md` — gap parent plan
- `.windsurf/plans/prompt-assembly-reception-hardening-9c4e2b.md` — ADR-PA-001 execution
- `.windsurf/plans/prompt-assembly-few-shot-exemplars-9c4e2b.md` — E0 exemplars bank
