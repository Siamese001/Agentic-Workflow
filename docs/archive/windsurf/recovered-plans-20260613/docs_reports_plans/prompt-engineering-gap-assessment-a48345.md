# Prompt Engineering Gap Assessment — Agentic Architecture

Comprehensive gap analysis of the agentic architecture's prompt engineering practices against industry best practices, covering all major prompt technique categories with detailed findings and recommendations.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The architecture has **strong foundational infrastructure** — a 30-pattern instructional injection system, XML semantic fencing, a prompt governance CMS with versioning, and adversarial red-team templates. However, several critical gaps exist in **injection defense depth, few-shot/multi-shot implementation maturity, observability instrumentation, and output validation enforcement**. This report identifies 28 findings across 8 categories with severity ratings and actionable recommendations.

---

## Scope & Methodology

**Files Assessed** (primary):
- `agentic_core/prompt_governance/` — assembler, renderer, governance hub, security, meta-prompts
- `agentic_core/config/core/injection_layer_config.py` — 30 instructional patterns
- `agentic_core/mixins/instructional_injection_mixin.py` — mixin delivery system
- `agentic_core/runtime/config/prompt_injection_loader_config.py` — runtime injection engine
- `agentic_core/L5_safety/enforcement/input_validation_guardrail.py` — guardrails
- `agentic_core/L0_routing/scripts/reasoning.py` — reasoning strategies
- `agentic_core/L1_cognition/` — CognitiveNode, ReAct engine, prompts_util
- `agentic_core/L4_state/utils/rag_enhancement_util.py` — few-shot injector
- `apps_shared/validators/resume_prompts_validator.py` — domain prompt templates
- `apps_shared/types/prompt_optimizer_types.py` — optimizer types
- `data/prompt_governance/` — YAML injection configs, evaluations, governance
- `data/golden/prompt_injection_attacks_200.jsonl` — adversarial test dataset

**Best-Practice Framework**: OWASP LLM Top 10, OpenAI prompt engineering guide, Google DeepMind prompt security, Anthropic constitutional AI patterns, academic literature (CoT, ToT, ReAct, Self-Consistency, RLHF alignment).

---

## Category 1: Prompt Injection Defense

### What Exists
- **InjectionDetector** (`prompt_governance/security/injection_detector.py`): 6-phrase keyword blocklist
- **InputValidationGuardrail** (`L5_safety/enforcement/input_validation_guardrail.py`): 5 regex patterns for injection detection
- **PromptAssembler** (`prompt_governance/core/prompt_assembler.py`): XML semantic fencing with `InputSanitizer`, untrusted data tagging
- **GovernanceHub** (`prompt_governance/core/governance_hub.py`): Pipeline: injection scan → PII scrub
- **Adversarial templates**: `cot_jailbreak.jinja`, `encoded_payload_base64.jinja`, `encoded_payload_leetspeak.jinja`
- **Golden dataset**: `prompt_injection_attacks_200.jsonl` (200 attack vectors)
- **Instructional Pattern #21**: Prompt-Injection Shielding Layer
- **Instructional Pattern #22**: Data vs Instruction Separation

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 1.1 | **Blocklist is trivially bypassable** | CRITICAL | `InjectionDetector` has only 6 static phrases. Typos, synonym substitution, unicode homoglyphs, multi-language attacks, and indirect jailbreaks all bypass it. Comment in code acknowledges: "Phase 5 adds model-based checks" — but Phase 5 doesn't exist yet. |
| 1.2 | **No model-based injection classification** | HIGH | No ML/LLM-based classifier to detect semantic injection attempts. Regex/keyword is necessary but insufficient per OWASP LLM01. |
| 1.3 | **Indirect prompt injection unaddressed** | HIGH | No defense against injections embedded in RAG-retrieved documents, tool outputs, or multi-hop context. The `UNTRUSTED DATA` wrapping (Pattern #6) is instructional only — LLMs can still follow injected instructions from data blocks. |
| 1.4 | **No encoding/obfuscation detection at runtime** | HIGH | Adversarial templates exist for base64 and leetspeak testing, but `InjectionDetector.scan()` doesn't decode or normalize these encodings before checking. Attacks using unicode, ROT13, base64, or character substitution pass through. |
| 1.5 | **Output injection not validated** | MEDIUM | `GovernanceHub.validate_output()` only scrubs PII from LLM output. No check for the LLM echoing injected instructions, leaking system prompts, or producing harmful content. |
| 1.6 | **Semantic fencing relies on LLM compliance** | MEDIUM | XML tags (`<CONTEXT_DATA>`, `<DIRECTIVES>`) are a best practice but ultimately depend on the LLM honoring boundaries. No runtime verification that output respects fence boundaries. |

### Recommendations
- **R1.1**: Expand blocklist to 200+ patterns including multilingual, unicode-normalized, and synonym variants. Reference OWASP LLM01 pattern library.
- **R1.2**: Implement a lightweight classifier (fine-tuned distilbert or similar) as a pre-flight check before prompt assembly. Route suspicious inputs to enhanced scrutiny.
- **R1.3**: Add content-security scanning for RAG-retrieved chunks and tool outputs before they enter prompt context. Tag all external content with provenance metadata.
- **R1.4**: Add decoding pipeline (base64, URL encoding, unicode normalization, leetspeak) before injection scanning.
- **R1.5**: Implement output guardrails: system prompt leakage detection, harmful content classification, instruction echo detection.
- **R1.6**: Add post-response validation that checks whether output references fence-boundary content inappropriately.

---

## Category 2: System Prompt Architecture

### What Exists
- **PromptAssembler**: XML-structured system prompts with `<SYSTEM_PRIME>`, `<CONTEXT_DATA>`, `<DIRECTIVES>`, `<OUTPUT_FORMAT>`
- **SovereignPromptRenderer**: Jinja2 templating with `StrictUndefined`, schema validation headers
- **Prompt Registry CMS** (`apps_shared/config/prompt_registry_config.py`): Categorized templates with versioning
- **PromptVersionManager** (`data/prompt_governance/versioning/PromptTemplate.py`): Semantic versioning, env tagging (dev/staging/prod), rollback
- **Prompt Manifest** (`data/prompt_governance/registry/prompt_manifest.yaml`): Central index with security settings

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 2.1 | **System prompts not cryptographically protected** | MEDIUM | No hash/signature verification that system prompts haven't been tampered with at runtime. `prompt_manifest.yaml` declares audit_logging but no integrity checking. |
| 2.2 | **No prompt A/B testing infrastructure** | MEDIUM | PromptVersionManager supports versioning and rollback but has no experimentation framework for comparing prompt variants against quality metrics. |
| 2.3 | **Template variable injection risk** | MEDIUM | `PromptTemplate.render()` uses simple string `.replace()` without escaping. If a template variable value contains `{another_var}`, it could cause unintended substitution in a second pass. |
| 2.4 | **Prompt registry has zero entries** | LOW | `prompt_index.yaml` shows `total_prompts: 0` and all category counts are 0. The registry infrastructure exists but isn't populated — prompts live in scattered Python files instead. |
| 2.5 | **No prompt length/token budget enforcement** | MEDIUM | `PromptOptimizer.compress_prompt()` uses `len(prompt) // 4` for token estimation — this is very rough. No integration with actual tokenizer or model context window limits. |

### Recommendations
- **R2.1**: Add SHA-256 hash verification for system prompts at load time. Store hashes in manifest.
- **R2.2**: Build A/B framework that can route traffic to prompt variants and measure output quality deltas.
- **R2.3**: Use Jinja2 for all rendering (already available via SovereignPromptRenderer) instead of manual `.format()`/`.replace()`. Jinja2 handles escaping properly.
- **R2.4**: Migrate scattered prompt definitions in Python files to the registry CMS. Priority: `resume_prompts_validator.py` (715 lines of inline prompt logic).
- **R2.5**: Integrate `tiktoken` or model-specific tokenizer for accurate token counting and enforce hard limits per model's context window.

---

## Category 3: Few-Shot / Multi-Shot Prompting

### What Exists
- **FewShotInjector** (`L4_state/utils/rag_enhancement_util.py`): Basic add/get/inject for examples
- **prompts_util.py** (`L1_cognition/utils/prompts_util.py`): 13 hardcoded few-shot strings (refactoring, imports, style, safety, concurrency, hygiene, testing, strategy, reflection, sherlock, gitops, property tests, historian)
- **PromptOptimizer.format_prompt()**: Prepends examples before user prompt
- **Macro ToT** in `resume_prompts_validator.py`: Multi-draft generation with variation instructions
- **PromptAssembler**: `examples` parameter in assembly (optional, passed through)

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 3.1 | **Few-shot examples are static and hardcoded** | HIGH | `prompts_util.py` has 13 inline string constants. No mechanism to dynamically select examples based on task similarity, user context, or domain. |
| 3.2 | **FewShotInjector has no semantic retrieval** | HIGH | `get_relevant_examples()` just returns the first N examples — no embedding-based similarity matching. This defeats the purpose of dynamic few-shot selection. |
| 3.3 | **No example quality validation** | MEDIUM | No mechanism to validate that few-shot examples are correct, current, and representative. Stale examples degrade output quality. |
| 3.4 | **No multi-shot escalation pattern** | MEDIUM | System lacks a progressive escalation from zero-shot → few-shot → many-shot based on task complexity or initial failure. |
| 3.5 | **Examples not versioned alongside prompts** | LOW | Few-shot examples in `prompts_util.py` are not managed by the PromptVersionManager — they drift independently from prompt templates. |

### Recommendations
- **R3.1**: Store few-shot examples in a searchable vector store (e.g., ChromaDB, already used elsewhere). Select examples via embedding similarity to the current query.
- **R3.2**: Implement semantic retrieval in `FewShotInjector.get_relevant_examples()` using the existing RAG infrastructure.
- **R3.3**: Add golden-set validation: each few-shot example should have expected output and be regression-tested.
- **R3.4**: Implement adaptive shot selection: start zero-shot, escalate to few-shot on low-confidence or failed validation, escalate to many-shot for persistent failures.
- **R3.5**: Register few-shot examples as versioned assets in the prompt registry CMS.

---

## Category 4: Chain-of-Thought / Reasoning Patterns

### What Exists
- **ReasoningStrategyFactory** (`L0_routing/scripts/reasoning.py`): 7 strategies — CoT, ToT, ReAct, Reflection, Critique, MultiPath
- **ReActEngine** (`L1_cognition/config/react_config.py`): Think→Act→Observe loop, max steps, self-reflection
- **CognitiveNode** (`L1_cognition/engines/CognitiveNode.py`): Adaptive strategy selection via weighted bias
- **Instructional Pattern #14**: Reason-Then-Answer Structure
- **Instructional Pattern #12**: Self-Consistency / Multi-Branch Thinking
- **ReasoningMode enum**: REACT, COT, TOT, SELF_CONSISTENCY, SHOTGUN
- **Macro ToT**: Tree-of-Thought draft generation with evaluator scoring and synthesis

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 4.1 | **Reasoning strategies are skeleton implementations** | HIGH | All strategies in `reasoning.py` generate placeholder strings like `"Step {i+1}: Analyze aspect of '{problem}'"` — they don't actually construct LLM prompts with CoT/ToT instructions. They're framework scaffolding, not functional reasoning. |
| 4.2 | **No structured CoT output parsing** | MEDIUM | No parser extracts and validates intermediate reasoning steps from LLM output. The system generates CoT instructions but can't verify the model actually followed them. |
| 4.3 | **Self-Consistency declared but not implemented** | HIGH | `ReasoningMode.SELF_CONSISTENCY` exists in the enum but has no corresponding strategy class in the factory. The multi-branch Pattern #12 injects instructions but doesn't implement the voting/consensus mechanism. |
| 4.4 | **No reasoning trace persistence** | MEDIUM | `ReActTrace` data class exists but no storage backend. Reasoning traces are generated in-memory but lost after execution — no audit trail for debugging or improvement. |
| 4.5 | **Strategy selection is random-weighted** | MEDIUM | `CognitiveNode._biased_select()` uses `random.random()` for strategy selection. No feedback loop from outcome quality to strategy weights. Strategy effectiveness is never measured. |

### Recommendations
- **R4.1**: Convert skeleton strategies into actual prompt construction functions that emit proper CoT/ToT/ReAct prompts for the target LLM.
- **R4.2**: Implement structured output parsing that extracts reasoning steps, validates logical coherence, and detects reasoning failures.
- **R4.3**: Implement SelfConsistencyStrategy: generate N responses with temperature sampling, extract answers, select majority answer.
- **R4.4**: Persist reasoning traces to structured storage for debugging, quality analysis, and strategy optimization.
- **R4.5**: Implement bandit-style adaptive strategy selection based on measured outcome quality (e.g., Thompson sampling over strategy success rates).

---

## Category 5: Instructional Prompt Patterns

### What Exists
- **30 Instructional Patterns** across 6 layers (Framing, Context, Reasoning, Tooling, Safety, Output) — well-designed, documented in both code and YAML
- **InstructionalInjectionMixin**: Provides layer-based injection to all agents
- **PromptInjectionLoader**: Runtime matching and application of injection patterns by hop_type/stage/context
- **Modular YAML configs** (`data/prompt_governance/injections/modular/`) for each layer
- **Reinforced constraints** (`build_generation_prompt_with_reinforced_constraints`): Progressive constraint escalation across retries

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 5.1 | **No telemetry on which patterns are used** | MEDIUM | Patterns have an `enabled` flag but no usage tracking. Can't measure which patterns improve output quality vs. add noise. |
| 5.2 | **Pattern effectiveness unmeasured** | HIGH | No A/B comparison or ablation study infrastructure. Adding all 30 patterns simultaneously makes it impossible to know which ones help. |
| 5.3 | **Pattern ordering not optimized** | MEDIUM | `inject_all_layers()` applies patterns in fixed layer order. Research shows prompt ordering significantly affects LLM output quality — no optimization tested. |
| 5.4 | **Progressive constraint escalation is domain-specific** | LOW | `build_generation_prompt_with_reinforced_constraints()` is a good pattern but only implemented for resume word-count constraints. Not generalized. |
| 5.5 | **Mixin opt-in is implicit** | LOW | Agents inherit `InstructionalInjectionMixin` but there's no enforcement that safety-critical agents actually call `inject_safety_layer()`. |

### Recommendations
- **R5.1**: Add telemetry counters for each pattern application (pattern_id, agent, outcome).
- **R5.2**: Implement ablation testing: run prompts with/without specific patterns and measure quality delta.
- **R5.3**: Test alternative orderings (e.g., safety-first, output-last) and measure effect on output quality.
- **R5.4**: Generalize progressive constraint reinforcement as a reusable pattern across all domains.
- **R5.5**: Add a `@requires_safety_injection` decorator that enforces safety layer injection for L5-classified agents.

---

## Category 6: Output Validation & Structured Generation

### What Exists
- **Instructional Pattern #26**: Strict JSON-Only Output Mode
- **Instructional Pattern #27**: Schema Enforcement & Examples
- **Instructional Pattern #28**: Stability Contracts
- **Instructional Pattern #29**: Error Envelope Normalization
- **PromptAssembler**: Output schema parameter, `<OUTPUT_FORMAT>` XML tag
- **Response parsing**: `parse_response()` attempts XML/JSON extraction from responses

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 6.1 | **No runtime schema validation of LLM output** | CRITICAL | Schema enforcement is instructional only (Pattern #27 tells the LLM to match schema). No code validates the actual response against the schema. LLM non-compliance goes undetected. |
| 6.2 | **No structured output mode integration** | HIGH | Modern LLM APIs (OpenAI JSON mode, Anthropic tool_use, Gemini structured output) guarantee valid JSON. The architecture doesn't use these — it relies on free-text prompting for structure. |
| 6.3 | **Response parser is fragile** | MEDIUM | `parse_response()` uses basic string `find()` for XML extraction and falls back to JSON.loads. No robust parser for malformed output, partial responses, or mixed formats. |
| 6.4 | **No output consistency verification** | MEDIUM | Stability Contracts (Pattern #28) are instructional. No code compares output field ordering or naming across invocations. |
| 6.5 | **No retry-on-parse-failure** | MEDIUM | If output parsing fails, there's no automatic retry with more explicit formatting instructions. |

### Recommendations
- **R6.1**: Add `jsonschema` or `pydantic` validation for every LLM response before it enters the pipeline.
- **R6.2**: Use LLM-native structured output modes (JSON mode, function calling) as primary, with instructional patterns as defense-in-depth.
- **R6.3**: Implement robust output parser with fallback chain: structured mode → XML extraction → JSON extraction → regex extraction → retry.
- **R6.4**: Add schema drift detection: compare output schemas across invocations and flag changes.
- **R6.5**: Implement retry loop with progressive format reinforcement on parse failure (similar to existing constraint escalation pattern).

---

## Category 7: Context Engineering & RAG Integration

### What Exists
- **Instructional Pattern #6**: Untrusted Block Wrapping
- **Instructional Pattern #8**: Context Pruning Rules
- **Instructional Pattern #10**: Structured Context Ordering
- **SelfRAGProcessor** (`L4_state/utils/rag_enhancement_util.py`): Self-reflective RAG
- **EpisodicMemory** & **KnowledgeGraphInjector**: Context enrichment
- **Multi-hop RAG** in `resume_prompts_validator.py`: 4-phase RAG with librarian agent
- **Context budget**: max_tokens parameter in context layer

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 7.1 | **No context window management strategy** | HIGH | Token budget is a soft instructional hint (Pattern #8). No code enforces context fits within model limits. Risk of silent truncation by the API. |
| 7.2 | **RAG chunk provenance not tracked in prompts** | MEDIUM | Retrieved chunks enter context without source attribution. Evidence Binding (Pattern #17) is instructional — no structured metadata tagging of RAG sources in prompt context. |
| 7.3 | **No relevance scoring for context items** | MEDIUM | All context items are included equally. No scoring/ranking to prioritize high-relevance items when approaching context limits. |
| 7.4 | **Librarian context is free-text, not structured** | LOW | `librarian_section` is inserted as markdown-formatted text into prompts. Structured data would be more reliable. |

### Recommendations
- **R7.1**: Implement hard context window management: count tokens per model, truncate intelligently (preserve system prompt + recent context, trim mid-context).
- **R7.2**: Add structured provenance metadata to every RAG chunk: `{source, retrieval_score, timestamp, chunk_id}`.
- **R7.3**: Implement relevance-based context packing: score each context item and pack highest-relevance items first within budget.
- **R7.4**: Use structured JSON for librarian context injection instead of markdown.

---

## Category 8: Observability & Governance

### What Exists
- **Prompt Evaluation Rubric** (`data/prompt_governance/evaluations/rubric.yaml`): Comprehensive 10-criteria scoring framework
- **Access Control** (`data/prompt_governance/governance/`): RBAC, approval workflows, compliance mapping
- **Registry Audit** (`prompt_governance/scripts/audit_registry_linkages.py`): Verifies registry→template linkage
- **Template Drift Detection** (`prompt_governance/scripts/detect_template_drift.py`): Detects template changes
- **Regression Tests** (`data/prompt_governance/evaluations/regression_tests.yaml`): Test framework defined

### Findings

| # | Finding | Severity | Details |
|---|---------|----------|---------|
| 8.1 | **No runtime prompt logging/tracing** | HIGH | No structured log of actual assembled prompts sent to LLMs. Can't debug, audit, or analyze prompt effectiveness post-hoc. |
| 8.2 | **PromptOptimizer is a stub** | MEDIUM | `optimize()` returns prompt unchanged. `analyze_prompt()` returns hardcoded scores (0.8, 0.7). No actual optimization logic. |
| 8.3 | **Evaluation rubric is YAML-only, not automated** | MEDIUM | Comprehensive rubric exists but no code executes it. Evaluation is manual. |
| 8.4 | **No prompt cost tracking** | LOW | No tracking of token usage, API costs, or latency per prompt template. |
| 8.5 | **Governance YAML is extensive but disconnected** | LOW | 40+ governance YAML files exist (access control, approval workflows, compliance) but no runtime code enforces them. They're aspirational documentation. |

### Recommendations
- **R8.1**: Implement prompt tracing: log every assembled prompt with metadata (template_id, agent, patterns_applied, token_count, timestamp) to structured storage.
- **R8.2**: Implement actual optimization: token compression, redundancy removal, instruction deduplication.
- **R8.3**: Build automated evaluation runner that scores prompts against the rubric using LLM-as-judge or golden-set comparison.
- **R8.4**: Add cost tracking middleware: log tokens_in, tokens_out, model, latency, cost_usd per request.
- **R8.5**: Connect governance YAMLs to runtime enforcement or remove them to avoid false confidence.

---

## Priority Matrix

| Priority | Count | Findings |
|----------|-------|----------|
| **CRITICAL** | 2 | 1.1 (blocklist bypassable), 6.1 (no output schema validation) |
| **HIGH** | 9 | 1.2, 1.3, 1.4, 3.1, 3.2, 4.1, 4.3, 5.2, 7.1 |
| **MEDIUM** | 13 | 1.5, 1.6, 2.1, 2.3, 2.5, 3.3, 3.4, 4.2, 4.4, 4.5, 5.1, 5.3, 6.2-6.5, 7.2, 7.3, 8.1-8.3 |
| **LOW** | 4 | 2.4, 3.5, 5.4, 5.5, 7.4, 8.4, 8.5 |

## Implementation Plan (Recommended Order)

1. **Sprint 1 — Critical Fixes**: R1.1 (expand blocklist), R6.1 (add schema validation)
2. **Sprint 2 — Injection Hardening**: R1.2 (ML classifier), R1.3 (indirect injection defense), R1.4 (encoding detection)
3. **Sprint 3 — Reasoning Maturity**: R4.1 (functional strategies), R4.3 (self-consistency), R3.2 (semantic few-shot)
4. **Sprint 4 — Output Reliability**: R6.2 (structured output modes), R6.3 (robust parser), R6.5 (retry loop)
5. **Sprint 5 — Observability**: R8.1 (prompt tracing), R5.1 (pattern telemetry), R8.4 (cost tracking)
6. **Sprint 6 — Governance Activation**: R2.4 (populate registry), R8.3 (automated evaluation), R8.5 (governance enforcement)

---

## Strengths (What the Architecture Does Well)

- **Layered injection architecture**: 30 patterns across 6 semantic layers is well-designed and exceeds most production systems
- **XML semantic fencing**: `PromptAssembler` properly separates trusted/untrusted content with tagged boundaries
- **Red-team templates**: Adversarial jinja templates (CoT jailbreak, base64, leetspeak) show security awareness
- **Governance infrastructure**: Versioning, registry, rubric, approval workflows — the bones are excellent
- **Progressive constraint reinforcement**: The retry-with-escalation pattern in resume generation is a best practice
- **Constitutional guardrails**: Pattern #23 and delegation guards (#24) align with Anthropic-style constitutional AI
- **Sovereign rendering**: StrictUndefined Jinja2 with schema validation prevents template injection

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

