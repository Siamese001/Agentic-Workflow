# ADR-059 — Embedding-Cosine Semantic Chunking

**Status**: Accepted
**Date**: 2026-04-24
**Deciders**: Knowledge / Retrieval working group
**Impact Layers**: `agentic_core.knowledge.chunking`, `tools/eval`
**Plan**: `.claude/plans/rag-semantic-chunker-gap-c4f1a8.md`

## Context

Review of Sarkar, "The Right Chunk, Wrong Context Problem" (2026), against
the repo surfaced one real chunking gap. The repo already implements:

- Anthropic **Contextual Retrieval** (ADR-045) — LLM-augmented chunks before
  embedding & BM25 indexing.
- Jina **Late Chunking** (`agentic_core/knowledge/retrieval/late_chunking.py`)
  — pooling token embeddings of a pre-embedded long document.
- Hybrid BM25 + vector + **RRF** fusion (`hybrid_search_engine.py`).
- Cross-encoder **reranking** (`reranker_factory.py`, ADR-046).
- **Parent-child hydration** (`parent_child_hydrator.py`,
  `chunk_manifest_registry.py`).

What was missing is the canonical LangChain `SemanticChunker` /
LlamaIndex `SemanticSplitterNodeParser` pattern: split sentences, embed
each, cut where adjacent cosine similarity drops. The existing
`SemanticObjectChunker` is regex-only (paragraph + sentence boundaries)
and its name was misleading — no embedding involvement.

## Decision

Introduce `EmbeddingSemanticChunker` in
`agentic_core/knowledge/chunking/chunking_modes.py` alongside the existing
four strategies. It implements the four standard breakpoint modes
(`percentile`, `stdev`, `iqr`, `gradient`) with an **injectable embedder**
so tests do not cold-start a model and production can wire BGE-m3 or
another canonical embedder via `ChunkingEngine.register_chunker()`.

### Why a separate class (not replace `SemanticObjectChunker`)

- Backward compatibility — callers referencing `SemanticObjectChunker` by
  name keep working.
- Different cost profile — embedding-cosine chunking costs N embeddings
  per document; regex chunking is free. Keeping both lets callers choose.
- Different failure surface — embedding-cosine degrades when sentences
  are too short or too uniform; regex chunking is unconditionally robust.

### Relationship to ADR-045 (Contextual Retrieval) and Late Chunking

| Technique | When it fits |
|---|---|
| `EmbeddingSemanticChunker` | Documents where **sentence-level topic shifts** are the dominant boundary signal (tech support transcripts, FAQs, heterogeneous reference docs). |
| **Late Chunking** (Jina) | Documents **< 8k tokens** where full-doc context matters at every chunk; minimizes storage (no extra per-chunk text) and resists bad boundary choices. |
| **Contextual Retrieval** (ADR-045) | When absolute quality is the priority and LLM inference cost is acceptable; stacks on top of the other two at retrieval time. |

These are complementary, not alternative. A production pipeline may use
`EmbeddingSemanticChunker` at ingest, `contextual_chunk_builder` to
augment each chunk, then `late_chunking` is reserved for corpora with
different characteristics.

## Implementation

- **File**: `agentic_core/knowledge/chunking/chunking_modes.py`
- **Class**: `EmbeddingSemanticChunker(ChunkingStrategy)`
- **Registration**: `ChunkingEngine.register_chunker("embedding_semantic", instance)`
- **Tests**: `tests/unit/agentic_core/knowledge/chunking/test_embedding_semantic_chunker.py` (29 tests, all passing)
- **Ablation harness**: `tools/eval/ragbench_runner.py` with synthetic
  TechQA-schema fixture at `data/eval/golden/ragbench_techqa_synthetic.jsonl`.
  Real RAGBench TechQA data can be dropped in at the same path with no
  code changes.

### Breakpoint mode defaults (match LangChain)

| Mode | Default threshold | Cutoff rule |
|---|---|---|
| `percentile` | 95.0 | distance > P95(distances) |
| `stdev` | 3.0 | distance > mean + 3·σ |
| `iqr` | 1.5 | distance > Q3 + 1.5·IQR |
| `gradient` | 95.0 | \|Δd\| > P95(\|Δd\|) |

### Min/max clamping

`min_chunk_chars` merges too-small runs forward; `max_chunk_chars` splits
too-large runs at sentence boundaries regardless of similarity. Defaults
are 100 and 2000 characters respectively.

## Consequences

**Positive:**
- Closes the Sarkar Part 1 Technique #2 gap.
- Harness in `tools/eval/ragbench_runner.py` now produces the 5-approach
  head-to-head table on demand; provides a reproducible anchor to the
  blog's methodology.
- Injectable embedder means unit tests run in < 1 s with no model load.

**Negative / trade-offs:**
- Production use requires a real embedder (BGE-m3 or equivalent); cold
  start is paid once per engine.
- Synthetic fixture produces near-ceiling numbers (Hit@5 = 1.0 across
  approaches) because it is designed for plumbing verification, not
  discrimination. Real RAGBench data needed for meaningful ablation
  numbers.

**Follow-ups (deferred):**
- Wire BGE-m3 embedder into `ChunkingEngine` bootstrap so
  `"embedding_semantic"` is usable without explicit registration.
- Vendor real RAGBench TechQA 50-query subset (license review required).
- Add a 6th ablation row for Contextual Retrieval (ADR-045) to quantify
  its uplift on the same benchmark.

## Links

- ADR-045 — Contextual Retrieval (Anthropic)
- ADR-046 — Rerank Revival
- Plan: `.claude/plans/rag-semantic-chunker-gap-c4f1a8.md`
- Report: `docs/reports/rag/ragbench_ablation_20260424.md`
- External: Sarkar (2026) "The Right Chunk, Wrong Context Problem" —
  https://arnabksarkar.github.io/blogs/rag-part1.html
- External: Anthropic (Sept 2024) "Introducing Contextual Retrieval" —
  https://www.anthropic.com/news/contextual-retrieval
- External: Jina (2024) "Late Chunking" — arXiv 2409.04701
- External: Friel et al. (2024) "RAGBench" — arXiv 2407.11005
