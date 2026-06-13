# Context Engineering Gap Analysis Plan

Perform a comprehensive context engineering gap analysis of the Agentic-Workflow repo against industry best practices, with special focus on ensuring subatomic (dumber/narrower) agents receive sufficient clarity and context in their prompts.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Findings Summary (from codebase exploration)

### What Exists Today

**Infrastructure (Strong)**
- `PromptAssembler` — XML semantic fencing with `SYSTEM_PRIME`, `CONTEXT_DATA`, `DIRECTIVES`, `NEGATIVE_CONSTRAINTS`, `OUTPUT_FORMAT` tags
- `InstructionalInjectionMixin` — 30 patterns across 6 layers (Framing, Context, Reasoning, Tooling, Safety, Output)
- `GoldenContextMixin` — anti-drift injection of SSOT rules into message lists after 10+ messages
- `ContextManagementMixin` — token tracking, priority-based pruning, overflow prevention
- `SubAtomicEngineImpl` — gateway-backed LLM calls with `resilient_mutation(prompt, system_prompt, fission_active)`
- 23 Jinja2 templates in `prompt_governance/templates/` with schema validation headers
- 19 meta-prompts in `prompt_governance/meta_prompts/`
- Agent spec JSON configs in `apps_lic/config/agent_specs.json` and `apps_rg/config/rg_agent_specs.json`

**Governance (Strong)**
- Prompt injection shielding (patterns 21-25)
- Input sanitization (XML/JSON)
- Template integrity checks
- Registry with content hashing

### Critical Gaps Identified

#### GAP-1: Subatomic Agents Lack Per-Agent System Prompts (SEVERITY: HIGH)
- **Finding**: `SubAtomicAgent` base class has no `system_prompt`, no `persona`, no `role_description` field. It's a bare stub with `execute()` that `pass`es and a `heal()` that returns `"skipped"`.
- **Impact**: When orchestrator dispatches to a subatomic agent, the agent has zero self-knowledge about what it is or what it should do. The LLM call in `SubAtomicEngineImpl.resilient_mutation()` takes an optional `system_prompt` kwarg, but nothing in the base class populates it.
- **Best Practice**: Every agent, especially dumber/narrower ones, needs a crisp identity prompt: role, capabilities, boundaries, expected I/O format.

#### GAP-2: No Agent-Level Prompt Card / Persona Registry (SEVERITY: HIGH)
- **Finding**: `agent_specs.json` files contain only operational config (temperatures, thresholds, keywords) — zero prompt instructions, persona definitions, or task descriptions. The `prompt_registry_config.json` maps only 2 templates. Most agents have no registered prompt.
- **Impact**: There is no single place to look up "what does this agent know about itself?" for any of the 149 active agents. Prompt construction is ad-hoc and scattered.
- **Best Practice**: Each agent should have a "prompt card" — a structured persona definition (role, goal, constraints, I/O schema, few-shot examples) that is loaded at instantiation.

#### GAP-3: InstructionalInjectionMixin Is Never Called in Production (SEVERITY: HIGH)
- **Finding**: `inject_framing_layer`, `inject_safety_layer`, `inject_all_layers`, and `prepare_messages_for_llm` are only referenced in test files. Zero production agent code calls these methods. The mixin is inherited but dormant.
- **Impact**: The entire 30-pattern instructional injection system is dead code in production. Agents don't get framing, safety, or output structure injections.
- **Best Practice**: Injection should be automatic (via base class `execute()` or gateway middleware), not opt-in.

#### GAP-4: Orchestrator→Agent Context Handoff Is Structural Only (SEVERITY: MEDIUM-HIGH)
- **Finding**: `ExecutionContext` carries `accumulated_context`, `metadata`, `call_path`, `depth`, `phase` — all structural orchestration data. It contains zero task-level context (what the agent should actually do, what data it should process, what the user's goal is).
- **Impact**: When `orchestrator_engine.run_agent()` dispatches to an agent, the agent receives execution plumbing but no semantic task context. The "Zero-Loss DNA Preservation" preserves predecessor chains but not task instructions.
- **Best Practice**: Context handoff should include: task description, input data, expected output format, upstream results summary, and any constraints.

#### GAP-5: SubAtomicEngineImpl Concatenates system_prompt+prompt Naively (SEVERITY: MEDIUM)
- **Finding**: `full_prompt = f"{system_prompt}\n\n{prompt}"` — raw string concatenation with no semantic fencing, no role separation, no XML structure. This bypasses the entire `PromptAssembler` infrastructure.
- **Impact**: The core LLM execution path for subatomic agents ignores the XML fencing, injection shielding, and template system that was purpose-built. Prompt injection defenses are circumvented.
- **Best Practice**: All LLM calls should route through `PromptAssembler.assemble()` or at minimum use the XML semantic fencing template.

#### GAP-6: GoldenContextMixin Only Injects Structural SSOT Rules (SEVERITY: MEDIUM)
- **Finding**: The golden context is a static string about base agent locations, layer hierarchy, depth rules, and forbidden patterns. It contains zero task-level reminders.
- **Impact**: Anti-drift protection only prevents structural hallucinations. It doesn't help agents remember their current task, user intent, or output requirements during long execution chains.
- **Best Practice**: Golden context should also inject task-specific anchors: current goal, success criteria, and output format reminders.

#### GAP-7: ContextManagementMixin Uses Heuristic Token Estimation (SEVERITY: MEDIUM)
- **Finding**: `estimate_tokens()` uses `len(text) // 4` — a rough heuristic. The `_create_summary()` method is a truncation stub (`content[:half]...[summarized]...content[-half:]`), not an LLM-powered summarizer.
- **Impact**: Token budgets are approximate; context may overflow or be under-utilized. Summaries lose semantic content.
- **Best Practice**: Use tiktoken for accurate counts (already referenced in comments but not implemented). Replace truncation with LLM-powered or extractive summarization.

#### GAP-8: No Few-Shot Examples in Agent Prompts (SEVERITY: MEDIUM)
- **Finding**: Template schema headers declare `optional_vars` but none of the 23 templates include few-shot examples. The `PromptAssembler` has an `examples` parameter but it's never populated in practice.
- **Impact**: Dumber agents that would benefit most from seeing 1-2 concrete input→output examples receive none. This is the single biggest lever for improving narrow agent accuracy.
- **Best Practice**: Every subatomic/worker agent should have 1-3 few-shot examples baked into its prompt card.

#### GAP-9: No Output Schema Enforcement at LLM Call Level (SEVERITY: MEDIUM)
- **Finding**: Jinja templates define `OUTPUT FORMAT (strict JSON only)` in prose, but there's no structured output mode (e.g., `response_format={"type": "json_object"}` for OpenAI, or Pydantic model extraction via Instructor). The `HardenedOpenAIExecutor` and `HardenedAnthropicExecutor` don't use structured output APIs.
- **Impact**: Agents may return malformed responses that fail downstream parsing. "Strict JSON only" in prompt text is a suggestion, not enforcement.
- **Best Practice**: Use provider-native structured output (OpenAI JSON mode, Anthropic tool use, Instructor/Pydantic extraction) for all agents with defined output schemas.

#### GAP-10: No Prompt Versioning or A/B Testing Infrastructure (SEVERITY: LOW)
- **Finding**: Templates have `VERSION: v1.0 (Auto)` in headers but no mechanism to version-control prompt changes, compare performance across versions, or roll back.
- **Impact**: Prompt improvements can't be measured or safely deployed.
- **Best Practice**: Prompt versioning with performance metrics tracking per version.

---

## Implementation Plan

### Phase 1: Agent Prompt Card System (addresses GAP-1, GAP-2, GAP-8)
1. Define a `PromptCard` dataclass: `role`, `goal`, `constraints`, `input_schema`, `output_schema`, `few_shot_examples`, `injection_layers` (which of the 30 patterns to activate)
2. Create `prompt_cards/` registry under `agentic_core/prompt_governance/` with one JSON/YAML card per agent
3. Add `prompt_card: PromptCard` field to `SovereignBaseAgent` loaded at `__post_init__` from registry
4. Start with the 6 canonical executors + 10 highest-traffic worker agents
5. Each card includes 1-3 few-shot examples

### Phase 2: Auto-Injection Pipeline (addresses GAP-3, GAP-5)
1. Create `PromptPipeline` middleware that sits between agent logic and LLM gateway
2. Pipeline auto-applies: agent's prompt card → framing injection → safety injection → context fencing → output schema → golden context
3. Refactor `SubAtomicEngineImpl.resilient_mutation()` to use `PromptAssembler.assemble()` instead of raw concatenation
4. Wire `HardenedOpenAIExecutor` and `HardenedAnthropicExecutor` through the pipeline

### Phase 3: Semantic Context Handoff (addresses GAP-4, GAP-6)
1. Extend `ExecutionContext` with `task_description: str`, `input_data: dict`, `expected_output_schema: dict`, `upstream_summary: str`
2. Add task-specific golden context injection (goal + success criteria + output format) alongside structural SSOT injection
3. Implement context compression: when handing off between agents, summarize upstream results into a concise brief

### Phase 4: Structured Output & Token Accuracy (addresses GAP-7, GAP-9)
1. Integrate tiktoken for accurate token counting in `ContextManagementMixin`
2. Replace truncation summarizer with extractive summarization
3. Add `response_format` / Instructor integration for agents with defined output schemas
4. Add output validation: parse agent response against declared schema, retry on failure

### Phase 5: Prompt Observability (addresses GAP-10)
1. Log assembled prompts with version hash to telemetry
2. Track token usage, response quality scores per prompt version
3. Add prompt diff tooling for safe iteration

---

## Priority Matrix

| Gap | Severity | Effort | Impact on Subatomic Agents | Phase |
|-----|----------|--------|---------------------------|-------|
| GAP-1 | HIGH | Medium | **Direct** — agents have no identity | 1 |
| GAP-2 | HIGH | Medium | **Direct** — no discoverable persona | 1 |
| GAP-3 | HIGH | Medium | **Direct** — injection system is dead | 2 |
| GAP-4 | MED-HIGH | Medium | **Direct** — no task context at dispatch | 3 |
| GAP-5 | MEDIUM | Low | **Direct** — bypasses safety fencing | 2 |
| GAP-6 | MEDIUM | Low | Indirect — drift protection is structural only | 3 |
| GAP-7 | MEDIUM | Low | Indirect — token budgets approximate | 4 |
| GAP-8 | MEDIUM | Medium | **Direct** — no examples for narrow agents | 1 |
| GAP-9 | MEDIUM | Medium | **Direct** — outputs unvalidated | 4 |
| GAP-10 | LOW | Medium | Indirect — no measurement | 5 |

## Artifact Location
Final report will be saved to `docs/reports/plans/context-engineering-gap-analysis.md` per Constitutional Rule #0.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

