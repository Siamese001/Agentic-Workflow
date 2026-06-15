# ADR-058 — Query Transforms Catalog (HyDE, Step-Back, Decomposition, Self-Query)

**Status**: Accepted (router contract implemented; package split superseded)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: new `agentic_core/L1_cognition/reasoning/query_transforms/`, `agentic_core/L1_cognition/reasoning/multi_query_fusion.py`, `agentic_core/knowledge/retrieval/retrieval_plan.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W3.1
**Relates-to**: ADR-045 (contextual retrieval, ingest-side), ADR-046 (rerank), ADR-056/057 (embedder mechanics), `multi_query_fusion.py` (existing query-side work)

**Current-state note (2026-06-15):** `RetrievalRouter` routes `hyde`, `multi_query`, `decomposition`, `step_back`, and `self_query`, and RAG semconv has query-transform spans. The dedicated `query_transforms/` package split is superseded by the router-level strategy contract; a new core transform package would require a fresh Author-Gate plan.

---

## Context

Current query-side transforms in the repo:

| Transform | Module | Status |
|---|---|---|
| Multi-query fusion (generate N paraphrases, fuse) | `agentic_core/L1_cognition/reasoning/multi_query_fusion.py` | ✅ present |
| HyDE (hypothetical answer → embed) | — | ❌ absent |
| Step-back (abstract-level reformulation) | — | ❌ absent |
| Decomposition (complex → sub-queries → fuse) | — | ❌ absent |
| Self-query (LLM extracts metadata filters from NL) | — | ❌ absent |
| Query clarification (ambiguity → multi-interpret) | — | implicit in multi-query; not explicit |

Published effect sizes (per industry benchmarks on comparable corpora):

| Transform | Lift on Recall@20 | Cost | Best domain |
|---|:---:|---|---|
| Multi-query fusion | +3–8 % | 1 cheap LLM call | Broad queries |
| HyDE | +5–15 % | 1 cheap LLM call | Query/answer vocab divergence (code, Q&A) |
| Step-back | +4–12 % | 1 cheap LLM call | Multi-hop reasoning, "why does X fail when Y" |
| Decomposition | +8–20 % | N cheap LLM calls | Compound queries ("list all X that do Y and Z") |
| Self-query | precision gain (not recall) | 1 cheap LLM call | Filterable metadata (layer, date, artifact_type) |

The cost denomination matters: these are **sub-dollar** per query with Claude Haiku / GPT-4o-mini / local Qwen-14B. The repo already operates a sanctioned local Qwen vLLM (per ADR-045 amendment), so marginal cost is GPU-time only.

## Decision

Adopt a **catalog of four query-side transforms** plus explicit non-transform, with uniform protocol, deterministic identity, and routing via W3.2's rubric (separate document).

### Normative Requirements

1. **Module layout** — new package `agentic_core/L1_cognition/reasoning/query_transforms/`:
   ```
   __init__.py               # exports QueryTransform protocol + registry
   base.py                   # QueryTransform ABC, TransformResult dataclass
   identity.py               # IdentityTransform (no-op, canonical baseline)
   multi_query.py            # relocates logic currently in multi_query_fusion.py
   hyde.py                   # HyDETransform
   step_back.py              # StepBackTransform
   decomposition.py          # DecompositionTransform
   self_query.py             # SelfQueryTransform
   registry.py               # name → transform factory
   ```
   Existing `multi_query_fusion.py` becomes a thin shim that delegates to `multi_query.py` for one release, then retires.

2. **Uniform protocol** — every transform implements:
   ```
   class QueryTransform(Protocol):
       name: str                          # stable slug: "identity", "hyde", ...
       def apply(
           self,
           query: str,
           context: TransformContext,     # intent, layer hints, budget
       ) -> TransformResult:
           """
           TransformResult contains:
             - queries: list[str]         # 1..N transformed queries
             - filters: dict[str, Any]    # metadata filters (self-query only)
             - budget_used: dict          # latency_ms, llm_tokens, cost_usd
             - transform_id: str          # deterministic hash for replay
           """
   ```

3. **HyDETransform** — given a query, prompt a cheap LLM for a **hypothetical answer or document** of ≤200 tokens, then embed THAT instead of (or alongside) the raw query. Useful when query vocabulary (NL question) differs from corpus vocabulary (code identifiers). Must always return at least the **original** query in the queries list as well, so HyDE failure degrades gracefully.

4. **StepBackTransform** — prompt the LLM for an **abstraction** of the question: "What general concept or principle is this query asking about?" The abstract query retrieves the concept-level context; the original query retrieves the specific-level context. Final top-K is an RRF fusion over both. Ref: Zheng et al., *Take a Step Back* (ICLR 2024).

5. **DecompositionTransform** — prompt the LLM to split a compound query into ≤4 atomic sub-queries. Each sub-query is retrieved independently; results are fused (RRF) with provenance. Enforces a hard cap of 4 to prevent runaway LLM cost and fan-out to the vector store.

6. **SelfQueryTransform** — prompt the LLM with the repo's metadata schema (`layer`, `artifact_type`, `file_path` prefix, `embedding_model`, `freshness_days`) and a structured extraction request. Returns `{queries:[cleaned_query], filters:{"where": {...}}}`. The filter is handed to ChromaDB's native `where` clause (`SovereignChromaClient.query` already supports it; no client change needed). Returns no filter when the LLM is unsure — never invents filters.

7. **Deterministic identity** — each transform's output carries a `transform_id` = SHA-256 of `{transform_name, transform_version, llm_identity, prompt_template_version, query}`. Caches and the eval harness key off this.

8. **Budget plumbing** — every transform takes a `budget: TransformBudget` with `max_latency_ms`, `max_llm_tokens`, `max_cost_usd`. Exceeding → fall back to identity + telemetry event. No silent budget busts.

9. **Chaining** — a query may run through **at most one** transform per invocation. Chaining HyDE + Step-Back + Decomposition is explicitly **not supported** in v1 because the combinatorial cost and result-fusion complexity pay back diminishingly. W3.2's routing rubric picks one.

10. **Registry + factory** — `get_query_transform(name: str, *, llm_gateway=None) -> QueryTransform` is the single construction point. Honors `QUERY_TRANSFORM=identity|multi_query|hyde|step_back|decomposition|self_query` env override for A/B work, same pattern as `reranker_factory.get_reranker()`.

### Non-Goals

- **Query clarification loops** (prompt the user to disambiguate) — owned by L0 routing and runtime HITL (ADR-023); this ADR is retrieval-side only.
- **Query expansion via knowledge-graph hop** — that's CRAG/Self-RAG (W4 plan, future ADR); transforms here are single-shot, no retriever-loop feedback.
- **Training or fine-tuning a dedicated query-transform model.** Prompt-based only.
- **Batched transform** (transform N queries in one LLM call) — optimization deferred.

## Consequences

**Positive**
- Fills the largest documented retrieval-quality gap beyond ADR-045/046: query-side semantic alignment.
- Uniform protocol + registry makes A/B eval routine (`QUERY_TRANSFORM` env + `retrieval_abcd_harness.py` extension).
- Self-query closes the "Chroma `where` is capable but never used by agents" gap from the parent plan §G14.
- Each transform is independently rollback-able.

**Negative / costs**
- Each transform adds 200–1000 ms latency + 1 LLM call per query. On local Qwen vLLM: ~$0 marginal; on Anthropic: ~$0.0005–0.002 per query.
- Maintaining five LLM prompt templates. Mitigated by versioning under `transform_version` and the A/B harness.
- Debug surface area grows (which transform fired? which query went to the store?). Mitigated by the `transform_id` stamping in OTel spans.

**Risks**
- **R1 — LLM hallucinates a filter in SelfQuery that excludes the actual answer.** Mitigation: strict schema-validation of the LLM output; invalid/unknown filter keys are dropped, not raised; A/B gate enforces precision AND recall floors, not precision alone.
- **R2 — Decomposition fan-out explodes.** Mitigation: hard cap 4 sub-queries; budget enforced.
- **R3 — HyDE produces off-policy content.** Mitigation: output passes through `embedding_input_guard.GuardedText` before embedding, identical to any other text in the embedding pipeline.
- **R4 — Transforms drift away from corpus as it grows.** Mitigation: W5.1 nightly harness re-evaluates per-transform recall floors; regressions page.

## Alternatives Considered

1. **Only keep multi-query fusion.** Current state. Leaves documented 15-20 % recall lift unclaimed.
2. **Implement transforms inline in `multi_query_fusion.py` without a catalog.** Fastest path but tangles five orthogonal concerns; A/B impossible; retirement impossible.
3. **Use LangChain's `SelfQueryRetriever` / `MultiQueryRetriever` adapters.** Pulls in a heavy dependency graph and imposes their schema. Rejected — the primitives are small; own them.
4. **Use a dedicated query-rewriting model (e.g. `llm-rewrite-t5`).** Another model to host. The LLM we already operate is sufficient per published numbers. Rejected.
5. **Train a fused query transform (one prompt that outputs all strategies).** Unstable across strategies; hard to eval; low caller-depth. Rejected.

## Validation

- `pytest tests/unit/agentic_core/L1_cognition/reasoning/query_transforms/` — per-transform contract tests, deterministic `transform_id`, budget enforcement, fallback-to-identity on LLM failure.
- `tools/eval/retrieval_abcd_harness.py` gains a `QUERY_TRANSFORM` sweep alongside existing `RERANKER` sweep → 5 × 3 = 15 cells per run. Matrix published to Notion.
- Acceptance gate on the golden set (W5.1):
  - HyDE: Recall@20 ≥ identity + 5 %
  - Step-Back: Recall@20 ≥ identity + 4 %
  - Decomposition: Recall@20 on **compound** queries ≥ identity + 10 %
  - Self-Query: Precision@20 ≥ identity + 8 % without recall regression > 2 %
  - Multi-query: unchanged (already in place; regression gate only)

Rollback: set `QUERY_TRANSFORM=identity` globally. Transform modules stay on disk; they are no-ops until selected.

## References

- Gao et al., *Precise Zero-Shot Dense Retrieval without Relevance Labels* (2022) — HyDE
- Zheng et al., *Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models* (ICLR 2024)
- Chase et al., *Self-Querying Retriever* (LangChain docs, 2023+)
- Khot et al., *Decomposed Prompting* (ICLR 2023)
- In-repo: `agentic_core/L1_cognition/reasoning/multi_query_fusion.py`
- Routing rubric: `docs/reports/plans/query-transform-routing-rubric.md` (W3.2)
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
