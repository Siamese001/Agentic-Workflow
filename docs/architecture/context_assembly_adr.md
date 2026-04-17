# Architecture Decision Record — Context Assembly Grounding Invariants

**ADR ID:** ADR-CTX-001
**Status:** Accepted
**Date:** 2026-04-17
**Authority tier:** T4_repo_canonical
**Normative use:** `invalid_for_normative_use = False` — this ADR IS a normative source for context-assembly invariants inside this repository.
**Scope marker:** Context grounding for all L1/L2/L3 reasoning and orchestration flows.

---

## 1. Status

**Accepted.** This ADR codifies three invariants that already hold in the canonical `ContextAssembler` implementation. No module rewrite is mandated. The invariants are now canonically binding on every new context-producing path.

---

## 2. Context

Every reasoning, orchestration, and task-execution path that consumes "context" in this repository is routed through `agentic_core.L1_cognition.reasoning.context_assembler.ContextAssembler.assemble_context()`. The assembler takes a `RAGQuery`, runs a `SearchFusionEngine` search, converts results to `ContextItem` records, filters and ranks them, applies length constraints, and returns a `RAGContext` whose items carry `source_file`, `line_number`, `item_id`, and per-item `relevance_score` / `confidence`.

Three invariants of this pipeline have been implicit in code but have not been written down as an authoritative architectural decision. Requirement-graph family **F04 (Context Assembly)** relies on these invariants being canonical. Atoms **F04.02**, **F04.03**, and **F04.04** each depend on one of the three invariants below.

---

## 3. Decision

### 3.1 Invariant CTX-I1 — Context Attribution (supports F04.02)

**Every `ContextItem` delivered to a reasoning, orchestration, or task-execution consumer MUST carry resolvable source attribution.**

Concretely:
- Each `ContextItem` MUST have a non-empty `item_id` identifying the source record.
- Each `ContextItem` MUST have `source_file` set to the path, collection, or identifier from which the item was retrieved when such a source is known. When no repo-local source exists (e.g., an external API response), the `source_file` field MUST hold the external identifier (URL, document ID) rather than be left empty.
- Each `ContextItem` MUST preserve its `relevance_score` and `confidence` from the producing `SearchResponse.results`. Downstream consumers MUST NOT rewrite these scores.
- The aggregated `RAGContext` MUST expose `source_distribution`: a map of source → count for every context item included in the final set.
- Truncated items MUST carry `context_type = "truncated"` so that downstream consumers can distinguish a truncated item from a complete item.

**Forbidden:** emitting a `ContextItem` with `item_id = None`, unattributed `content`, or a score rewritten from the source record.

**Implementation backing:** `ContextAssembler._convert_to_context_items()` constructs every `ContextItem` from a `SearchResult` and carries `item_id`, `source_file`, `line_number`, `relevance_score`, `confidence`. `ContextAssembler._create_context()` computes `source_distribution` over all delivered items.

### 3.2 Invariant CTX-I2 — Single Grounded Path, No Private Substitute (supports F04.03)

**Context consumed by any reasoning, orchestration, or task-execution path MUST originate from a `RAGContext` produced by `ContextAssembler.assemble_context()` (or a documented superseding assembler registered in this repo). Private, unattributed context substitutes are forbidden.**

Concretely:
- A consumer MUST NOT construct an ad-hoc `list[ContextItem]` from inline prompt text, hard-coded fixtures, or module-local caches and treat it as equivalent to an assembled `RAGContext`.
- A consumer MUST NOT strip the `source_distribution`, `item_type_distribution`, or per-item attribution fields before passing the context downstream.
- When a consumer augments context (e.g., reasoning scratchpad notes), the augmentation MUST be delivered alongside the `RAGContext`, never merged into it in a way that erases source attribution of the original items.
- Test doubles (stubs, mocks) used in unit tests are exempt from this invariant ONLY when the test explicitly asserts behavior that depends on an assembled-path input; they MUST NOT be used in production code paths.

**Forbidden:** substituting private, unattributed context while preserving the `RAGContext` type signature. The type alone is not the contract; the attributed provenance is the contract.

**Implementation backing:** `ContextAssembler` is the sole public entry point producing `RAGContext` in `agentic_core.L1_cognition.reasoning`. The `create_context_assembler()` factory returns only instances of this class. No alternative `RAGContext` constructor is exported.

### 3.3 Invariant CTX-I3 — Assembly Idempotence for Identical Inputs (supports F04.04)

**Given identical inputs — same `RAGQuery`, same `SearchFusionEngine` state, same `RAGConfig`, same `GraphRAGConfig` — `ContextAssembler.assemble_context()` MUST return a `RAGContext` whose item set (by `item_id`) and per-item attribution fields are identical across invocations.**

Concretely:
- Filter and rank order MUST be deterministic given identical relevance scores and item types. Ties MUST break on a stable key (canonically: item_id lexicographic order after score sort).
- Length-constraint truncation MUST be deterministic: the same ordered input yields the same truncated set and the same `truncation_applied` flag.
- Diversity filtering MUST be deterministic: the same input yields the same `diverse_items` list. Randomized selection is forbidden inside the assembly path.
- Timing-dependent fields (`assembly_time_ms`) are explicitly exempt from idempotence. Item identity, attribution, ordering, and length behavior are NOT exempt.
- When the upstream `SearchFusionEngine` state changes (index update, collection change), that constitutes an input change and the idempotence invariant does not apply across that boundary. The invariant applies within a fixed-state window.

**Forbidden:** introducing nondeterministic ordering, reservoir sampling, wall-clock-dependent ranking, or any selection mechanism that yields different `item_id` sets for identical inputs.

**Implementation backing:** `_filter_and_rank_items()` sorts by `relevance_score` descending; `_apply_diversity_filtering()` walks items in rank order with a deterministic `seen_sources` set; `_apply_length_constraints()` walks items in rank order until budget exhausts. None of these introduces wall-clock or random state.

---

## 4. Relation to OOS-003

OOS-003 (Out-of-scope: context-assembly ADR) carries a revisit trigger that this ADR satisfies. After this ADR is registered in the canonical requirement graph, OOS-003's revisit condition is met and the exclusion SHOULD be re-evaluated in a later wave.

This ADR does not itself close OOS-003 (the closure is an exclusion-state transition, not an ADR action). It does make the closure cleanly supportable.

---

## 5. Scope Limits (non-consequences)

- This ADR does NOT prescribe how `SearchFusionEngine` computes relevance scores. Relevance semantics remain in the search engine's own doctrine.
- This ADR does NOT mandate a specific token-budget formula. Token estimation remains `_estimate_tokens()` heuristic.
- This ADR does NOT bind L5 policy to context assembly. That remains an open interaction candidate (C2 in the interaction log) pending a separate decision.
- This ADR does NOT specify replay-determinism at the mutation layer. That concern is covered by `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md`. The idempotence invariant here is specific to context assembly, not mutation replay.

---

## 6. Validation Criteria

- **CTX-I1:** a CI gate that inspects every call site returning `RAGContext` confirms `ContextItem.item_id != None` and `source_file` is set (or carries an external identifier) on every item. Test hook: `tests/architecture/test_context_attribution.py` (to be authored).
- **CTX-I2:** a static gate forbidding direct construction of `RAGContext` outside `ContextAssembler.assemble_context()` and its factory. Test hook: `tests/architecture/test_no_private_context.py` (to be authored).
- **CTX-I3:** a replay test that runs `assemble_context()` twice against a frozen search-engine fixture and compares the returned item IDs and ordering. Test hook: `tests/architecture/test_context_idempotence.py` (to be authored).

Validation tests are out of scope for this ADR's publication but are tracked as an implementation-debt item.

---

## 7. References

- `agentic_core/L1_cognition/reasoning/context_assembler.py` — implementation
- `agentic_core/L1_cognition/types/rag_types.py` — `RAGContext`, `RAGQuery`, `ContextItem`, `RAGConfig`
- `agentic_core/L1_cognition/reasoning/search_fusion_engine.py` — upstream search
- `agentic_core/L1_cognition/reasoning/reasoning_context_builder.py` — an adjacent consumer
- `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md` — adjacent (mutation-replay), not this ADR
- Requirement graph family F04; atoms F04.02, F04.03, F04.04
- Exclusion OOS-003 (revisit trigger now satisfied)

---

## 8. Change History

| Version | Date | Note |
|---|---|---|
| 1.0 | 2026-04-17 | Initial ADR — codifies CTX-I1/I2/I3 against existing `ContextAssembler` implementation. Authored in Wave F3 to close F04 red family. |
