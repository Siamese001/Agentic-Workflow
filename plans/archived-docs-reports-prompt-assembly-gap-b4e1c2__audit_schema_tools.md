---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\prompt-assembly-gap-b4e1c2\\audit_schema_tools.md'
original_relative_path: 'prompt-assembly-gap-b4e1c2\\audit_schema_tools.md'
source_sha256: fce317682d6706c9cbb0131e3191eb3151c61ce65ef6461ba4ae19a4ea99aaba
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W5 Audit — Response-schema & Tool-channel Discipline

**Plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
**Waves closed**: W5 phases 5.1, 5.2
**Scope**: Read-only audit. Determines whether every LLM call site routes
response schemas through the API `response_schema` / `response_format` field
(not stringified into prompt body) and tools through the API `tools=` field
(not inlined as prose).

**Method**: `grep_search` for literal occurrences of `response_schema`,
`response_format`, `tools=`, `tool_schema`, `allowed_tools` across
`agentic_core/` with manual inspection of matched files.

**Provenance**: `backend=grep, snapshot=working-tree 2026-04-23`.

---

## 1. Response-schema audit (G8)

### 1.1 Raw findings

| File | Matches | Shape | Verdict |
|------|--------:|-------|---------|
| `agentic_core/prompt_governance/core/prompt_assembler.py` | 8 | `PromptAssembler._last_response_schema`, `AssembledPrompt.response_schema` — schema is bound to assembled-prompt result object | **PASS (binding)** — schema is captured, not stringified into slot body |
| `agentic_core/L1_cognition/reasoning/query_planner.py` | 2 | Consumer — reads schema from routed plan to validate output | **PASS** |
| `agentic_core/evaluation/judges/openai_judge.py` | 2 | Passes `response_format={"type":"json_schema", ...}` to OpenAI API | **PASS** — uses native API field |
| `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py` | 1 | Consumer — reads schema from governance packet | **PASS** |
| `agentic_core/knowledge/enrichment/semantic_enricher.py` | 1 | Consumer | **PASS** |
| `agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py` | 1 | Consumer | **PASS** |
| `agentic_core/L2_execution/types/gateway_types.py` | 1 | Type declaration | **PASS** |
| `agentic_core/adg/extraction/visitors/core.py` | 3 | ADG-level metadata; not a gateway dispatch | **N/A** |

### 1.2 Gap confirmation

The binding path `AgentSpec.response_schema → PromptBOM → CompiledPromptArtifact
→ provider adapter → API response_format / response_schema` is **designed** in
ADR-PROMPT-ASSEMBLY-001 Q4 but **not yet uniformly implemented** in provider
adapters. The audit found:

- `openai_judge.py` uses the native `response_format` field correctly (already
  compliant).
- `SovereignLLMGateway.py` (primary dispatch) does **not** yet thread
  `response_schema` to the API layer — it is carried on
  `CompiledPromptArtifact` but not read by the gateway (pre-ADR-PA-001 state).
- No evidence of `response_schema` being stringified into `S0`/`I0`/`R0` slot
  bodies in production paths. The `PromptAssembler` legacy path writes schema
  into `output_format` string for a RESTART-mode template (`R0` text), but
  this is a pre-ADR-PA-001 fallback used only by a subset of callers.

**Action**: W5.1 audit outcome = gateway threading is the remaining gap.
Closure is scheduled in `prompt-assembly-reception-hardening-9c4e2b` plan
W2 (Anthropic + OpenAI adapters) and W5 (AgentSpec response_schema).

**Severity of residual gap**: **H** — confirmed, scoped, queued.

---

## 2. Tool-channel audit (G17, G22)

### 2.1 Raw findings

| File | Matches | Shape | Verdict |
|------|--------:|-------|---------|
| `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | 6 | `allowed_tools_schema` read from `CompiledPromptArtifact`; passed to provider client via `tools=` kwarg | **PASS** |
| `agentic_core/L2_execution/capability/registry_validator.py` | 6 | Capability registry validates tool schemas at load time, not injected into prompt | **PASS** |
| `agentic_core/L2_execution/reasoning/slot_assembly_engine.py` | 6 | Consumer of `allowed_tools`; does NOT inline tool text into slot bodies | **PASS** |
| `agentic_core/L2_execution/reasoning/action_node_core.py` | 5 | Consumer | **PASS** |
| `agentic_core/L2_execution/reasoning/compiled_artifact.py` | 2 | Type definition — `allowed_tools_schema: list` field | **PASS** |
| `agentic_core/L2_execution/reasoning/adaptation_orchestrator.py` | 3 | Consumer | **PASS** |
| `agentic_core/L2_execution/enforcement/UniversalWriteGateway.py` | 2 | Consumer on the write side; tool schemas ride the UWG envelope, not prompt body | **PASS** |

### 2.2 Gap confirmation

**No inline tool-schema text** detected in `S0`, `D0`, `I0`, `E0` slot content
or in any registry mixin (spot-checked under
`agentic_core/prompt_governance/registry/` and
`agentic_core/prompt_governance/meta_prompts/`). Tool schemas are correctly
carried on `CompiledPromptArtifact.allowed_tools_schema` and passed to the
provider API via `tools=`.

**Parallel-tool-calls switch (G22)**: **not yet implemented**. `AgentSpec` has
no `parallel_tool_calls: bool` field; gateway defaults to provider default
(True). Closure: ADR-PROMPT-ASSEMBLY-002 §13.

**Severity of residual gap**:
- G17: **PASS** — no defect.
- G22: **L** — spec'd in ADR-PA-002; minor behavior knob.

---

## 3. Summary table

| Gap | Audit verdict | Next-step owner |
|-----|--------------|-----------------|
| G8  (response_schema threading) | Gateway path not yet threaded; assembler binding correct | `reception-hardening` W2 + W5 |
| G17 (tool schemas via API) | **Clean** — all call sites compliant | none (closed) |
| G22 (parallel_tool_calls switch) | Not implemented; spec'd in ADR-PA-002 §13 | `prompt-assembly-gap-b4e1c2` W7 |

---

## 4. Methodology note

This audit used `grep_search` for literal-string confirmation only. It did
**not** perform dependency tracing (which would require ADG fan-in/fan-out
queries). Literal search is the correct tool here because the question is
"does this string appear inlined in slot content?" — a pattern-match task, not
a topology task.
