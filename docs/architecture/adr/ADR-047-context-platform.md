# ADR-047 — Context Platform: Unified Assembly for Docs, Memory, and Tools

**Status**: Accepted (implemented)
**Date**: 2026-04-23
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/knowledge/engine` (new), `agentic_core/knowledge/retrieval`, `agentic_core/L4_state/memory`, MCP Registry, `apps_research` (pilot), `apps_shared`
**Plan**: `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md` (W4, W5)

**Current-state note (2026-06-15):** Implemented by `agentic_core/knowledge/engine/context_platform.py` and the `context_assembly_manifest.schema.json` path, with `tests/unit/agentic_core/knowledge/engine/test_context_platform.py`.

---

## Context

The 2025 consensus in external guidance — Anthropic's *Effective Context
Engineering for AI Agents*, Google's Vertex AI grounding stack, and
RAGFlow's year-end review — converges on a single architectural claim:

> Retrieval for agents is no longer about returning document chunks. It is
> about **assembling context** — documents, memory, and tool/skill
> descriptions — into the smallest high-signal set the model needs for the
> current step.

This repo has all three substrates but they are not unified:

- **Documents / RAG**: `agentic_core/knowledge/retrieval/*` (rich: C0.1
  plan, hybrid recall, parent-child hydration, evidence contract).
- **Memory**: `memory` MCP (Cursor Agent-side cross-session graph) and
  `agentic_core/L4_state/memory/*` (runtime semantic cache, canonical
  store). These are not addressable through the C0 pipeline.
- **Tools / skills**: `.windsurf/mcp_config.json` + per-app registries.
  Tool descriptions are statically concatenated into prompts. No retrieval,
  no ranking — leading to documented "choice paralysis" at scale (RAGFlow
  2025).

There is no declarative shape a caller can ship to say "for task X, give
me the right mix of documents, memory, and tools." Each app wires its own
ad hoc combination.

## Decision

Introduce a **Context Platform**: a single declarative pipeline that, given
a `ContextAssemblyManifest`, returns a fully-assembled context payload
drawing from all three substrates.

Normative requirements:

1. A JSON schema `config/schemas/context_assembly_manifest.schema.json`
   defines the manifest shape: task descriptor, tenant/ACL, corpus pointers,
   memory scopes, tool-selection policy, budget caps (tokens, latency), and
   provider target.
2. A new engine `agentic_core/knowledge/engine/context_platform.py`
   orchestrates:
   - Corpus-size gate (existing `corpus_size_gate.py`): skip RAG when
     full-context + caching is cheaper and better.
   - Document retrieval (existing C0.1–C0.5 pipeline).
   - Memory retrieval (new adapter over `L4_state/memory/*` and
     Cursor Agent-side `memory` MCP where appropriate).
   - Tool/skill retrieval (new `tool_selector.py`, ADR-045-adjacent, over
     MCP Registry and `L4_state/cache/tool_embedding_cache.py`).
   - Compaction + tool-result clearing for long-horizon loops.
   - Prompt-assembly handoff via `anthropic_prompt_renderer.py` (or vendor
     equivalent behind the W6.2 adapter).
3. Apps migrate progressively, starting with `apps_research` as pilot.
   Apps not yet migrated continue to call the existing C0 pipeline
   directly; no forced cutover.
4. Manifest evaluation is **replayable** end-to-end. `replay_key`,
   `policy_hash`, and a content digest stamp the assembled payload so any
   downstream answer is reproducible from (manifest, snapshot).
5. JIT identifier pattern: the platform may return lightweight
   identifiers (`IdentifierRef`) instead of full content when the manifest
   opts in; dereferencer tools live at L2 under authorized-write rails and
   stay ACL-bound.

## Non-Goals

- Replacing the MCP Registry. The platform **consumes** registry metadata;
  registry ownership stays where it is.
- Inventing a new vector store. Platform runs on the existing ChromaDB +
  BM25 + graph substrates.
- Cross-tenant context blending. Tenant isolation remains absolute and is
  enforced by the pre-retrieval gate upstream of the platform.

## Consequences

**Positive**

- Ends the ad-hoc-per-app retrieval pattern; one testable surface.
- Makes tool choice a data-driven retrieval problem, which is how 2025
  external guidance says it should be treated.
- Natural home for the compaction + note-taking patterns Anthropic's
  long-horizon guidance calls for.
- Replay-friendly end-to-end.

**Negative / costs**

- Large blast radius at the apps layer. Mitigated by opt-in per-app
  migration behind a feature flag.
- Manifest schema drift risk. Mitigated by JSON-schema CI gate and
  version bind.

**Risks**

- Scope creep: the platform becomes a "do-everything" dumping ground.
  Mitigated by tight manifest contract and the explicit Non-Goals above.
- ACL leakage across substrates. Mitigated by substrate-specific
  pre-retrieval gates running BEFORE the platform fuses results.

## Alternatives Considered

1. **Status quo: each app keeps its own assembler.** Accepts duplication
   and drift; makes tool-retrieval and compaction impossible to add
   systemically.
2. **Build tool-retrieval only, leave docs and memory separate.** Solves
   the worst single pain (choice paralysis) but still leaves three
   disjoint context stories per app.
3. **Outsource to an external "context platform" product.** Unacceptable
   constitutional coupling; our retrieval substrates and governance rails
   are too custom.

## References

- Anthropic, *Effective Context Engineering for AI Agents*, 2025
- Google Cloud, *RAG and grounding on Vertex AI*, 2024
- RAGFlow, *From RAG to Context — 2025 year-end review*, 2025
- Theory Ventures, *Context Platform* thesis, 2024–2025
- Constitutional §22 (graph-layer primacy) and §24 (deferred-scope
  capture) both extend into the platform's eval and backlog hooks.
- Plan: `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`
