# Operator Runbook — curated_agent_docs Collection

**Status**: Production-ready · **Last validated**: 2025-07 (v5 — Phase 4 authority enforcement)  
**Collection name**: `curated_agent_docs` · **Embedding model**: `BAAI/bge-m3` (1024-dim)  
**ChromaDB path**: `data/cache/chromadb` · **Total chunks**: 579

---

## 1. Collection Overview

`curated_agent_docs` is a hand-curated, high-signal ChromaDB collection containing 32 sources across
6 topic buckets. It is authoritative for architecture, orchestration, safety/eval, best-practice, and
tool-contract (MCP/FastMCP) queries. It does NOT replace `arch_docs` (broad repo coverage) or
`ext_knowledge` (external web scrapes) — it is a focused routing target.

| Bucket          | Sources | Chunks | v3 change |
|-----------------|---------|--------|-----------|
| arch_standards  | 7       | 111    | —         |
| orchestration   | 13      | 133    | +4 sources, +44 chunks (LangGraph, AutoGen, Anthropic patterns) |
| rag_retrieval   | 3       | 95     | —         |
| safety_eval     | 5       | 51     | —         |
| tool_contracts  | 3       | 171    | +2 sources, +136 chunks (MCP SDK README, OpenAI MCP doc) |
| observability   | 1       | 13     | — |

---

## 2. Rebuilding Each Collection

### 2a. `curated_agent_docs` (this collection)

```bash
# Full rebuild (drop + re-ingest)
python tools/generate/ingestion/ingest_curated_agent_docs.py

# Dry-run first (validates all sources, no Chroma writes)
python tools/generate/ingestion/ingest_curated_agent_docs.py --dry-run

# Expected output:
#   Sources evaluated : 34  (excluded: 5)
#   Total chunks      : 574
#   Required OK/FAIL  : 19/0
#   Optional FAIL     : 2  (models.md fetch failed; subagent.ipynb 404)
#   Dedup collisions  : 0
#   DRY-RUN PASS — all required sources available.
```

**Ingestion is idempotent** — re-running upserts existing chunks (no-op) and adds new ones.
The collection will NOT be deleted between runs unless you explicitly call `client.delete_collection("curated_agent_docs")`.

### 2b. `arch_docs` (broad internal repo coverage)

```bash
python tools/generate/ingestion/ingest_arch_docs.py
```

Scans `docs/`, `AGENTS.md`, `README.md`. Covers 8840+ chunks from all internal markdown.
Run after any significant documentation restructure.

### 2c. `ext_knowledge` (external web scrapes)

```bash
python tools/generate/ingestion/ingest_ext_knowledge.py
python tools/generate/ingestion/ingest_agent_framework_docs.py
```

Fetches external URLs (Anthropic, OpenAI agents, LangChain). Rate-limited; expect 5–15 min.
External sources may return 403/404 — check output for failures.

---

## 3. Validating Metadata Population

### 3a. Quick schema check

```bash
python -c "
import chromadb, json
c = chromadb.PersistentClient('data/cache/chromadb')
col = c.get_collection('curated_agent_docs')
r = col.get(limit=3, include=['metadatas'])
for m in r['metadatas']:
    print(json.dumps(m, indent=2))
print('Total:', col.count(), 'docs')
"
```

**Required fields** (all chunks must have these):

| Field             | Expected values / type                |
|-------------------|---------------------------------------|
| `canonical`       | `True` (all curated sources are canonical) |
| `authority_level` | float 0.7–1.0                         |
| `topic_bucket`    | one of: arch_standards, orchestration, rag_retrieval, safety_eval, observability, tool_contracts |
| `doc_family`      | one of: adr, standard, guide, reference |
| `source_url`      | non-empty string (local path or https URL) |
| `heading_path`    | section breadcrumb or "no-headings"   |
| `chunk_index`     | int ≥ 0                               |

### 3b. Automated metadata audit

```bash
python -c "
import chromadb
c = chromadb.PersistentClient('data/cache/chromadb')
col = c.get_collection('curated_agent_docs')
r = col.get(include=['metadatas'])
required = {'canonical','authority_level','topic_bucket','doc_family','source_url','heading_path','chunk_index'}
missing_any = [m for m in r['metadatas'] if not required.issubset(m.keys())]
non_canonical = [m for m in r['metadatas'] if not m.get('canonical')]
low_auth = [m for m in r['metadatas'] if float(m.get('authority_level', 0)) < 0.70]
print(f'Total: {len(r[\"metadatas\"])} | Missing fields: {len(missing_any)} | Non-canonical: {len(non_canonical)} | Low authority: {len(low_auth)}')
# All three should be 0 for a healthy collection.
"
```

**Healthy output**: `Missing fields: 0 | Non-canonical: 0 | Low authority: 0`

---

## 4. Running the Regression Harness

```bash
# Quick run (outputs to stdout + writes report files)
python tools/eval/retrieval_eval_curated.py --k 5 --out docs/reports/retrieval_eval_curated.md

# Live-path run (simulates HybridSearchEngine authority rerank + collapse_group_dedup — v5 benchmark)
python tools/eval/retrieval_eval_curated.py --k 5 --live-path --out docs/reports/retrieval_eval_curated_v5.md

# Output files:
#   docs/reports/retrieval_eval_curated_v5.md   — markdown report (7 sections incl. Phase 4 gate)
#   docs/reports/retrieval_eval_curated_v5.json — per-query raw metrics (40 × 3 = 120 rows)

# Expected pass thresholds (fail if worse than) — v5 live-path benchmark:
#   curated overall win rate          : ≥ 95%  (v5 achieved 97%)
#   arch/policy/history wins          : ≥ 85%
#   best-practice wins                : = 100%
#   tooling/MCP wins                  : = 100%
#   canonical_hit_rate (curated)      : = 1.000
#   tooling_contamination (curated)   : = 0.000
#   arch_docs_contamination (normative classes): = 0  ← Phase 4 gate
```

**Runtime**: ~15s on GPU, ~60s on CPU (40 queries × 3 collections, model load included).

### Interpreting results

| Metric         | What it measures                                         |
|----------------|----------------------------------------------------------|
| MRR (dist<0.35)| First highly-relevant hit rank — quality signal          |
| dist@1         | Cosine distance of top hit (lower = better match)        |
| canonical_hit  | Fraction of top-K from canonical sources (should be 1.0 for curated) |
| authority      | Mean authority_level of top-K results                    |
| arch_depth     | Fraction of top-K tagged as arch-relevant by metadata    |
| bp_relevance   | Fraction tagged as best-practice relevant                |
| redundancy     | Fraction where same source_url appears >1× in top-K     |
| source_div     | Unique doc_family count in top-K                         |
| tooling_contam | Fraction of results from code/tooling artifacts (should be 0 for arch queries) |

---

## 5. Failure Patterns to Watch For

### F1: Required source fetch failure
**Symptom**: `Required OK/FAIL : X/1` or more in dry-run output.  
**Cause**: External URL returned 403/404, or internal file path deleted/moved.  
**Fix**: Update the `path` in `CURATED_SOURCES` in `ingest_curated_agent_docs.py`. Re-run dry-run first.

### F2: Dedup collisions > 0
**Symptom**: `Dedup collisions: N` in dry-run report.  
**Cause**: Same (source_url, heading_path, chunk_index) appears in two distinct CURATED_SOURCES entries.  
**Fix**: Remove the duplicate entry from `CURATED_SOURCES`. The collapse_group field documents intentional clusters.

### F3: Redundancy rate > 0.5 in eval
**Symptom**: `redundancy_rate` column > 0.50 for `curated_agent_docs` in eval report.  
**Cause**: Multiple sources pointing to the same URL, or very large documents producing many chunks from one source dominating top-K.  
**Fix**: Check for duplicate paths in CURATED_SOURCES. Consider adding a `max_chunks_per_source` guard in `ingest_curated_agent_docs.py`.

### F4: Canonical hit rate drops below 1.0
**Symptom**: `canonical_hit_rate` < 1.000 for `curated_agent_docs`.  
**Cause**: A source was added to CURATED_SOURCES with `canonical=False`.  
**Fix**: All curated sources must be canonical. Set `canonical: True` for any new entry, or add it to `EXCLUDED_SOURCES`.

### F5: Overall win rate drops below 95%
**Symptom**: Eval harness reports `All queries: X/40 (Y%)` where Y < 95.  
**Cause A**: arch_docs was rebuilt WITHOUT Phase 0 authority metadata (`invalid_for_normative_use`, `source_collection`, etc.), causing `_is_canonical` in the eval harness to over-count arch_docs as canonical, boosting its win_score.  
**Fix A**: Re-run `ingest_arch_docs.py` with Phase 0 metadata fields intact. Verify `arch_docs canonical_hit_rate` ≤ 0.10 in the report. The eval harness `_is_canonical` gates on `invalid_for_normative_use=True` (Phase 4 guard).  
**Cause B**: A high-signal curated source was removed or fetched at a stale URL.  
**Fix B**: Check dry-run output for `Required FAIL` entries. Restore missing sources.

### F9: arch_docs_contamination > 0 for normative query classes
**Symptom**: Section 6 of the v5+ report shows FAIL rows for policy, tooling, or standards queries.  
**Cause**: arch_docs chunks with `source_collection=arch_docs` appeared in curated_agent_docs top-K. This should be impossible (separate collections) unless the collection was rebuilt from a wrong source.  
**Fix**: Verify `curated_agent_docs` contains only sources from `CURATED_SOURCES`. Check that no arch_docs were accidentally ingested into curated collection. Re-run ingestion if necessary.

### F6: POLICY category wins drop (UWG / C0 / determinism queries)
**Symptom**: arch_docs starts winning POLICY-01, POLICY-04 consistently.  
**Cause**: `.windsurf/rules/constitutional.md` or `global_rules.md` were removed or significantly rewritten.  
**Fix**: These are scored 0.88 and 0.82 in CURATED_SOURCES and are marked `required=True`. Dry-run will catch removals. If content changed, re-run ingestion.

### F8: POLICY-05 regressed (constitutional hard constraints query)
**Symptom**: POLICY-05 wins for arch_docs after adding new orchestration pattern docs.  
**Cause**: Anthropic/LangGraph/AutoGen pattern docs surface for "constraints" queries, diluting constitutional.md signal in top-K.  
**Fix**: Apply `collapse_group_dedup(max_per_group=2)` in `HybridSearchEngine` before returning results for `tool_contracts` and `best_practice` routed queries. This caps Anthropic pattern cluster at 2 slots, letting constitutional.md surface.

### F7: Embedding model mismatch
**Symptom**: `IngestionError: Model dim mismatch: got X, expected 1024`.  
**Cause**: EMBEDDING_MODEL changed or a different model was loaded from cache.  
**Fix**: Ensure `BAAI/bge-m3` is the model at `tools/generate/ingestion/ingest_curated_agent_docs.py:EMBEDDING_MODEL`. The collection was built with 1024-dim embeddings — a dim change requires full rebuild.

---

## 6. Adding New Sources

1. Add entry to `CURATED_SOURCES` list in `ingest_curated_agent_docs.py`
2. Set all required fields: `source_type`, `path`, `title`, `doc_type`, `doc_family`, `topic_bucket`, `authority_level`, `canonical`, `collapse_group`, `keep_reason`, `score`, `required`
3. Score must be ≥ 0.77 (minimum surface threshold)
4. Run dry-run: `python tools/generate/ingestion/ingest_curated_agent_docs.py --dry-run`
5. Verify chunk count in source details (expect 5–50 chunks per source)
6. Run live ingestion
7. Re-run regression harness to confirm no regression

---

## 7. Collection Routing Recommendation

```
Query category                  → Primary collection    → Routing domain key
─────────────────────────────────────────────────────────────────
architecture / best-practice    → curated_agent_docs    → architecture
policy / safety / eval          → curated_agent_docs    → architecture
ADR / standards / history       → curated_agent_docs    → architecture
orchestration / multi-agent     → curated_agent_docs    → best_practice
retrieval / embedding / RAG     → curated_agent_docs    → best_practice
MCP / FastMCP / tool contracts  → curated_agent_docs    → tool_contracts  ← NEW (v3)
external framework docs         → curated_agent_docs    → best_practice
code / symbol lookup            → arch_docs             → code
```

Routing is implemented in `query_router.py` via `QueryIntentDetector.detect_topic_domain()`.  
Apply `collapse_group_dedup(max_per_group=2)` from `evidence_shaper.py` for `tool_contracts` and `best_practice` routed results to suppress MCP SDK cluster redundancy.

See `query_router.py` for domain-aware collection routing implementation.
