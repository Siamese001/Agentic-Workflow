# RAGBench Ablation — 6-Approach Head-to-Head

Generated: 2026-04-24 22:45:32 UTC
Fixture: `C:/Git/Agentic-Workflow/data/eval/golden/ragbench_techqa_synthetic.jsonl`
Queries: 25
Top-K: 5

| Approach | Hit@5 | MRR@5 |
|---|---|---|
| 1. Naive fixed-size (200/50) + vector | 1.000 | 0.933 |
| 2. + Embedding-cosine semantic chunking | 1.000 | 0.940 |
| 3. + Hybrid (vector + BM25, RRF) | 1.000 | 0.960 |
| 4. + Cross-encoder-style rerank | 1.000 | 1.000 |
| 5. + Parent-child hydration | 1.000 | 1.000 |
| 6. + Contextual Retrieval (Anthropic, ADR-045) | 1.000 | 1.000 |

## Notes

- **Embedder**: deterministic 256-dim bag-of-words (hash-bucketed). Swap for BGE-m3 via a pluggable embedder to match production numbers.
- **Reranker**: token-overlap + cosine composite. Stands in for `ms-marco-MiniLM-L-6-v2` / `BAAI/bge-reranker-v2-m3`.
- **Hybrid**: Reciprocal Rank Fusion with k=60 (matches `hybrid_search_engine.RRF_K`).
- **Parent-child hydration**: deduplicates ranked list by `metadata.parent_id` and returns the parent passage id for scoring.
- **Gap from Sarkar blog**: blog used real `all-MiniLM-L6-v2` on RAGBench TechQA 50 queries. This harness is the plumbing — point `--fixture` at the real RAGBench JSONL and swap the embedder to match numbers.
