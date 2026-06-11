---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\rag-semantic-chunker-gap-c4f1a8.md'
original_relative_path: '_archive\\2026-05\\rag-semantic-chunker-gap-c4f1a8.md'
source_sha256: eb0a30e1130c05660e0df0feb8c6d6275c2e9b53a283e2176fb1e5c418dcb6df
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: RAG Semantic-Chunker Gap + Public-Benchmark Anchor

**Status**: Todo
**Tier**: T2 (3–5 files, single layer: `agentic_core/knowledge/chunking` + `tools/eval`)
**Plan ID**: `rag-semantic-chunker-gap-c4f1a8`
**Created**: 2026-04-24
**Origin**: NEXT_STEP from review of Sarkar "The Right Chunk, Wrong Context Problem" (Part 1)
**Web research basis**: Anthropic Contextual Retrieval (Sept 2024), Jina Late Chunking (arXiv 2409.04701), LangChain `SemanticChunker`, LlamaIndex `SemanticSplitterNodeParser`, RAGBench (arXiv 2407.11005)

---

## Context: What the Repo Already Has (do not duplicate)

| Capability | Location | Source-of-art |
|---|---|---|
| Contextual Retrieval (Anthropic) | `tools/ingestion/anthropic_context_gateway.py`, `contextual_chunk_builder.py`, ADR-045 | Anthropic Sept 2024 |
| Late chunking (Jina) | `agentic_core/knowledge/retrieval/late_chunking.py`, `tools/ingestion/late_chunking_helper.py` | Jina arXiv 2409.04701 |
| Hybrid BM25 + Vector + RRF | `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` (`_rrf_fuse`, `RRF_K=60`) | Standard RRF |
| Cross-encoder reranking | `agentic_core/knowledge/retrieval/{cross_encoder_reranker,bge_reranker_adapter,reranker_factory}.py` | ms-marco-MiniLM, BGE-v2-m3 |
| Parent-child hydration | `agentic_core/knowledge/retrieval/parent_child_hydrator.py`, `chunk_manifest_registry.py` | Hierarchical / Parent-Document |
| Heuristic semantic chunking (regex) | `agentic_core/knowledge/chunking/chunking_modes.py::SemanticObjectChunker` | Paragraph + sentence regex (NOT embedding-cosine) |
| Hit@K / MRR@K eval primitives | `agentic_core/utils/workflow_engines/mrr.py`, `tools/eval/retrieval_abcd_harness.py` | Internal sets only |

**Gap**: (1) embedding-cosine semantic chunker, (2) RAGBench TechQA public-benchmark anchor, (3) end-to-end ablation harness comparing approaches head-to-head.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1 | `EmbeddingSemanticChunker` strategy | 2,000 | sentence-transformers already installed; `chunking_modes.py` is the SSOT registry | 🟢 Todo | Class lands; 4 breakpoint modes (percentile, stdev, IQR, gradient); registered; unit tests pass |
| W2 | W2.1, W2.2 | RAGBench TechQA loader + ablation harness | 2,500 | RAGBench is HF-hosted (`rungalileo/ragbench`); TechQA subset small enough to vendor | 🟢 Todo | `tools/eval/ragbench_runner.py` emits 5-row × 2-col Hit@5 / MRR@5 markdown table |
| W3 | W3.1 | Wire to `chunk_policy_engine` + ADR-047 | 1,500 | Existing `chunking_modes` registry pattern is stable | 🟢 Todo | New mode selectable via config; ADR-047 written; MCP Registry / ADR Registry updated |

**Budget**: 6,000 tokens (matches NEXT_STEP estimate).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Add `EmbeddingSemanticChunker` | `agentic_core/knowledge/chunking/chunking_modes.py` (add class), `tests/unit/agentic_core/knowledge/chunking/test_embedding_semantic_chunker.py` (new) | Existing `SemanticObjectChunker` name is misleading — must not rename (backward-compat); must avoid embedding-model cold-start in unit tests (use a stub embedder) | 2,000 | Todo |
| W2.1 | RAGBench TechQA loader | `data/eval/golden/ragbench_techqa.jsonl` (vendor 50 queries), `tools/eval/ragbench_loader.py` (new) | License check on RAGBench data; must be offline-runnable (no HF download at test time) | 1,000 | Todo |
| W2.2 | 5-approach ablation harness | `tools/eval/ragbench_runner.py` (new), reuses `hybrid_search_engine` toggles + `mrr.py` | Must toggle: (a) naive fixed vs (b) semantic vs (c) +hybrid vs (d) +rerank vs (e) +parent-child — without re-indexing per run | 1,500 | Todo |
| W3.1 | Wire + ADR-047 | `agentic_core/knowledge/chunking/chunk_policy_engine.py` (register), `docs/architecture/adr/ADR-047-embedding-semantic-chunking.md` (new), Notion ADR Registry row | ADR must cross-reference ADR-045 (contextual retrieval) and late_chunking.py to clarify the decision space | 1,500 | Todo |

---

## W1.1 Detail — `EmbeddingSemanticChunker` Contract

Modeled on LangChain `SemanticChunker` (breakpoint modes) and LlamaIndex `SemanticSplitterNodeParser` (buffer_size window).

```python
class EmbeddingSemanticChunker(ChunkingStrategy):
    def __init__(
        self,
        embedder: Callable[[list[str]], list[list[float]]],  # injectable (dependency inversion — allows stub in tests)
        breakpoint_type: Literal["percentile", "stdev", "iqr", "gradient"] = "percentile",
        breakpoint_threshold: float = 95.0,  # percentile cutoff
        buffer_size: int = 1,                # sentences on each side to group before embedding
        min_chunk_chars: int = 100,          # avoid tiny chunks
        max_chunk_chars: int = 2000,         # hard cap
    ): ...

    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        # 1. Split into sentences (reuse existing regex from SemanticObjectChunker)
        # 2. Group with buffer_size window → "sentence groups"
        # 3. Embed each group
        # 4. Compute cosine distance between adjacent groups → distances[]
        # 5. Find breakpoints where distance > threshold (by mode)
        # 6. Assemble chunks between breakpoints, respecting min/max_chunk_chars
        # 7. Return Chunk[] with metadata {"strategy": "embedding_semantic", "breakpoint_type": ..., "doc_id": ...}
```

**Key design decisions** (baked in from research):

- **Injectable embedder** — unit tests pass a stub returning deterministic vectors; production wires BGE-m3 or the existing embedder from `agentic_core/L4_state/exemplars/embedding_retriever.py`. Avoids cold-start and model-load in tests.
- **4 breakpoint modes** match LangChain's `SemanticChunker` (percentile, stdev, IQR, gradient) — no lock-in to one threshold style.
- **Progress bar mandatory** — constitutional §16 requires `ProgressReporter` for any loop over >10 sentences.
- **Late-chunking complement, not replacement** — docstring explicitly notes: "For documents <8k tokens with high semantic density, prefer `late_chunking.py`. This chunker is for the pre-embedding boundary-detection case."

---

## W2.1 Detail — RAGBench TechQA Loader

RAGBench (`rungalileo/ragbench` on HuggingFace, arXiv 2407.11005) contains TechQA as one of 12 subsets. Plan:

1. Vendor **50 queries** (Sarkar blog used 50) + their gold passages into `data/eval/golden/ragbench_techqa.jsonl` — one JSON-per-line with fields: `query_id`, `query`, `relevant_passage_ids`, `relevant_passages`.
2. Loader returns `list[EvalQuery]` — no HF dependency at runtime.
3. License check: RAGBench is Apache-2.0 compatible for eval use (confirm in ADR-047).

**Out of scope**: full 100K-pair RAGBench; other subsets (PubmedQA, CUAD, FinBench). One subset is enough to anchor against the blog.

---

## W2.2 Detail — 5-Approach Ablation Harness

`tools/eval/ragbench_runner.py` produces:

```
| Approach                                      | Hit@5 | MRR@5 |
|-----------------------------------------------|-------|-------|
| 1. Naive fixed-size (200 char, 50 overlap)   | 0.XX  | 0.XX  |
| 2. + Embedding semantic chunking             | 0.XX  | 0.XX  |
| 3. + Hybrid BM25 (RRF)                        | 0.XX  | 0.XX  |
| 4. + Cross-encoder rerank                     | 0.XX  | 0.XX  |
| 5. + Parent-child hydration                   | 0.XX  | 0.XX  |
```

Reuses existing toggles on `HybridSearchEngine`:
- `enable_lexical=False/True` (row 2→3)
- Pass/skip rerank stage via factory (row 3→4)
- Hydrate vs return-child-verbatim via `parent_child_hydrator` (row 4→5)

**Bonus row** (if time permits): "6. + Contextual Retrieval (ADR-045)" to show the Anthropic uplift on the same benchmark. This is the unique value the repo has over the blog.

---

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Impact | Surface |
|---|---|---|---|---|---|
| `agentic_core/knowledge/chunking/chunking_modes.py` | L_KNOWLEDGE (~L2) | Medium (registry consumers) | CENTRAL_DEPENDENCY | New class appended; no existing class changed → **zero blast radius** | None |
| `agentic_core/knowledge/chunking/chunk_policy_engine.py` | L_KNOWLEDGE | Medium | ORCHESTRATOR | Registers new mode (additive) | None |
| `tools/eval/ragbench_runner.py` | L6 obs / eval | 0 (new file) | ISOLATED | New tool, no callers yet | None |

Query executed: `adg_nodes_by_file` for `chunking_modes.py` confirms additive-only change. No fan-in disruption.

---

## ADG_GRAPH_LAYER_EVIDENCE

- **`mv_graph_reverse_dependency_hotspots`**: `chunking_modes.py` fan-in shows it is consumed by `chunk_policy_engine.py` and `contextual_chunk_builder.py`. Both are called through a strategy-registry dispatch; adding a new strategy class is **append-only** and does not disturb any existing edge.
- **`mv_hotspot_centrality`**: the chunking subsystem is NOT in the top-20 centrality rank — it is a leaf-ish module, confirming low blast radius.
- **Semantic edges**: no `writes_to` / `emits_side_effect` edges originate from chunking_modes.py — it is pure compute. Adding a new pure class adds zero new side-effect edges.
- **P-views**: not in any `v_p0_*` / `v_p1_*` violation view.
- **Provenance**: backend=sqlite, snapshot=adg_indexed_04242026 (latest available).

---

## Definitions of Done

1. `EmbeddingSemanticChunker` class present in `chunking_modes.py` with all 4 breakpoint modes.
2. Unit test file with stub-embedder covers: percentile mode, stdev mode, min/max chunk clamp, empty-text edge case, single-sentence edge case.
3. `data/eval/golden/ragbench_techqa.jsonl` vendored with 50 queries + license note.
4. `tools/eval/ragbench_runner.py` produces the 5-row markdown table and writes to `docs/reports/rag/ragbench_ablation_<UTC_DATE>.md`.
5. Registered in `chunk_policy_engine.py` under mode name `"embedding_semantic"`.
6. `docs/architecture/adr/ADR-047-embedding-semantic-chunking.md` written, cross-referencing ADR-045 (contextual retrieval), late_chunking, and clarifying when to use which of the three.
7. Notion ADR Registry row auto-posted for ADR-047.
8. `pytest tests/unit/agentic_core/knowledge/chunking/test_embedding_semantic_chunker.py` → all green.
9. Full ADG regen shows **no new P0/P1/P2 defects**; optional: regen not required if only pure additions.

---

## Verification Commands

```bash
# W1.1 unit tests
python -m pytest tests/unit/agentic_core/knowledge/chunking/test_embedding_semantic_chunker.py -v

# W2.2 ablation
python tools/eval/ragbench_runner.py --output docs/reports/rag/ragbench_ablation_$(date -u +%Y%m%d).md

# W3.1 ADG regen (additive class, should be clean)
python tools/generate_full_adg.py
```

---

## Out of Scope (explicitly)

- Contextual Retrieval enhancement (already in ADR-045 — revisit in a separate plan if uplift is insufficient).
- LLM-as-chunker mode (agenta/Weaviate 2024 idea) — higher cost, diminishing returns over embedding-cosine; defer.
- Full RAGBench (12 subsets) integration — TechQA alone anchors against the Sarkar blog.
- Benchmarking against Voyage/Gemini embeddings — repo standardizes on BGE-m3; separate decision.

---

## References

- Sarkar, "The Right Chunk, Wrong Context Problem" (2026) — https://arnabksarkar.github.io/blogs/rag-part1.html
- Anthropic, "Introducing Contextual Retrieval" (Sept 2024) — https://www.anthropic.com/news/contextual-retrieval
- Jina AI, "Late Chunking" — arXiv 2409.04701
- Friel et al., "RAGBench" — arXiv 2407.11005
- LangChain `SemanticChunker` API — `langchain_experimental.text_splitter.SemanticChunker`
- LlamaIndex `SemanticSplitterNodeParser` — https://docs.llamaindex.ai/en/stable/examples/node_parsers/semantic_chunking/
- Internal: ADR-045 (Contextual Retrieval), ADR-046 (Rerank Revival), `agentic_core/knowledge/retrieval/late_chunking.py`
