---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-intake-rag-enrichment-c5e8d2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-intake-rag-enrichment-c5e8d2.md'
source_sha256: 20b24fc1b7b2afb2f5535710008b649c0f8379a730284d5bd09359480b6fd411
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna Wave 3 — Vector RAG Enrichment at Template Time

**Slug**: `apps-qna-intake-rag-enrichment-c5e8d2`
**Status**: not-started (scaffold only)
**Owner**: TBD
**Created**: 2026-04-30
**Parent**: Wave 1 of `apps_qna` intake architecture
**Depends on**: Wave 2 (LLM extraction) is **not** required, but improves quality

## Goal

Embed the research brief, JD, and interviewer profiles into a per-interview
ChromaDB collection (via the `vector_db` MCP). Card templates gain a Jinja
helper `{{ rag_lookup("query", k=3) }}` that retrieves relevant chunks at
build time, letting cards 04 (Company Overlay), 05 (Architecture), 08
(Governance), 21 (Likely Questions) etc. surface content grounded in the
actual research substance — not just the typed YAML structure.

This is the actual RAG pattern from Anthropic's Skills/Rules playbook:
Rules (always-on) provide the spine; Skills (route-loaded) provide the
focused context; RAG retrieval grounds Skills in the source material.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|------------:|--------|
| 0 | 0.1 | Determinism + test-fixture decisions | 2000 | Todo |
| 1 | 1.1, 1.2 | Per-interview embedding pipeline | 4000 | Todo |
| 2 | 2.1 | Jinja `rag_lookup` helper + template wiring | 3000 | Todo |
| 3 | 3.1 | SemanticRouter + RAG: auto-populate likely_questions | 2000 | Todo |
| 4 | 4.1 | Eval: do RAG-grounded cards beat typed-YAML-only cards? | 3000 | Todo |

**Total est. tokens**: ~14k

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|------------:|--------|
| 0.1 | Test determinism plan | New ADR or doc decision | ChromaDB embeddings change between releases; tests need to either (a) freeze a model, (b) mock the MCP, (c) snapshot embeddings | 2000 | Todo |
| 1.1 | Embedding pipeline | `apps_qna/rag/embed_pipeline.py` | Chunk size, stride, embedding model selection, MCP failure mode at build time | 2000 | Todo |
| 1.2 | Per-interview collection naming | `apps_qna/rag/collection_name.py` | Slug-derived naming; collection eviction policy | 2000 | Todo |
| 2.1 | Jinja helper | `apps_qna/builder/rag_jinja.py` registered in CardPackBuilder env | Failure mode when MCP is down; cache to make builds reproducible within a session | 3000 | Todo |
| 3.1 | Auto-populate likely_questions | `apps_qna/integrations/from_jd.py` + `from_research_brief.py` enriched | SemanticRouter (already shipped) scores JD-derived questions against routes; populates card 21 | 2000 | Todo |
| 4.1 | RAG vs no-RAG eval | `apps_qna/tests/eval/rag_quality_eval.py` | Need a quality metric — judge the cards against a reference set | 3000 | Todo |

## Gap Register

- **G-RAG-1**: Build-time MCP dependency is non-trivial. Today the build is a pure-Python in-process operation. Adding an MCP call at build time means tests need either MCP-up or mocked-MCP.
- **G-RAG-2**: Embeddings must be deterministic for reproducible test fixtures. ChromaDB defaults to a SaaS-grade embedding model that may evolve. We need a frozen-model contract.
- **G-RAG-3**: When the MCP is unavailable, what's the build behavior? Fail loud? Silently fall back to no-RAG mode? The latter is dangerous (cards quietly degrade); the former breaks builds when ops issues occur.
- **G-RAG-4**: Jinja `rag_lookup` is a side-effecting template call. Standard Jinja templates are pure functions of context. We're widening the contract.

## Architecture sketch

```text
Wizard / build-time
    │
    ▼
Embedding pipeline (apps_qna/rag/embed_pipeline.py)
    │ chunks: research_brief + JD + each interviewer profile
    ▼
vector_db MCP (per-interview collection: qna__<slug>)
    │
    ▼
CardPackBuilder.build()
    │ Jinja env has registered helper rag_lookup(query, k=3)
    ▼
Template render — e.g. card 04:
    {% set company_anchors = rag_lookup("company decisioning anchors", k=3) %}
    {% for chunk in company_anchors %}- {{ chunk }}{% endfor %}
    │
    ▼
Card with grounded content
```

## Dependencies

- Wave 1 (typed adapters) — delivered and stable
- `vector_db` MCP server — already in mcp_config.json
- SemanticRouter (Wave 6, delivered) — used by phase 3.1

## Out-of-Scope (NEXT_STEP)

- Cross-interview RAG (sharing chunks across packs)
- Live re-embedding when the JD changes
- Reranking (cosine alone is fine for v1)
