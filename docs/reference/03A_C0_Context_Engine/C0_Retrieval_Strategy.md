# C0 Grounding Retrieval Strategy

> ADR-102 companion. Production retrieval strategy for C0 Context Engine.
> Status: ACCEPTED. Date: 2026-05-07.

## Strategy Overview

C0 grounding retrieves evidence to support or refute claims made by L2 execution.
The strategy is multi-modal, budget-bound, and fail-closed.

| Dimension | Policy |
|-----------|--------|
| Default mode | Hybrid (dense + sparse + metadata) |
| Fallback mode | Dense-only if sparse index unavailable |
| Graph mode | ADG-backed, gated on seed_file_path |
| Budget floor | 512 tokens minimum |
| SLO budget | 5000ms default, configurable per route |
| Weak support | Refine once, then caveat |
| Cache policy | Read-through with D2 semantic cache |

## Retrieval Modes

1. **Hybrid (default)**: Dense (BGE-M3 via ChromaDB) + Sparse (BM25 via SQLite FTS5) + Metadata filters. Fusion: RRF with k=60.
2. **Dense-only**: BGE-M3 embeddings with cosine similarity. Used when sparse index unavailable.
3. **Sparse-only**: BM25 over tokenized content. Used for exact-match queries.
4. **Graph (ADG)**: Traverses ADG dependency graph up to max_graph_hops. Gated on seed_file_path.

## Pipeline Stages

| Stage | Name | Description |
|-------|------|-------------|
| C0.0 | Preflight | Eligibility check |
| C0.1 | Plan | Build bounded RetrievalPlan |
| C0.2 | Recall | Execute hybrid/dense/sparse/graph recall |
| C0.3 | Hydrate | Expand parent-child references |
| C0.4 | Validate | Run quality gates + contradiction detection |
| C0.5 | Shape | Format evidence for prompt assembly |
| C0.6 | Refine | Optional second pass on weak support |

## Quality Gates

| Gate | Threshold | Action on Fail |
|------|-----------|----------------|
| G1 Authority | authority_score >= 0.3 | Drop item |
| G2 Freshness | within freshness_rule band | Downgrade to STALE |
| G3 Coverage | >= 1 item per claim | Flag UNRESOLVED_GAP |
| G4 Contradiction | severity < 0.7 | Flag CONTRADICTION |
| G5 Citation | citation_stability >= 0.5 | Downgrade confidence |

## Integration Points

- apps_rg: C0 retrieves company research + job description context
- apps_qna: C0 retrieves interview templates + experience library
- apps_research: C0 retrieves web evidence for company briefs
- apps_lic: C0 retrieves outreach context + recipient research

## References

- Schema: agentic_core/L1_cognition/c0_context/types.py
- Preflight: agentic_core/L1_cognition/c0_context/preflight.py
- Dispatcher: agentic_core/L0_routing/c0_retrieval/dispatcher.py
- Recall: agentic_core/knowledge/retrieval/hybrid_recall_stage.py
