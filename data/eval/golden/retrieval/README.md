# Retrieval Golden Set

Per ADR-061. One JSONL file per corpus, one row per query. Schema:

```json
{
  "query_id": "code-001",
  "query": "How does the reranker factory pick the backend?",
  "intent_class": "code_concept",
  "expected_chunks": ["agentic_core/knowledge/retrieval/reranker_factory.py:52-67"],
  "expected_answer_summary": "RERANKER env: auto/heuristic/cross_encoder/none.",
  "negative_chunks": [],
  "tags": ["retrieval", "factory", "env_driven"],
  "added_at": "2026-04-24",
  "curator": "AA"
}
```

## Files

| File | Target size (v1) | Status |
|---|---:|---|
| `code.jsonl` | 80 pairs | seed (3 pairs) |
| `docs.jsonl` | 60 pairs | not yet curated |
| `tests.jsonl` | 30 pairs | not yet curated |
| `traces.jsonl` | 20 pairs | not yet curated |
| `incidents_rca.jsonl` | 20 pairs | not yet curated |

Curation is owned by the W5.1 implementation plan
(`adr-061-golden-set-curation`) per the parent plan's NEXT_STEP markers.
This directory ships a seed so the harness can exercise its plumbing
against real shape immediately.

## Refresh cadence

Quarterly. Stale rows (where the canonical chunk has changed substantially)
are flagged by W5.3's drift metric and re-curated.
