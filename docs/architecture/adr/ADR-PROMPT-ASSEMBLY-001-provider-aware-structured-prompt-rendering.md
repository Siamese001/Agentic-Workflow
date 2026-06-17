# ADR-PROMPT-ASSEMBLY-001 — Provider-aware structured prompt rendering

- **Status**: Accepted (implemented; superseded in part by later prompt-assembly slot contract)
- **Decision Date**: 2026-04-23
- **Deciders**: Author-Gate Q1-Q4 resolved 2026-04-23 (user + Codex). Confidence band 0.88-0.93.
- **Impact Layers**: L0, L2, L4, L5, L_SHARED, L_TOOLS
- **Plan**: [`prompt-assembly-reception-hardening-9c4e2b.md`](../../../plans/archived-claude-archive__2026-05__prompt-assembly-reception-hardening-9c4e2b.md)
- **Historical Notion Registry**: `https://www.notion.so/Provider-aware-structured-prompt-rendering-34b27693f55c8136b834c1ce1908c144`
- **HITL Ledger rows**: Q1/Q2/Q3/Q4 Prompt Assembly decisions posted 2026-04-23.

Current-state note (2026-06-15): provider-aware adapter rendering and slot contracts are implemented in the prompt assembly/provider adapter path. The original 8-slot order has since been superseded in part by the later 10-slot prompt assembly contract (`S0-D0-M0-I0-E0-C0-Y0-U0-H0-R0`).

## Context

`AirlockAssembler.assemble_from_bom`
(`@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:343-346`)
flattens `S0 + D0 + I0 + C0` with `"\n\n".join(...)` into a single
`final_system_string`. The gateway
(`@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py:558-565`)
then passes `(final_system_string, final_user_string, allowed_tools_schema)` to
provider adapters. This erases slot structure before the LLM receives it and
makes compliance with current Anthropic (Claude Opus 4.7) and OpenAI (GPT-4.1,
o-series) prompting best practice architecturally impossible:

- No XML tagging per content type (Anthropic's single strongest recommendation).
- No instruction hierarchy (developer > system > user on OpenAI reasoning models).
- No `<example>` / `<examples>` wrapping of few-shot exemplars.
- No `<thinking>` scaffold channel.
- No `<document>`-wrapped RAG context.
- No per-provider long-context reordering.
- No structured-output (`response_format` / JSON schema) binding.

Scorecard: 22 of 30 best-practice techniques missing, 5 partial, 3 present.
Full cross-map: `@c:/Git/Agentic-Workflow/docs/reference/_primers/prompting/current_architecture_crossmap.md`.

Additionally, 5 of 9 SSOT prompt categories
(`@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt`)
lack a dedicated assembler slot: EXEMPLARS, META-COGNITIVE, SYNTHESIS, HEALING PROPOSAL;
DEPENDENCY is slotted but not `<document>`-wrapped.

## Decision

Adopt four coupled changes, locked via Author-Gate on 2026-04-23:

### Q1 — META-COGNITIVE slot shape (confidence 0.88)

Add a dedicated `M0` slot between `C0` and `U0`. New canonical order:

```
S0 → D0 → I0 → E0 → C0 → M0 → U0 → H0
```

`M0` carries CoT scaffolds, reasoning strategies, `<thinking>` / `<answer>`
output-shape instructions, and self-check prompts. Slot-order validator and
`GovernedPayload` schema extended.

**Rejected**: per-slot `thinking` attribute (conf 0.40) — breaks SSOT 1:1
category mapping and makes reception gates harder.

### Q2 — Provider-adapter contract (confidence 0.93)

`CompiledPromptArtifact` carries **structured slots** to the provider adapter.
Each adapter renders per vendor:

- **Anthropic adapter**: emit `<instructions>`, `<context>`, `<examples>`,
  `<thinking>`, `<document>/<document_content>/<source>`; set `system=<role>`.
- **OpenAI GPT-4.1 adapter**: split into `system` (S0+I0) + `user` (C0+U0);
  use markdown section headings (`# Role`, `# Instructions`, `# Context`,
  `# Examples`, `# Reasoning Steps`, `# Final instructions`).
- **OpenAI o-series adapter**: use `developer` role for D0; prepend
  `Formatting re-enabled` when AgentSpec declares `markdown_output=True`;
  avoid CoT prompts (reasoning is internal).

Replay-key determinism preserved by hashing the **structured slots**, not the
rendered string.

**Rejected**: status-quo flatten-at-assembler (0.25) caused the reception gap;
dual-contract (0.55) creates SSOT drift.

### Q3 — Long-context composition (confidence 0.89)

Per-provider adapter policy with shared **tail-repeat default** when
`C0_tokens >= context_token_threshold` (initial 8000, tune in W5):

- **Anthropic** (≥ threshold): hoist C0 to top, keep I0/M0 at original
  positions, append 1-line task reminder at tail.
- **OpenAI** (≥ threshold): keep order, append condensed I0 + U0 as
  `# Final instructions` block.

**Rejected**: assembler-level fixed reorder (0.55) ignores vendor-specific
optimal reorder; no-change (0.30) leaves ~30% quality on the table per
Anthropic long-context tests.

### Q4 — Structured-output schema source (confidence 0.90)

`AgentSpec` (one per app in `apps_*/config/agent_spec_config.py`) declares an
optional `response_schema: dict | None` field. `PromptBOMBuilder` reads it,
`CompiledPromptArtifact` carries it, provider adapters pass to vendor API as
`response_format` (OpenAI) or enforced tool_choice / JSON mode (Anthropic).

Dynamic output shapes: discriminated-union schemas, or governance-whitelisted
permissive schemas.

**Rejected**: caller-supplied schema (0.50) inverts capability authorization;
hybrid AgentSpec-default-with-caller-override (0.55) creates dual SSOT drift.

## Consequences

### Positive
- Every LLM call leaves the gateway provider-idiomatically rendered.
- Reception gates (`check_prompt_reception.py`, `check_xml_tag_coverage.py`,
  `check_response_schema_coverage.py`, `check_prompt_conflicts.py`) become
  implementable as CI guards.
- SSOT 9-category coverage rises from 4/9 to 9/9 (SYNTHESIS remains deferred
  to follow-on wave — see plan W6 DEFERRED_SCOPE).
- AgentSpec gains response_schema as a first-class capability-governance
  property, auditable by L5_safety.

### Negative / Risks
- `CompiledPromptArtifact` schema change ripples to all provider adapters
  (blast radius ~12 call sites).
- HMAC signature inputs change; a replay-key migration shim is required in
  W2.1 to preserve determinism across the boundary.
- Adapter LoC grows (~150 each); adapter-side bugs become a new risk surface.
- On Claude 4.6+ / Mythos Preview, prefill on the last assistant turn is
  deprecated (400 error). We never used prefill, so no migration is needed,
  but an anti-regression gate will forbid introducing it.

### Neutral
- Slot-order validator moves from 5-slot to 8-slot sequence.
- Manifest hash scheme migrates; historical replay traces remain valid for the
  old 5-slot order for 90 days per a migration window.

## Execution

Executed in 5 waves per
`plans/archived-claude-archive__2026-05__prompt-assembly-reception-hardening-9c4e2b.md`:

1. **W1** — Reception audit + gateway/assembler instrumentation.
2. **W2** — Structured `CompiledPromptArtifact`; Anthropic + OpenAI adapters.
3. **W3** — E0 / M0 / H0 slots added; validator and payload extended.
4. **W4** — Exemplar bank and ≥3-example assembly gate.
5. **W5** — AgentSpec response_schema + 4 CI gates + golden-replay tests.

## References

- Anthropic best practices (distilled): `docs/reference/_primers/prompting/anthropic_best_practices_2026.md`
- OpenAI best practices (distilled): `docs/reference/_primers/prompting/openai_best_practices_2026.md`
- Current-architecture cross-map: `docs/reference/_primers/prompting/current_architecture_crossmap.md`
- SSOT prompt categories: `docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt`
- Related: `agentic_process_mapping_v32.md` (overall L0-L6 mental model)
