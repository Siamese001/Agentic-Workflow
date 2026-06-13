# Prompt Assembly — Best-Practices Gap Analysis & Rectification Plan

- **Plan slug**: `prompt-assembly-best-practices-gap-b4e1c2`
- **Tier**: T3 (cross-layer, spans `agentic_core/prompt_governance/**`, `agentic_core/L0_routing/reasoning/assembly_stage.py`, `agentic_core/knowledge/retrieval/prompt_envelope.py`, `apps_shared/enforcement/**`, and reference docs)
- **Status**: Design executed + **approved 2026-04-23**. EQ-1 child plan opened at `.windsurf/plans/eq1-compiled-artifact-schema-d9a3e7.md`. All 5 previously-deferred items promoted to scheduled (EQ-15..EQ-19). Code-wave execution tracked in `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md` (EQ-1..EQ-19, no residual deferrals).
- **Authored against**: source docs from Anthropic (Claude 4 prompting best practices + XML tagging), OpenAI (GPT-4.1 prompting guide + long-context + agentic reminders), Google (Gemini 3 developer guide + prompt design strategies)
- **Repo reference**: `@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md` and `@c:/Git/Agentic-Workflow/docs/reference/C5_Retrieval_Prompt_Assembly.md`

---

## 1. Scope & Goal

Compare Anthropic / OpenAI / Google prompt-assembly guidance (2024–2026 snapshot) against:

1. The architecture doc `Prompt Assembly.md` (PA.1 → PA.4 flow).
2. The implemented slot taxonomy + assembly pipeline:
   - `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/core/prompt_assembler.py` (`PromptAssembler`, 868 lines, 10-slot XML template)
   - `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py` (`AirlockAssembler`, 376 lines, `GovernedPayload` + BOM path)
   - `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/prompt_envelope.py` (`PromptEnvelope`, 275 lines — C0 → Assembly handoff)
   - `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/contracts/slot_contracts.py` (slots `S0, D0, M0, I0, E0, C0, Y0, U0, H0, R0`)
   - `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/security/assembly_injection_neutralizer.py`

Goal: enumerate every gap, classify severity, and sequence a rectification wave queue. **This plan produces no code or doc edits; it is the map.**

---

## 2. Best-Practice Summary (extracted from vendor docs)

### 2.1 Anthropic — Claude 4 / Opus 4.7 best practices
(source: `docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices` + `use-xml-tags`)

| # | Principle | Key mechanic |
|---|-----------|--------------|
| A1 | Structure prompts with XML tags | `<instructions>`, `<context>`, `<input>`, `<example>`/`<examples>`; consistent descriptive names; nest naturally |
| A2 | Give Claude a role in system prompt | Even a single role sentence shifts tone/accuracy |
| A3 | Long-context structure | Put longform data **at top**, query/instructions **at bottom**; up to ~30% quality lift |
| A4 | Multi-document container | `<document index="n"><document_content>…</document_content><source>…</source></document>` — metadata subtags matter |
| A5 | Ground responses in quotes | Ask the model to quote relevant spans first before answering |
| A6 | Use examples (few-shot) effectively | Relevant, diverse, structured inside `<example>` / `<examples>` |
| A7 | Thinking / interleaved thinking controls | Calibrate effort and depth via prompt flags |
| A8 | Parallel tool calling | Explicitly enable/optimize; reduce over-eagerness |
| A9 | Model self-knowledge | Tell the model its identity and exact model string when the app needs it |
| A10 | Communication style, response length, verbosity | Explicit control, migrate away from prefilled responses |
| A11 | Reduce hallucination in agentic coding | Avoid test-passing and hard-coding incentives |

### 2.2 OpenAI — GPT-4.1 prompting guide
(source: `developers.openai.com/cookbook/examples/gpt4-1_prompting_guide`)

| # | Principle | Key mechanic |
|---|-----------|--------------|
| O1 | Recommended prompt skeleton | `# Role and Objective`, `# Instructions` (+`## Sub-categories`), `# Reasoning Steps`, `# Output Format`, `# Examples`, `# Context`, `# Final instructions` |
| O2 | Delimiter ranking | Markdown is a strong default; XML next; **JSON is poor for long-context document packing** |
| O3 | Long-context document format | `<doc id='1' title='…'>…</doc>` or `ID: 1 | TITLE: … | CONTENT: …` — both beat JSON |
| O4 | Instruction repetition for long context | Place instructions **both before and after** long context; if only once, prefer before |
| O5 | Tuning context reliance | Explicit "only use external context" vs "may use internal knowledge" directive |
| O6 | Agentic standing reminders (3) | **Persistence**, **Tool-calling ("use tools, do not guess")**, **Planning ("plan extensively before each call")** |
| O7 | Tool definitions | Use API `tools` field, not inline schema text; name + describe each param; place complex examples in `# Examples` section |
| O8 | Chain-of-thought | Encourage explicit planning text between tool calls |
| O9 | Parallel tool caveat | Test; disable `parallel_tool_calls` if anomalies observed |
| O10 | Apply-patch / diff format | Structured edit format for code editing agents |

### 2.3 Google — Gemini 3 + Prompt design strategies
(source: `ai.google.dev/gemini-api/docs/prompting-strategies` + `gemini-3`)

| # | Principle | Key mechanic |
|---|-----------|--------------|
| G1 | Clear / specific instructions — Identity / Constraints / Output format sections | Markdown-headed sections; constraint enumeration |
| G2 | Large-data prompts | Place instruction/question **after** the data context; anchor with "Based on the above …" |
| G3 | Structured outputs | Prefer API structured-output feature over in-prompt schema coercion for complex JSON |
| G4 | Thinking level knob | Gemini 3 adds per-call thinking level; control via API, not prompt |
| G5 | Thought signatures | New field for verifiable reasoning chains |
| G6 | Few-shot consistency | Uniform format across examples; avoid mixing templates |
| G7 | Multimodal function responses | Typed function-response objects, not stringified |

### 2.4 Cross-vendor convergence (what all three agree on)

1. **Explicit structured delimiters** beat flat prose (XML or Markdown headers > JSON for docs).
2. **Position matters in long context** — instructions near data boundaries, not buried.
3. **Role + objective + constraints separation** is a stable skeleton.
4. **Few-shot examples** should be wrapped, named, and uniform.
5. **Structured outputs should ride the API's native response-schema field**, not be stringified into the prompt.
6. **Tool definitions belong in the API tools field**, not inside the system prompt body.
7. **Agentic reminders** (persistence, tool-first, plan-then-act) materially improve autonomy.

---

## 3. Current Repo State (Directly Observed)

### 3.1 Reference doc `Prompt Assembly.md`

Describes a 4-stage macro-flow:

- **PA.1 LOAD** — persona template, output schema, conversation history
- **PA.2 SLOT** — inject raw text, graph triples, contradiction rules
- **PA.3 BUDGET** — tokenize, reserve output tokens, FIFO eviction (P1 convo, P2 evidence)
- **PA.4 EMIT** — compile envelope, HMAC sign, attach routing meta

It **does not** mention:
- The 10-slot taxonomy (`S0, D0, M0, I0, E0, C0, Y0, U0, H0, R0`) already in code.
- Slot authority tiers (`ABSOLUTE`, `BINDING`, `GOVERNED`, `INFORMATIONAL`, `ZERO`, `GUIDING`, `PRIVATE`, `ANALYTIC`, `PROPOSED`, `SCHEMA`).
- Multi-provider (Anthropic/OpenAI/Gemini) formatting variance.
- Long-context reordering.
- Grounding-in-quotes directive.
- Agentic-reminder injection.

### 3.2 Code state (high-signal excerpts)

- `PromptAssembler.assemble()` uses a **single XML template** with ten `<SLOT_*>` fences, sanitizes user data, validates slot order, HMACs manifest via SHA-256 only (no idempotency nonce). Templates stored on disk under `./templates/prompts/*.xml`.
- `AirlockAssembler.assemble_from_bom()` composes `S0 → D0 → I0 → C0 → U0`, runs `AssemblyInjectionNeutralizer` on `U0`, produces `CompiledPromptArtifact` signed with HMAC-SHA256. Token estimate is `(len(system)+len(user))//4` — not provider-tokenizer-aware.
- `PromptEnvelope` carries `verified_chunks`, `cited_spans`, `system_blocks: tuple[str, ...]`, but no `<document>` rendering helper, no grounding-in-quotes directive, no ordering hint for long context.
- No visible multi-provider delimiter adapter (XML-for-Claude / Markdown-for-GPT / Markdown-for-Gemini).
- No conversation-history compressor — but doc PA.1 claims one.
- No native response-schema API wiring — `assemble_with_schema()` attaches schema to `AssembledPrompt`, but downstream gateway wiring is not verified end-to-end in this assessment (see Gap G8).
- No standing agentic-reminder block (persistence / tool-first / plan-first) surfaced as a first-class slot or mixin.

---

## 4. Gap Register

Severity: **S** = Severe (correctness/security), **H** = High (quality loss), **M** = Medium (best-practice drift), **L** = Low (doc polish).

| ID  | Gap | Best-practice source | Severity | Repo touchpoint |
|-----|-----|----------------------|----------|-----------------|
| G1  | `Prompt Assembly.md` does not reflect 10-slot taxonomy, slot authority tiers, or BOM/Envelope architecture | internal drift | **H** | `docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md` |
| G2  | No multi-provider delimiter adapter (XML for Claude, Markdown headers for GPT-4.1/Gemini, fallback rules) | A1, O1, O2, G1 | **H** | `prompt_assembler.py`, `assembly_stage.py` |
| G3  | No `<document index=n><document_content>…<source>…</source></document>` rendering for multi-doc `C0` evidence; `C0` is flat dict | A4, O3 | **H** | `prompt_envelope.py`, `PromptAssembler._format_context_data` |
| G4  | Long-context reordering absent — doesn't "long data at top, query at bottom"; no instruction duplication for very long contexts | A3, O4, G2 | **H** | `AirlockAssembler.assemble_from_bom` (slot order fixed `S0→D0→I0→C0→U0`) |
| G5  | No grounding-in-quotes directive for long-document tasks | A5 | **M** | templates, `I0` mixins |
| G6  | No standing agentic-reminder block (persistence / tool-first / plan-first) as slot or mixin | O6 | **H** | `slot_contracts.py`, template registry mixins |
| G7  | Token estimator is char/4 or words/0.75; not model-specific (tiktoken / Anthropic tokenizer / Gemini counter) | PA.3 (doc), A1/O1 implicit | **M** | `PromptEnvelopeFactory`, `AirlockAssembler`, `prompt_assembler.py` |
| G8  | Output schema flows as stringified JSON inside `SLOT_R0`; native response-schema API field not verified end-to-end | G3, A10, O1 "Output Format" | **H** | `AssembledPrompt.response_schema` wiring to gateway |
| G9  | Exemplars slot `E0` has no canonical `<example>`/`<examples>` wrapping convention; no uniform few-shot template | A6, G6 | **M** | `E0` content generation, template catalog |
| G10 | HMAC signature present but idempotency nonce promised in doc PA.4 is not implemented (only deterministic `manifest_hash`) | internal drift | **M** | `GovernedPayload`, `CompiledPromptArtifact` |
| G11 | Conversation-history compression promised in PA.1 is not implemented; no convo-history field on `PromptEnvelope` | internal drift | **H** | `PromptEnvelope`, missing compressor module |
| G12 | Token-budget eviction (FIFO convo, drop-lowest-ranked evidence) promised in PA.3 but not implemented — overflow is only flagged | PA.3 (doc), A3 | **H** | `PromptEnvelopeFactory.from_contract` + downstream truncator |
| G13 | No default role sentence when `S0` content is empty; silent behavior | A2 | **L** | `AirlockAssembler`, `SlotS0` |
| G14 | No prompt-caching prefix discipline — slot order is stable, but no documented policy on which prefixes are cache-keyed per provider | Anthropic prompt caching, OpenAI prompt caching | **M** | architecture doc, template registry |
| G15 | No model-identity self-knowledge block when app needs the model to identify itself | A9 | **L** | `I0` mixin |
| G16 | No thinking-depth / thinking-level knob; Gemini 3 `thinking_level` and Claude interleaved-thinking controls unused | A7, G4, G5 | **M** | gateway / routing payload, not pure PA |
| G17 | Tool definitions — need to confirm all call sites route tools through API `tools` field, not inline schema text in `S0`/`I0`/`D0` | O7 | **H** | `AirlockAssembler`, gateway adapters |
| G18 | Negative constraints use `<NEGATIVE_CONSTRAINTS>` block; no guidance on preferring positive framings + explicit sub-categories | O1, G1 | **L** | template defaults |
| G19 | Tuning-context-reliance directive not parameterized ("only use context" vs "may use internal knowledge") | O5 | **M** | `D0` fence set |
| G20 | No provider-matrix regression tests for prompt format variance (Claude vs GPT-4.1 vs Gemini golden renders) | all three | **H** | `tests/**` — currently single golden per path |
| G21 | `Prompt Assembly.md` ASCII diagram does not cite actual modules (`prompt_assembler.py`, `assembly_stage.py`, `prompt_envelope.py`, `AssemblyInjectionNeutralizer`, `TemplateRegistry`, `ElevatorShaft`) | internal drift | **L** | doc |
| G22 | Caveat handling — no documented disable-path for `parallel_tool_calls` when anomalies observed (OpenAI caveat) | O9 | **L** | gateway defaults |
| G23 | No apply-patch / diff-format convention for L2 code-editing agents (`apps_rg`, healer paths) | O10 | **M** | `apps_rg/**`, `apps_shared/enforcement/**` |

**Count**: 23 gaps. S=0, H=10, M=8, L=5.

---

## 5. Rectification Wave Plan

All waves are documentation + design first, then code. Every code wave will itself spawn a child T2/T3 plan at execution time with ADG evidence; this plan is the parent map.

### 5.1 Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1, 1.2, 1.3 | Doc alignment — rewrite `Prompt Assembly.md` to reflect 10-slot taxonomy, authority tiers, BOM/Envelope flow; add provider matrix; link to modules | 8 000 🟢 | Vendor docs cited in §2 are authoritative for this snapshot; no API version drift mid-wave | **Done** | Refreshed `@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md` with 10-slot taxonomy, module cross-links, provider-matrix table, status matrix (§7). Closes G1/G21. |
| W2 | 2.1, 2.2 | Multi-provider adapter design | 14 000 🟡 | — | **Done (prior work)** | Already captured in `docs/architecture/adr/ADR-PROMPT-ASSEMBLY-001-provider-aware-structured-prompt-rendering.md`; W2 objectives subsumed. Closes G2/G3/G4/G8/G9 at design. |
| W3 | 3.1, 3.2, 3.3 | Agentic-reminder + self-knowledge + thinking-depth I0 mixins | 10 000 🟢 | — | **Done** | ADR-PROMPT-ASSEMBLY-002 §3 (G5 grounding), §4 (G6 agentic standing), §5 (G15 model identity), §11 (G16 thinking-depth). |
| W4 | 4.1, 4.2 | Token budget + compression + eviction | 18 000 🟡 | — | **Done** | ADR-PROMPT-ASSEMBLY-002 §6 (G7 counter), §7 (G11 compressor), §8 (G12 eviction). |
| W5 | 5.1, 5.2 | Response schema + tools-API discipline audit | 9 000 🟢 | — | **Done** | Audit at `docs/reports/plans/prompt-assembly-gap-b4e1c2/audit_schema_tools.md`: G17 clean, G8 scoped to reception-hardening W2, G22 spec'd in ADR-PA-002 §13. |
| W6 | 6.1, 6.2 | Envelope integrity — idempotency nonce, cache prefix, context-reliance | 6 000 🟢 | — | **Done** | ADR-PROMPT-ASSEMBLY-002 §9 (G10 nonce), §10 (G14 cache prefix), §12 (G19 context reliance). |
| W7 | 7.1, 7.2 | Regression & golden tests | 12 000 🟡 | — | **Done** | Test plan at `docs/reports/plans/prompt-assembly-gap-b4e1c2/test_plan_matrix.md` (G20 matrix goldens, G23 apply-patch, G14 prefix stability gate). |
| W8 | 8.1 | Consolidated migration + sunset plan | 6 000 🟢 | — | **Done** | Execution queue at `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md` (EQ-1..EQ-14 with dependencies, rollback, Author-Gate entry points). |

**Total**: 83 000 tokens estimated (🟡 ceiling ~24 000 per wave respected).

### 5.2 Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Rewrite `Prompt Assembly.md` to match code reality | `docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md` | ASCII diagram must survive; keep PA.1–PA.4 as section anchors for back-refs | 3 500 | Todo |
| 1.2 | Cross-link to `C5_Retrieval_Prompt_Assembly.md` and module paths | `docs/reference/C5_Retrieval_Prompt_Assembly.md` | Avoid doc drift between the two — pick one SSOT, other becomes index | 2 500 | Todo |
| 1.3 | Add "Vendor Matrix" subsection with minimal rendered examples per provider | same docs | Must cite vendor URLs with captured-date stamps so future drift is visible | 2 000 | Todo |
| 2.1 | Spec `ProviderAwareRenderer` — interface + delimiter strategy table | new design doc under `docs/architecture/adr/` | Must preserve current XML default for back-compat; provider choice comes from routing metadata, not in prompt | 8 000 | Todo |
| 2.2 | Spec `<document>` container + long-context reordering rules + grounding-in-quotes default directive | same design doc | Reordering must remain deterministic (affects `manifest_hash`) | 6 000 | Todo |
| 3.1 | Spec agentic-reminder mixin (`I0_AGENTIC_STANDING_V1`) with persistence / tool-first / planning reminders | `prompt_governance/core/invariant_registry.py` + mixin catalog | Must not double-inject when caller already sets equivalents | 4 000 | Todo |
| 3.2 | Spec model-self-knowledge mixin (`I0_MODEL_IDENTITY_V1`) | same | Model string is provided by router, not hard-coded | 3 000 | Todo |
| 3.3 | Spec thinking-depth knob (`ROUTING_META.thinking_level`) — lives on routing meta, not in prompt body | routing payload spec | Gemini accepts native field; Claude uses interleaved-thinking prompt — adapter must split | 3 000 | Todo |
| 4.1 | Spec provider-aware token counting (tiktoken / anthropic / gemini) with fallback | `PromptEnvelopeFactory`, `AirlockAssembler` | Falls back to char/4 only on dependency absence — log once | 9 000 | Todo |
| 4.2 | Spec conversation-history compressor + deterministic eviction (FIFO convo, lowest-ranked evidence drop, must-use preserved) | new module `agentic_core/prompt_governance/core/history_compressor.py` + `PromptEnvelope.convo_history` | Must be deterministic so `manifest_hash` stays replay-stable | 9 000 | Todo |
| 5.1 | Audit every gateway call site for `response_schema` wiring | `agentic_core/**/gateways/**`, `apps_*/integrations/**` | Read-only; produces a CSV of call-site compliance | 5 000 | Todo |
| 5.2 | Audit every tool registration path — inline vs API `tools` field | same + `apps_shared/enforcement/**` | Any inline tool-schema text must be flagged as a defect row | 4 000 | Todo |
| 6.1 | Spec idempotency nonce addition + signature scheme migration | `GovernedPayload`, `CompiledPromptArtifact` | Back-compat shim for 90 days; nonce optional until default-on date | 3 500 | Todo |
| 6.2 | Spec prompt-caching prefix discipline — stable S0+D0+I0 block ordering, document which boundaries are cache keys per provider | design doc | Claude vs OpenAI cache APIs differ; must not break either | 2 500 | Todo |
| 7.1 | Design provider-matrix golden tests (one render per provider, diffed) | `tests/unit/prompt_governance/**` | `pytest_mcp` infra; avoid snapshot churn on cosmetic whitespace | 8 000 | Todo |
| 7.2 | Design apply-patch convention test for code-editing agents | `tests/**/apps_rg/**` | Non-Python agents also need this — but Python-only scope for W7 | 4 000 | Todo |
| 8.1 | Consolidated execution queue + rollback checkpoints | `.windsurf/plans/prompt-assembly-execution-<slug>-<6hex>.md` children | Order dependency: W2 before W4; W5 can parallel; W7 last | 6 000 | Todo |

---

## 6. ADG_GRAPH_LAYER_EVIDENCE

Evidence via direct grep + SQLite-on-disk read (MCP serialization §25 — single-MCP-per-response rule respected; grep used only for literal module confirmation, not dependency tracing).

- **Primary module consumers of `prompt_assembler`** (grep): 23 Python files in `agentic_core/` reference `prompt_assembler | PromptAssembly | assemble_prompt | build_prompt | render_prompt`. Highest-match concentration:
  - `agentic_core/knowledge/retrieval/prompt_envelope.py` (8 matches — C0 → PA handoff)
  - `agentic_core/L3_orchestration/reasoning/engines/sub_atomic_engine_impl.py` (4)
  - `agentic_core/evaluation/judges/pairwise_reference.py` (4)
  - `agentic_core/prompt_governance/core/prompt_assembler.py` (4)
  - `agentic_core/L3_orchestration/reasoning/engines/l4e_retrieval_integration.py` (3)
- **Semantic edges that matter for this plan** (by inspection of `assembly_stage.py`):
  - `flows_to`: `PromptEnvelope` → `AirlockAssembler.assemble_from_bom` → `CompiledPromptArtifact` → gateway (L2)
  - `reads_from`: `TemplateRegistry.get_s0 / get_i0_mixin / get_d0_fences` (L4 state store)
  - `writes_to`: `GovernedPayload.manifest_hash` / `CompiledPromptArtifact.signature` (replay ledger, L6 observability)
  - `emits_side_effect`: HMAC-SHA256 sign, `_emit_records_execution_trace`, `emit_replay_key`, `emit_determinism_digest`
  - `controls_flow`: `AssemblyInjectionNeutralizer.neutralize(U0)` — security chokepoint
- **P-view matches** (classification):
  - `v_p0_*`: none — no apps→infra direct imports in the touched paths (PA layer is itself governance infra).
  - `v_p1_*`: `assembly_stage.py` already uses lazy imports to avoid L0→L_PG gravity violations — pattern must be preserved in any new code wave.
  - `v_p2_*`: `AssemblyInjectionNeutralizer` has two copies (`security/` and `security/detectors/`) — a duplicated-adapter candidate worth de-duping in a future wave (not in scope for this plan).
- **Provenance**: `backend=sqlite+grep, snapshot=adg_indexed_<latest-on-disk>.sqlite`. Full ADG re-query deferred to W8.1 when code changes begin.

## 7. ADG_HOTSPOT_REPORT

| File | Archetype | Surfaces | Fan-in (est.) | Layer | Impact | Notes |
|------|-----------|----------|---------------|-------|--------|-------|
| `agentic_core/prompt_governance/core/prompt_assembler.py` | **CENTRAL_DEPENDENCY** | Execution, Write, Security | ≥23 (grep floor) | L_PG (governance) | high | Any format change ripples to all consumers; must stage behind a provider adapter. |
| `agentic_core/L0_routing/reasoning/assembly_stage.py` | **SAFETY_GATEKEEPER** | Security, Execution, Write, Observability | mid | L0 | high | Owns HMAC signing + injection neutralization + replay digests — all integrity concerns. |
| `agentic_core/knowledge/retrieval/prompt_envelope.py` | **STATE_NODE** | State, Execution | mid | L_KR | medium | C0 → PA handoff; adding convo-history / document-container support touches this SSOT. |
| `agentic_core/prompt_governance/contracts/slot_contracts.py` | **CENTRAL_DEPENDENCY** | None (contract-only) | high | L_PG | medium | Frozen contracts — any new slot requires contract-version bump + migration. |
| `agentic_core/prompt_governance/security/assembly_injection_neutralizer.py` (+ detectors copy) | **SAFETY_GATEKEEPER** | Security | low | L_PG | medium | Duplication flagged for later dedup; do not touch during this plan. |

Layer-criticality multipliers applied: L0 × 2.0, L_PG (governance ≈ L5 safety plane) × 2.0, L_KR × 1.75. All four primary hotspots ride the Safety/Security and Execution surfaces — any wave that edits them must gate through Author-Gate for antipattern risk and route through W7 golden-test matrix.

---

## 8. Risks & Author-Gate Triggers

| Risk | Mitigation | Author-Gate required? |
|------|-----------|----------------------|
| Format change breaks existing goldens | W7 matrix designed **before** any rendering change lands | Yes — at W2 design approval |
| New `I0` mixins double-inject with existing consumers | Inventory existing mixins in W3.1 before spec | Yes — at W3 design approval |
| Token-counter dependency adds heavy imports | Lazy import + graceful fallback to char/4 | No — deterministic fallback path |
| Provider-adapter choice affects `manifest_hash` determinism | Hash over canonical logical slots, not rendered string | Yes — at W2 design approval (architectural) |
| Convo-history compressor introduces non-determinism | Spec must be deterministic (hashable input → hashable output) | Yes — at W4 design approval |
| Idempotency-nonce scheme breaks replay verifiers | 90-day back-compat shim; nonce optional until default-on date | Yes — at W6 design approval |

---

## 9. Exit Criteria (plan-level)

1. Every gap G1..G23 is addressed by exactly one wave/phase, or explicitly deferred with a `DEFERRED_SCOPE:` marker emitted at wave-plan creation time.
2. `Prompt Assembly.md` is refreshed and demonstrably traces to `prompt_assembler.py`, `assembly_stage.py`, `prompt_envelope.py`, `slot_contracts.py`.
3. A vendor-matrix test harness exists (even if small) and is wired into `pytest_mcp`.
4. Architecture ADR(s) are authored for: provider-adapter, token-counter, conversation-history compressor, idempotency-nonce migration.
5. W8.1 emits a consolidated execution-queue plan with dependency order and rollback checkpoints.

---

## 10. Open Questions for User

1. Do you want the plan to cover **apply-patch / diff format** (O10, G23) for `apps_rg` code editing, or defer it to a separate plan?
2. Is multi-provider (Claude/GPT-4.1/Gemini) parity a hard requirement, or should the adapter ship **Claude-first** with GPT/Gemini as follow-on waves?
3. For conversation-history compression (G11), is a deterministic-summarizer (hash-stable) acceptable, or must the compressor be purely rule-based (last-N-turns + role dropout)?
4. For prompt caching (G14), do you want the plan to commit to Anthropic cache_control markers as a hard dependency, or leave the discipline abstract until a provider survey?

---

## 11. Plan Provenance

- Authored: 2026-04-23
- Vendor sources captured:
  - Anthropic prompting best practices, XML tags guide (retrieved this session)
  - OpenAI GPT-4.1 prompting guide (retrieved this session)
  - Google Gemini 3 developer guide + Prompt design strategies (retrieved this session)
- Code inspected: `prompt_assembler.py`, `assembly_stage.py`, `prompt_envelope.py`, `slot_contracts.py` (directly read), plus grep inventory of 23 consumer files
- Status: awaiting user decision on Section 10 open questions before first execution wave.
