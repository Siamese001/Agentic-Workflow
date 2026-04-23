# Current Prompt Assembly vs Best Practice — Cross-Map

**Scope**: Map every Anthropic / OpenAI best-practice technique (as of 2026-04)
against the current agentic_core prompt assembly pipeline, and score the gap.

**Sources**:
- `@c:/Git/Agentic-Workflow/docs/reference/prompting/anthropic_best_practices_2026.md`
- `@c:/Git/Agentic-Workflow/docs/reference/prompting/openai_best_practices_2026.md`
- `@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt` (9-row SSOT)

**Reviewed artifacts**:
- `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:240-378` — `AirlockAssembler.assemble_from_bom`
- `@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py:558-565` — provider handoff
- `@c:/Git/Agentic-Workflow/agentic_core/runtime/config/instructional_injections.py` — pattern loader
- `@c:/Git/Agentic-Workflow/agentic_core/prompt_governance/contracts/compiled_artifact_types.py` — `CompiledPromptArtifact`

---

## 1. Current architecture summary

### 1.1 Slots

Defined in `GovernedPayload` and composed by `AirlockAssembler.assemble_from_bom`:

| Slot | SSOT category | Content | How assembled |
|---|---|---|---|
| `S0` | SYSTEM/STATE | System prompt / constitution | `TemplateRegistry.get_s0(hash)` or `s0_override` |
| `D0` | INJECTIONS | Role-fence policy | `TemplateRegistry.get_d0_fences(hash)` — rendered as `<D0>\n  fence1\n  fence2\n</D0>` |
| `I0` | INSTRUCTIONAL | Mixin capability text | Loop `registry.get_i0_mixin(id)` for sorted mixins, joined with `\n\n` |
| `C0` | DEPENDENCY | JIT-loaded context | `load_context_jit(trace_id, intent_class)` via Elevator Shaft |
| `U0` | USER | User prompt | Wrapped `<U0>\n{raw}\n</U0>`, then `AssemblyInjectionNeutralizer.neutralize` |

### 1.2 Final composition (the critical line)

```@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:343-346
        system_parts = [p for p in [s0_content, d0_content, i0_content, c0_content] if p]
        final_system = "\n\n".join(system_parts)
        final_user = u0_clean
```

### 1.3 Gateway handoff

```@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py:558-565
            response = self._circuit_breaker.call(
                provider_impl.generate,
                artifact.final_system_string,
                artifact.final_user_string,
                artifact.allowed_tools_schema,
                **reasoning_kwargs,
            )
```

**Observation**: The LLM sees exactly two strings plus a tools schema. All slot
structure is lost at this boundary. No provider-aware routing (Anthropic
`system=` param vs OpenAI `developer` role for o-series vs OpenAI `system` role
for GPT-4.1).

---

## 2. Gap matrix — Anthropic

Legend: ✅ present · ⚠️ partial · ❌ missing

| # | Anthropic practice | Status | Where it is / should be | Gap / fix |
|---|---|---|---|---|
| A1 | XML tag each content type (`<instructions>`, `<context>`, `<example>`) | ❌ | `assembly_stage.py:343-346` joins with `\n\n` | Rewrite composition to emit named XML blocks |
| A2 | `<example>` / `<examples>` wrapping of few-shot | ❌ | `GoldenContextMixin` output flows into I0 unwrapped | Add E0 slot with `<examples><example index="n">` structure |
| A3 | Role in `system` param | ⚠️ | S0 generic; no per-agent role block | Derive `<role>` from AgentSpec at assembly time |
| A4 | Long docs at TOP, queries at bottom | ❌ | Current order is `S0→D0→I0→C0→U0` (docs mid-prompt) | Add ordering policy: when `C0 > N tokens`, hoist to top AND repeat instructions at tail |
| A5 | `<document>` wrapping with metadata | ❌ | `load_context_jit` returns stringified object | C0 formatter should emit `<document index="n" source="..."><document_content>...</document_content></document>` |
| A6 | Quote-first for long docs | ❌ | No policy in any slot | Add as a META-COGNITIVE (M0) scaffold when C0 is large |
| A7 | Adaptive thinking passthrough | ❌ | `reasoning_kwargs` exists but no thinking param surfaced | Provider adapter needs `thinking={"type":"adaptive"}` + `effort` |
| A8 | `<thinking>` / `<answer>` output tags | ❌ | No output-shape steering | Add to M0 slot or output_format binding |
| A9 | Multishot with `<thinking>` inside examples | ❌ | No CoT-annotated exemplars | Exemplar schema should support `thinking` field |
| A10 | Self-check instruction | ❌ | Not emitted anywhere | Add to M0 as optional tail instruction |
| A11 | Context-awareness prompt (multi-window) | ❌ | Not emitted | Add to S0 for long-running agents |
| A12 | Positive instructions ("do X") not negative ("don't Y") | Unknown | Depends on YAML corpus content | Add linter over instruction YAML |
| A13 | Explicit `<default_to_action>` / `<do_not_act_before_instructions>` | ❌ | Not modeled | D0 fence extension |
| A14 | Prefill deprecation awareness (4.6+) | ❌ | No prefill channel exists anyway (moot) | N/A |
| A15 | Injection neutraliser on U0 | ✅ | `AssemblyInjectionNeutralizer` on line 340 | Keep |
| A16 | Slot-order validation | ✅ | `validate_slot_order(S0→D0→I0→C0→U0)` line 335 | Needs update when E0/M0/H0 added |

---

## 3. Gap matrix — OpenAI

| # | OpenAI practice | Status | Where it is / should be | Gap / fix |
|---|---|---|---|---|
| O1 | Instruction hierarchy: developer > system > user | ❌ | All of S0+D0+I0+C0 → single `final_system_string` | Provider adapter must split: D0 → developer, S0+I0 → system, C0 → context, U0 → user |
| O2 | Markdown `#` section headings as primary delimiter | ⚠️ | Depends on template content | Templates should use `# Role`, `# Instructions`, `# Context`, etc. |
| O3 | XML for nested examples | ❌ | Same as A2 | E0 slot with XML wrapping |
| O4 | Prompt skeleton: Role → Instructions → Reasoning → Output → Examples → Context → Final | ⚠️ | Partial: we have system, instructions, context; missing Reasoning + Output Format + Final reminder | Add M0 (Reasoning) + output_format binding + tail CoT reminder |
| O5 | Conflicting-instruction detection | ❌ | No checker | `check_prompt_conflicts.py` lint (later wave) |
| O6 | Context-reliance tuning ("only use external context" vs mixed) | ❌ | Not modeled | C0 prefix policy |
| O7 | Instructions at top AND bottom for long context | ❌ | Fixed order | Assembler option: `repeat_instructions=True` when C0 > threshold |
| O8 | Reasoning model prompting (simple, no CoT, zero-shot-first) | ❌ | Same prompt sent to all models | Model-family-aware prompt variant selection |
| O9 | Developer-role routing for o-series | ❌ | Provider adapter missing | Provider-specific adapters |
| O10 | `Formatting re-enabled` header for o-series when markdown desired | ❌ | Not emitted | Provider adapter |
| O11 | Structured Outputs (JSON schema binding) | ⚠️ | `allowed_tools_schema` exists; no response_format | Extend artifact with `response_format` |
| O12 | Persistence reminder ("keep going until fully resolved") | ❌ | Not emitted | S0 for agentic flows |
| O13 | Tool-call guidance ("ask if unsure, don't guess") | ❌ | Not emitted | I0 mixin for tool-using agents |
| O14 | `parallel_tool_calls=false` when parallel causes issues | ❌ | Not surfaced as knob | Provider adapter param |

---

## 4. SSOT 9-category coverage

From `Agentic Prompt Categories.txt`:

| # | SSOT Category | Slot today | Status |
|---|---|---|---|
| 1 | USER PROMPT (Intent) | U0 | ✅ |
| 2 | INSTRUCTIONAL (The Books) | I0 | ⚠️ unwrapped |
| 3 | INJECTIONS (Role Fencing) | D0 | ✅ (but text, not XML-rich) |
| 4 | EXEMPLARS (Golden Context) | Inside I0 | ❌ needs E0 |
| 5 | DEPENDENCY (Context Widening) | C0 | ⚠️ stringified, not `<document>`-wrapped |
| 6 | META-COGNITIVE (Internal Monologue) | — | ❌ no M0 |
| 7 | SYNTHESIS (Pattern Analysis) | — | ❌ no slot; `SynthesisMixin` bypasses assembler |
| 8 | SYSTEM/STATE (The Rulebooks) | S0 | ✅ |
| 9 | HEALING PROPOSAL (The Correction) | — | ❌ no H0 |

**5 of 9 categories are missing or mis-slotted.** The narrow plan at
`@c:/Git/Agentic-Workflow/.windsurf/plans/prompt-assembly-few-shot-exemplars-9c4e2b.md`
only addresses row 4 (EXEMPLARS).

---

## 5. Reception gap (the user's core concern)

> "I know the wiring is present but not convinced the agents can receive them and use them."

**Root cause**: the gateway boundary at
`@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py:558-565`
erases all slot structure by concatenating S0+D0+I0+C0 into one `final_system_string`.
The LLM has no way to distinguish constitutional policy (D0) from capability text
(I0) from RAG context (C0) — they arrive as an undifferentiated wall.

**Consequences**:

1. **No instruction hierarchy** — D0 policy cannot outrank I0 on OpenAI
   reasoning models because both live in the same role.
2. **No XML benefits** — Anthropic's single strongest recommendation is XML-wrap
   each content type; we XML-wrap only D0 (with a generic `<D0>` tag) and U0.
3. **No provider-aware routing** — the same blob goes to Claude Opus 4.7
   (wants `<instructions>`, `<context>`, `<examples>` XML) and to o-series
   (wants simple developer message, no CoT prompts, zero-shot).
4. **No CoT scaffolding** — category 6 (META-COGNITIVE) has no slot, so no
   consistent `<thinking>...</thinking>` scaffold reaches the model.
5. **No exemplar structure** — few-shot exemplars flow in as raw I0 text with
   no `<example>`/`<examples>` boundaries, reducing multishot effectiveness.

**Evidence-gathering next step (W1)**: instrument `SovereignLLMGateway.generate`
to log per-slot byte counts and presence, capture which categories arrive at
which providers in production, and quantify the empirical gap before rewriting.

---

## 6. Recommended 5-wave plan (replaces single-concern exemplars plan)

| Wave | Focus | Deliverable |
|---|---|---|
| **W1 Reception audit** | Instrument gateway + assembler; log per-slot metrics | Reception evidence report |
| **W2 Structural tagging** | Replace `\n\n`-join with named XML blocks; provider-aware adapters | Anthropic: `<instructions>`, `<examples>`, `<context>`, `<thinking>`. OpenAI: markdown headings + developer/system routing |
| **W3 Missing slots** | Add E0 (exemplars), M0 (meta-cognitive), H0 (healing); extend `GovernedPayload` + slot-order validator | Order becomes `S0 → D0 → I0 → E0 → C0 → M0 → U0 → H0` |
| **W4 Exemplar bank** | Original narrow plan scope: `GoldenContextMixin` bank, ≥3 examples, similarity selection, `<example index="n">` | Assembly gate rejects exemplar-eligible prompts with <3 |
| **W5 Reception gates + CI** | `check_prompt_reception.py`, `check_xml_tag_coverage.py`, `check_prompt_conflicts.py`; golden-replay test against Anthropic & OpenAI providers | Pre-commit + `run_contract_gates.py` integration |

---

## 7. Open questions (for Author-Gate if chosen)

1. Should M0 (meta-cognitive) be a separate slot, or attribute on other slots?
   Trade-off: separate slot is clean; attributes allow per-category scaffolds.
2. Should provider-specific prompt *variants* live in the YAML injection loader
   or in provider adapters? (Recommend: provider adapters receive the structured
   `CompiledPromptArtifact` with slots intact, not a flattened string — this
   reverses the current contract.)
3. When C0 is large, do we repeat I0 at the tail (OpenAI A4) or hoist C0 to top
   (Anthropic A4)? Both practices agree but implementation differs.
4. Structured Outputs: does the caller specify JSON schema at `PromptBOM` build
   time, or does it derive from AgentSpec? (Recommend: AgentSpec — aligns with
   capability governance.)
