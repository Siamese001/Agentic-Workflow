# Operator Runbook — Wave B2 Collection Topology

**Status**: Active (Wave B2) · **Last validated**: 2026-07 (Wave B2 topology refactor)
**Collections**: `ext_authority`, `repo_evidence`, `ext_raw` · **Embedding model**: `BAAI/bge-m3` (1024-dim)
**ChromaDB path**: `data/cache/chromadb`

> **RETIRED collections**: `curated_agent_docs`, `arch_docs`, `ext_knowledge` — do NOT rebuild these
> against a Wave B2 ChromaDB store. Their ingestion scripts carry a `# RETIRED` header.
> See `docs/requirements/wave_b_chromadb_topology.md` for the full topology design.

---

## 1. Collection Overview (Wave B2)

Wave B2 replaces the single `curated_agent_docs` collection with three purpose-built collections:

| Collection | Lane | source_band | Authority | Script |
|------------|------|-------------|-----------|--------|
| `ext_authority` | A + B | `target_state_authority`, `supporting_guidance` | T2/T3 | `ingest_ext_authority.py` |
| `repo_evidence` | C + D | `repo_canonical`, `repo_implementation` | T4c/T4e | `ingest_repo_evidence.py` |
| `ext_raw` | E | `unvetted` | T5 | `ingest_ext_knowledge.py` |

**Routing rules (Wave B2)**:
- Normative requirements  → `ext_authority` only
- Best-practice / guidance → `ext_authority` (Lane B)
- Repo evidence / ADR lookup → `repo_evidence` (Lane C)
- Implementation search → `repo_evidence` (Lane D)
- Unvetted background → `ext_raw` (excluded from normative bundles)

---

## 2. Rebuilding Each Collection (Wave B2)

### 2a. `ext_authority` — vetted external web sources (Lanes A + B)

```bash
# Dry-run first (validates all 18 sources, no Chroma writes)
python tools/generate/ingestion/ingest_ext_authority.py --dry-run

# Full rebuild
python tools/generate/ingestion/ingest_ext_authority.py

# Expected output:
#   Collecting 18 ext_authority sources ...
#   Required OK/FAIL  : 5/0
#   After dedup: N unique chunks
```

Run after: any update to EXT_AUTHORITY_SOURCES catalogue, or after MCP SDK README changes.

### 2b. `repo_evidence` — repo-internal evidence (Lanes C + D)

```bash
# Dry-run first
python tools/generate/ingestion/ingest_repo_evidence.py --dry-run

# Full rebuild
python tools/generate/ingestion/ingest_repo_evidence.py

# Expected output:
#   Lane C: N chunks from 16 sources
#   Lane D: M chunks from docs/ scan
#   Total collected: N+M chunks
```

Run after: any significant documentation restructure in `docs/`, ADR additions, or AGENTS.md changes.

### 2c. `ext_raw` — unvetted scraped content (Lane E)

```bash
# IMPORTANT: Run 2a first so URL dedup is populated.
python tools/generate/ingestion/ingest_ext_knowledge.py --dry-run
python tools/generate/ingestion/ingest_ext_knowledge.py

# Expected output:
#   ext_authority URL dedup set: N URLs
#   Total collected: M documents (ext_authority dedup removed K)
```

Fetches from `agentic_best_practices` ChromaDB + disk. URL dedup removes content already in `ext_authority`.

---

## 3. Validating Metadata Population

### 3a. Quick schema check

```bash
python -c "
import chromadb, json
c = chromadb.PersistentClient('data/cache/chromadb')
col = c.get_collection('ext_authority')  # or repo_evidence / ext_raw
r = col.get(limit=3, include=['metadatas'])
for m in r['metadatas']:
    print(json.dumps(m, indent=2))
print('Total:', col.count(), 'docs')
"
```

**Required fields** (all chunks must have these — Wave B2 contract):

| Field                      | Expected values / type                |
|----------------------------|---------------------------------------|
| `source_collection`        | `"ext_authority"` \| `"repo_evidence"` \| `"ext_raw"` |
| `source_band`              | `"target_state_authority"` \| `"supporting_guidance"` \| `"repo_canonical"` \| `"repo_implementation"` \| `"unvetted"` |
| `authority_tier`           | `"T2_standard"` \| `"T3_guidance"` \| `"T4_repo_canonical"` \| `"T4_implementation_evidence"` \| `"T5_unvetted"` |
| `normative_scope`          | `"external_authority"` \| `"repo_internal"` \| `"unvetted"` |
| `invalid_for_normative_use`| `True` \| `False` |
| `source_url`               | `https://` URL (ext_authority) or repo-relative path (repo_evidence) |
| `heading_path`             | section breadcrumb or `"no-headings"` |
| `chunk_index`              | int ≥ 0 |

### 3b. Automated metadata audit

```bash
python -c "
import chromadb, sys
c = chromadb.PersistentClient('data/cache/chromadb')
required = {'source_collection','source_band','authority_tier','normative_scope','invalid_for_normative_use','source_url','heading_path','chunk_index'}
for cname in ('ext_authority', 'repo_evidence', 'ext_raw'):
    col = c.get_collection(cname)
    r = col.get(include=['metadatas'])
    missing = [m for m in r['metadatas'] if not required.issubset(m.keys())]
    print(f'{cname}: {col.count()} docs | Missing fields: {len(missing)}')
"
```

**Healthy output**: `Missing fields: 0` for each collection.

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
**Fix**: Update the `path` in `EXT_AUTHORITY_SOURCES` in `ingest_ext_authority.py` or `REPO_CANONICAL_SOURCES` in `ingest_repo_evidence.py`. Re-run dry-run first.

### F2: Dedup collisions > 0
**Symptom**: `Dedup collisions: N` in dry-run report.
**Cause**: Same (source_url, heading_path, chunk_index) appears in two distinct CURATED_SOURCES entries.
**Fix**: Remove the duplicate entry from `EXT_AUTHORITY_SOURCES` or `REPO_CANONICAL_SOURCES`. The `collapse_group` field documents intentional clusters.

### F3: Redundancy rate > 0.5 in eval
**Symptom**: `redundancy_rate` column > 0.50 for `ext_authority` in eval report.
**Cause**: Multiple sources pointing to the same URL, or very large documents producing many chunks from one source dominating top-K.
**Fix**: Check for duplicate paths in `EXT_AUTHORITY_SOURCES`. Consider adding a `max_chunks_per_source` guard in `ingest_ext_authority.py`.

### F4: Normative-use gate incorrect
**Symptom**: `invalid_for_normative_use=True` chunks appearing in normative bundles for `ext_authority`.
**Cause**: A source was added to CURATED_SOURCES with `canonical=False`.
**Fix (Wave B2)**: All ext_authority sources are normative by construction (`invalid_for_normative_use=False`). Remove any source with mismatched `source_band` or add it to the excluded section.

### F5: Overall win rate drops below 95%
**Symptom**: Eval harness reports `All queries: X/40 (Y%)` where Y < 95.
**Cause A**: arch_docs was rebuilt WITHOUT Phase 0 authority metadata (`invalid_for_normative_use`, `source_collection`, etc.), causing `_is_canonical` in the eval harness to over-count arch_docs as canonical, boosting its win_score.
**Fix A**: Re-run `ingest_repo_evidence.py` to restore `repo_evidence` with correct `invalid_for_normative_use=True` on all Lane D chunks.
**Cause B**: A high-signal ext_authority source was removed or fetched at a stale URL.
**Fix B**: Check dry-run output for `Required FAIL` entries in `ingest_ext_authority.py`. Restore missing sources.

### F9: arch_docs_contamination > 0 for normative query classes
**Symptom**: `ext_authority` chunks from repo-evidence or ext_raw appearing in normative bundles.
**Fix**: Verify `ext_authority` contains only sources from `EXT_AUTHORITY_SOURCES`. Check that no `repo_evidence` or `ext_raw` chunks were accidentally ingested into `ext_authority`.


### F6: POLICY category wins drop (UWG / C0 / determinism queries)
**Symptom**: arch_docs starts winning POLICY-01, POLICY-04 consistently.
**Cause**: `.codex/rules/constitutional.md` or `global_rules.md` were removed or significantly rewritten.
**Fix**: These are in `REPO_CANONICAL_SOURCES` in `ingest_repo_evidence.py` and are marked `required=True`. Dry-run will catch removals. If content changed, re-run ingestion.

### F8: POLICY-05 regressed (constitutional hard constraints query)
**Symptom**: POLICY-05 wins for arch_docs after adding new orchestration pattern docs.
**Cause**: Anthropic/LangGraph/AutoGen pattern docs surface for "constraints" queries, diluting constitutional.md signal in top-K.
**Fix**: Apply `collapse_group_dedup(max_per_group=2)` in `HybridSearchEngine` before returning results for `tool_contracts` and `best_practice` routed queries. This caps Anthropic pattern cluster at 2 slots, letting constitutional.md surface.

### F7: Embedding model mismatch
**Symptom**: `IngestionError: Model dim mismatch: got X, expected 1024`.
**Cause**: EMBEDDING_MODEL changed or a different model was loaded from cache.
**Fix**: Ensure `BAAI/bge-m3` is the model at all three ingestion scripts (`EMBEDDING_MODEL = "BAAI/bge-m3"`). The collections were built with 1024-dim embeddings — a dim change requires full rebuild of all three collections.

---

## 6. Adding New Sources (Wave B2)

### Adding to `ext_authority` (web sources)

1. Add entry to `EXT_AUTHORITY_SOURCES` in `ingest_ext_authority.py`
2. Required fields: `path` (https URL), `title`, `doc_type`, `doc_family`, `topic_bucket`, `collapse_group`, `required`
3. Source band is derived automatically by `_assign_source_band()` — add URL to `_LANE_A_URLS` if it is a T2_standard spec
4. Run dry-run: `python tools/generate/ingestion/ingest_ext_authority.py --dry-run`
5. Verify chunk count (expect 3–80 chunks per source)
6. Run live ingestion
7. Re-run regression harness to confirm no regression

### Adding to `repo_evidence` (local sources)

1. Add entry to `REPO_CANONICAL_SOURCES` in `ingest_repo_evidence.py`
2. Required fields: `path` (repo-relative), `title`, `doc_family`, `topic_bucket`, `collapse_group`, `required`
3. Run dry-run: `python tools/generate/ingestion/ingest_repo_evidence.py --dry-run`
4. Verify file exists and produces chunks
5. Run live ingestion

---

## 7. Collection Routing Recommendation (Wave B2)

```
Query category                  → Primary collection    → Routing domain key
─────────────────────────────────────────────────────────────────
architecture / best-practice    → ext_authority         → architecture
policy / safety / eval          → ext_authority         → architecture
ADR / standards / history       → repo_evidence (Lane C)→ internal_arch
orchestration / multi-agent     → ext_authority         → best_practice
retrieval / embedding / RAG     → ext_authority         → best_practice
MCP / FastMCP / tool contracts  → ext_authority         → tool_contracts
external framework docs         → ext_authority         → best_practice
repo implementation / ADG/code  → repo_evidence (Lane D)→ implementation
unvetted web background         → ext_raw               → (excluded from normative bundles)
```

Routing is implemented in `query_router.py` via `QueryIntentDetector.detect_topic_domain()`.
Apply `collapse_group_dedup(max_per_group=2)` from `evidence_shaper.py` for `tool_contracts` and `best_practice` routed results.

See `query_router.py` for domain-aware collection routing implementation.
