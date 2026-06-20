# ADR-045 — Contextual Retrieval Gateway Wiring

**Status**: Accepted (implemented; rescoped 2026-04-23; amended 2026-04-24 for local-LLM default)
**Date**: 2026-04-23 (amended 2026-04-24)
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `tools/ingestion/contextual_chunk_builder.py` (existing), `tools/ingestion/qwen_context_gateway.py` (new default), `tools/ingestion/anthropic_context_gateway.py` (opt-in), `tools/ingestion/ingest_code.py`, `tools/ingestion/ingest_docs.py`, `agentic_core/knowledge/canonical/chunk_manifest.py`.
**Plan**: `.codex/plans/c0-context-assembly-best-practices-b7c3a1.md` §2a (G1 residual)
**Supersedes / Relates-to**: `.codex/plans/anthropic-rag-gaps-7f3c2a.md` P1.1 (preprocessor landed; gateway wiring owned here)

**Current-state note (2026-06-15):** Implemented by the contextual chunk builder plus Qwen/Anthropic context gateways and chunk-manifest contextual fields; covered by ingestion gateway and contextual chunk builder tests.

---

## Amendment (2026-04-24) — local-LLM gateway promoted to default

Commit `7ccfc32b67` retires **paid Anthropic API calls as a default requirement** for ADR-045 contextualization. Rationale:

- Claude-Haiku-4-5 per-chunk cost scales linearly with corpus size. Back-of-envelope for a full repo ingest: 5k–50k chunks × (parent-doc input tokens + ~100 output tokens) = **$5–$50 per re-index**, and that cost recurs every time the corpus is rebuilt. The cache-control optimization discussed below mitigates but does not eliminate it.
- The repo already operates a sanctioned Qwen 2.5 vLLM serving path at L3 (`agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py`). The operator runs `Qwen/Qwen2.5-14B-Instruct-AWQ` on 32 GB of local VRAM, which is sized for this class of workload.
- Qwen2.5-14B is well above the quality floor for 50-100 token situated-context generation. The technique does not require frontier-model reasoning — it requires faithful paraphrase of the parent doc conditioned on the chunk. A strong mid-size open model is sufficient.

The **technique** (Anthropic-style chunk-prefix contextualization) is unchanged. Only the **default backend** changes from paid Claude to local Qwen vLLM. Anthropic remains available as an opt-in backend via `CONTEXT_GATEWAY=anthropic` for operators who want to reproduce Anthropic's published numbers verbatim.

**Backend selection matrix** (honored by `tools/ingestion/ingest_code.py::_build_context_gateway`):

| `CONTEXT_GATEWAY` value | Backend chain |
|---|---|
| unset / `auto` (default) | Qwen vLLM → Anthropic (if `ANTHROPIC_API_KEY`) → heuristic |
| `qwen` | Qwen vLLM only — returns None if unreachable (no paid fallback, $0 guarantee) |
| `anthropic` | Anthropic only — returns None if `ANTHROPIC_API_KEY` absent |
| `heuristic` / `off` / `none` | Skip all LLM gateways; force heuristic-only |

This amendment updates §Decision item 1, §Consequences (cost narrative), and §Alternatives Considered. All other normative requirements (additive `situated_context` field on `ChunkManifest`, replayability, A/B acceptance gate) remain intact.

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

1. Two adapter modules in `tools/ingestion/` both implement the `_GatewayProtocol` declared in `tools/ingestion/contextual_chunk_builder.py` — a single method `generate(prompt, *, model, max_tokens, temperature, timeout_s) -> str`:
   - **`qwen_context_gateway.py`** (default): routes through the sanctioned `QwenInferenceGateway` at `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py`. Resolves model id and base URL from the L0 SSOT (`QWEN_LOCAL_MODEL_ID`, `VLLM_BASE_URL` — see `agentic_core/L0_routing/config/model_registry.py`). Module-level singleton gateway amortizes init cost. `build_from_env()` probes `${VLLM_BASE_URL}/models` with a 2s timeout and returns `None` on unreachable server.
   - **`anthropic_context_gateway.py`** (opt-in): routes through `apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic`. `build_from_env()` returns `None` when `ANTHROPIC_API_KEY` is absent. Still supports `cache_control=ephemeral` on the `<document>` prefix once the `GenerationRequest` shape is extended (G11-residual, deferred).
2. Both ingest call sites go through `_build_context_gateway()` which honors the `CONTEXT_GATEWAY` env knob per the backend-selection matrix above. `ContextualChunkBuilder(gateway=...)` is constructed with whatever that function returns; `None` yields the heuristic-only path.
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

- One-time re-index cost per corpus. **Default path is $0** (local Qwen vLLM — GPU time only). Anthropic opt-in path pays $5-$50 per re-index depending on corpus size, mitigated by Haiku-tier pricing and (once G11-residual lands) `cache_control=ephemeral` prompt caching on the parent doc.
- `ChunkManifest` schema migration. Handled by additive `situated_context` field (schema 1.1, shipped 2026-04-24) with 1.0-era payloads reading cleanly as empty string.
- Slight ingest-time latency increase. Does not affect C0 query-time path. Local Qwen path adds ~200-500ms per chunk on a 32GB GPU; Anthropic path adds ~300-800ms per chunk network round-trip.
- New dependency on the local vLLM server being running for the default path. Graceful fallback: `build_from_env()` probes the server and returns `None` on unreachable, which surfaces as the heuristic path. No hangs, no exceptions leak.

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
4. **Paid Anthropic API as the default backend (original 2026-04-23 draft).**
   Rejected 2026-04-24. Per-chunk $ cost scales linearly with corpus size,
   making repeat re-indexes economically unattractive. The local Qwen vLLM
   path produces equivalent-quality situated contexts at $0 marginal cost
   once the GPU is powered on. Anthropic retained as opt-in backend for
   operators who want to reproduce Anthropic's published Recall@20 numbers
   verbatim or who don't have local GPU capacity.
5. **Late Chunking (Jina-style full-doc pooling).** Strong free alternative
   that achieves the same goal via a different mechanism: embed the full
   document, then pool token embeddings into chunk vectors (each chunk
   inherits cross-chunk context from the full-doc attention pass). Not a
   replacement for this ADR — complementary. Tracked as a separate backlog
   item against BGE-M3's long-context mode. If the local Qwen path shows
   insufficient lift on A/B, Late Chunking is the next thing to add (or
   combine).

## References

- Anthropic, *Contextual Retrieval in AI Systems*, 2024-09
- Google Cloud, *RAG and grounding on Vertex AI*, 2024
- OpenAI Cookbook, *Prompt Caching 101 / 201*, 2025
- In-repo distillation: `docs/reference/03_L0_Routing/C0 - Retrieval/Anthropic RAG Best Practices.md`
- Plan: `.codex/plans/c0-context-assembly-best-practices-b7c3a1.md`
