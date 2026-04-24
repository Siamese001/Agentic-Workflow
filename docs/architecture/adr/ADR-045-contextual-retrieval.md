# ADR-045 — Contextual Retrieval Gateway Wiring

**Status**: Proposed (rescoped 2026-04-23 after discovery of prior work)
**Date**: 2026-04-23
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `tools/ingestion/contextual_chunk_builder.py` (existing), `tools/ingestion/ingest_docs.py`, `tools/ingestion/ingest_code.py`, `agentic_core/knowledge/canonical/chunk_manifest.py`, new gateway adapter module.
**Plan**: `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md` §2a (G1 residual)
**Supersedes / Relates-to**: `.windsurf/plans/anthropic-rag-gaps-7f3c2a.md` P1.1 (preprocessor landed; gateway wiring owned here)

---

## Rescope note (2026-04-23)

The original draft of this ADR proposed building Contextual Retrieval from scratch. A subsequent scope-overlap audit found that prior plan `anthropic-rag-gaps-7f3c2a` already shipped:

- `tools/ingestion/contextual_chunk_builder.py` (254 lines, Haiku-4-5 default, gateway-mediated + heuristic fallback, 8+ unit tests passing).
- `--contextualize` flag on `ingest_docs.py` (line 519) and `ingest_code.py`.

But the gateway adapter those call sites expect was **never injected**. `ContextualChunkBuilder()` is constructed at both call sites with no `gateway=` argument, so `_gateway_available()` returns `False` and `enabled` resolves to `False` regardless of `ANTHROPIC_API_KEY`. Only the heuristic metadata-based path runs.

This ADR therefore narrows to: **land the gateway adapter and wire it** so the existing Claude-generated contextual-retrieval path becomes reachable in production.

---

## Context

Anthropic's *Contextual Retrieval in AI Systems* (Sept 2024) reports that
traditional chunk-then-embed pipelines strip away the document-level context
needed for retrieval to succeed on specific queries. Their fix — prepending an
LLM-generated **50–100 token chunk-specific context** to each chunk before
both dense and BM25 indexing — reduced retrieval failure by **49 %** in
isolation and by **67 %** when combined with reranking.

This repo's current C0.2 `HybridRecallStage` (see
`agentic_core/knowledge/retrieval/hybrid_recall_stage.py`) already performs
dense + sparse fusion with sparse-wins-on-IDs, and `ChunkManifest` carries
ACL, freshness, and version binds. But nothing in
`agentic_core/knowledge/ingestion/` or
`agentic_core/knowledge/chunking/` generates a per-chunk situated-context
string from the parent document. Chunks are embedded as-is. This leaves a
large, documented retrieval-quality lift on the table.

Google's *Vertex AI Hybrid Vector Search* (2024 GA) and OpenAI's
*Prompt Caching 201* both converge on the same upstream principle: cheap
pre-computation against cached static context is the lever that makes
high-quality retrieval economically viable.

## Decision

Adopt Anthropic-style **Contextual Retrieval** as the canonical ingest-time
augmentation for all text corpora served by C0.

Normative requirements:

1. A new adapter module (e.g. `agentic_core/knowledge/retrieval/anthropic_context_gateway.py`) implements the `_GatewayProtocol` declared in `tools/ingestion/contextual_chunk_builder.py` — a single method `generate(prompt, *, model, max_tokens, temperature, timeout_s) -> str` — and routes through the existing `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` entry path with `cache_control=ephemeral` applied to the `<document>` prefix.
2. Both call sites (`ingest_docs.py:563` and `ingest_code.py:472`) inject this adapter: `ContextualChunkBuilder(gateway=AnthropicContextGateway(...))` when `ANTHROPIC_API_KEY` is set; pass nothing (heuristic fallback preserved) when it is not.
3. `ChunkManifest` gains a `situated_context: str` field (non-breaking additive). The metadata key `chunk_context` already in use in the ingest scripts is promoted to the canonical manifest schema with a one-session migration window.
4. Indexes are rebuilt under a new schema version bind (`retrieval_plan.py` already honors version pinning); old and new indexes coexist during rollout.
5. The contextualizer pass MUST be replayable: inputs (parent doc hash, chunk id, model tier, prompt template version) fully determine output. Failures are logged and fall back to the heuristic path — never silently swallowed.
6. A/B harness: `retrieval_benchmark.py` compares heuristic-only vs. gateway-enabled recall on the calibration corpus defined by the `config/retrieval/calibration_manifest.yaml`. Acceptance gate: **Recall@20 ≥ heuristic-baseline + 20 %** on the calibration corpus.

## Non-Goals

- Multi-modal (image/audio) contextualization — deferred.
- Real-time re-contextualization on doc update — for now, re-run at
  re-index time only.
- Replacing the reranker (ADR-046 handles that).
- Rebuilding the `ContextualChunkBuilder` class or the `--contextualize` flag — both already shipped by `anthropic-rag-gaps-7f3c2a` P1.1.

## Consequences

**Positive**

- Largest published single-change retrieval-quality lift on Claude; directly
  improves C0.4 evidence quality and C0.5 citation precision.
- BM25 becomes materially stronger on specific-term queries because the
  situated context surfaces entity, date, and topical cues the raw chunk
  lacks.
- Schema-versioned indexes allow safe rollout and easy rollback.

**Negative / costs**

- One-time re-index cost per corpus. Mitigated by Haiku-tier pricing and
  prompt caching on the parent doc.
- `ChunkManifest` schema migration. Handled by additive field + version bind.
- Slight ingest-time latency increase. Does not affect C0 query-time path.

**Risks**

- Contextualization LLM occasionally emits off-policy or over-long context.
  Mitigation: schema-validate output length and strip any text that contains
  instructions or model chatter before indexing.
- Parent-doc prompt caching varies by provider. The vendor-agnostic cache
  adapter (W6.2) formalizes the contract.

## Alternatives Considered

1. **Keep raw chunks, improve chunking boundaries only.** Does not address
   the underlying information-loss problem Anthropic's data quantifies.
2. **Use a dedicated retrieval-oriented embedding model (e.g. Voyage).** Not
   mutually exclusive; can layer on top of Contextual Retrieval later. Out
   of scope for this ADR.
3. **Query-side rewriting instead of chunk-side situating.** Higher latency
   (every query pays) and harder to cache. Anthropic explicitly prefers
   ingest-side.

## References

- Anthropic, *Contextual Retrieval in AI Systems*, 2024-09
- Google Cloud, *RAG and grounding on Vertex AI*, 2024
- OpenAI Cookbook, *Prompt Caching 101 / 201*, 2025
- In-repo distillation: `docs/reference/03_L0_Routing/C0 - Retrieval/Anthropic RAG Best Practices.md`
- Plan: `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`
