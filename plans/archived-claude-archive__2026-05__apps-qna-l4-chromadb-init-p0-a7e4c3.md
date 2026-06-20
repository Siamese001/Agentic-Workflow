---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-qna-l4-chromadb-init-p0-a7e4c3.md'
original_relative_path: '_archive\\2026-05\\apps-qna-l4-chromadb-init-p0-a7e4c3.md'
source_sha256: 9f82ea121a1d4e289cc47e1d8c8da4c185ba4e8b79d77057260859207a120bd1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
description: P0 Critical - Initialize ChromaDB for apps_qna L4 semantic cache
tags: [P0, critical, chromadb, apps_qna, L4, semantic-cache, bge-m3]
status: Not Started
created: 2026-05-10
dependent_on: apps-embedding-gap-analysis-8f7d2e
blocks: apps-embedding-deferred-scope-f9a3b2
---

# P0: apps_qna L4 ChromaDB Cache Initialization

**Priority:** P0 — Critical  
**Impact:** Cache miss on every apps_qna request  
**Estimated Effort:** 2-3 days  
**Blocks:** apps-embedding-deferred-scope-f9a3b2

---

## Problem Statement

`NativePersistentCacheClient` in `agentic_core/L4_state/cache/gptcache_client.py` is configured to use ChromaDB at `artifacts/cache/l2/chroma`, but the directory **does not exist**. This causes:
- Cache initialization failure or fallback to in-memory only
- **Every request results in cache miss**
- No persistence across process restarts
- Token cost inefficiency

---

## Root Cause

From gap analysis W2/W3:
- Canonical path `artifacts/cache/l2/chroma` (per `VECTOR_CACHE_LAYOUT`) is empty
- ChromaDB persistent client cannot initialize without directory structure
- Code exists but storage layer is absent

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1-P1.3 | Directory setup + ChromaDB init | ~4,000 | Not Started | Directory exists, client initializes |
| W2 | P2.1-P2.3 | BGE-M3 collection creation | ~5,000 | Not Started | Collection with 1024-dim schema ready |
| W3 | P3.1-P3.3 | Integration + testing | ~4,000 | Not Started | Cache hits confirmed, zero regressions |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Create canonical directories | `agentic_core/L4_state/contracts/vector_cache_layout.py` | Directory permissions, path validation | ~1,000 | Not Started |
| P1.2 | Initialize ChromaDB client | `agentic_core/L4_state/cache/gptcache_client.py` | Client startup, error handling | ~1,500 | Not Started |
| P1.3 | Verify path resolution | `agentic_core/L4_state/config/chroma_paths.py` | CHROMA_PERSIST_DIR env override | ~1,500 | Not Started |
| P2.1 | Create semantic cache collection | ChromaDB persistent client | Collection schema, metadata fields | ~1,500 | Not Started |
| P2.2 | Configure BGE-M3 embedding function | `agentic_core/embeddings/bge_runtime.py` | Dimension validation (1024), normalization | ~2,000 | Not Started |
| P2.3 | Set similarity threshold | `apps_qna/config/domain_contract/cache_profiles.yaml` | 0.95 threshold alignment | ~1,500 | Not Started |
| P3.1 | Wire cache to apps_qna L4 | `apps_qna/` integration points | Adapter updates, config wiring | ~1,500 | Not Started |
| P3.2 | Functional testing | `tests/unit/L4_state/cache/` | Cache hit/miss validation | ~1,500 | Not Started |
| P3.3 | Load testing + smoke test | Integration test suite | Performance, no regression | ~1,000 | Not Started |

---

## Technical Specifications

### Collection Requirements

```yaml
collection_name: l2_semantic_cache
embedding_model: BAAI/bge-m3
dimension: 1024
normalization: L2
distance_metric: cosine
similarity_threshold: 0.95
```

### Required Metadata Fields

| Field | Type | Purpose |
|-------|------|---------|
| `tenant_id` | string | Multi-tenancy isolation |
| `route_id` | string | Route family tracking |
| `query_hash` | string | Exact lookup key |
| `timestamp` | int64 | LRU eviction support |
| `app_id` | string | apps_qna identification |
| `hit_count` | int | Usage analytics |

### Storage Layout

```
artifacts/cache/l2/
├── l2_cache.db           # SQLite scalar store (existing pattern)
└── chroma/               # ChromaDB persistent storage (NEW)
    ├── chroma.sqlite3
    └── *.bin
```

---

## Implementation Steps

### W1: Directory Setup + ChromaDB Init

**P1.1: Create canonical directories**
```python
# Ensure VECTOR_CACHE_LAYOUT.ensure_directories() is called
from agentic_core.L4_state.contracts.vector_cache_layout import VECTOR_CACHE_LAYOUT
VECTOR_CACHE_LAYOUT.ensure_directories()
```

**P1.2: Initialize ChromaDB client**
```python
# In gptcache_client.py _init_cache()
self._chroma_client = chromadb.PersistentClient(path=str(chroma_path))
self._chroma_collection = self._get_or_create_bgem3_collection()
```

**P1.3: Verify path resolution**
- Test with `CHROMA_PERSIST_DIR` env override
- Test default path resolution
- Validate on Windows + WSL paths

### W2: BGE-M3 Collection Creation

**P2.1: Create semantic cache collection**
```python
collection = self._chroma_client.get_or_create_collection(
    name="l2_semantic_cache",
    embedding_function=embedding_function,  # BGE-M3
    metadata={"hnsw:space": "cosine"}
)
```

**P2.2: Configure BGE-M3 embedding function**
```python
from agentic_core.embeddings.bge_runtime import bge_embed_batch
# Wrap for ChromaDB compatibility
```

**P2.3: Align similarity threshold**
- Read from `cache_profiles.yaml`: `similarity_threshold: 0.95`
- Configure ChromaDB query with `n_results=1, where={"$and": [{"score": {"$gte": 0.95}}]}`

### W3: Integration + Testing

**P3.1: Wire cache to apps_qna L4**
- Verify `apps_qna` uses `NativePersistentCacheClient` via L4 state layer
- Confirm cache lookups in request path

**P3.2: Functional testing**
```python
# Test cache hit
result1 = cache.get(query="test query")
result2 = cache.get(query="test query")  # Should be cache hit
assert result1 == result2
```

**P3.3: Load testing + smoke test**
```bash
python -m pytest tests/unit/L4_state/cache/ -v
python -m apps_qna --smoke-test  # Verify end-to-end
```

---

## Acceptance Criteria

| Criterion | Verification Method |
|-----------|---------------------|
| Directory `artifacts/cache/l2/chroma` exists | `ls -la artifacts/cache/l2/` |
| ChromaDB client initializes without error | Unit test: `test_chroma_client_init` |
| Collection `l2_semantic_cache` queryable | `client.list_collections()` includes it |
| BGE-M3 dimension 1024 enforced | Assertion in embedding function |
| Cache hit observed in request flow | OTEL span shows `cache_hit=true` |
| No regression in apps_qna functionality | Full smoke test suite passes |
| Token cost reduced (cache effectiveness) | Metrics show >10% hit rate |

---

## Rollback Strategy

1. **Code rollback:** Revert to in-memory cache only via config flag
2. **Data preservation:** Keep ChromaDB files, disable reads
3. **Fallback path:** If ChromaDB fails, gracefully degrade to SQLite-only or in-memory

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ChromaDB disk corruption | SQLite WAL mode, periodic backups |
| BGE-M3 model load failure | Lazy loading with timeout, CPU fallback |
| Permission errors on Windows | Test with standard user permissions |
| Similarity threshold mismatch | Configurable via cache_profiles.yaml |

---

## Verification Commands

```bash
# W1 verification
python -c "from agentic_core.L4_state.contracts.vector_cache_layout import VECTOR_CACHE_LAYOUT; print(VECTOR_CACHE_LAYOUT.validate_cache_layout('artifacts/cache/l2'))"

# W2 verification
python -c "import chromadb; c = chromadb.PersistentClient(path='artifacts/cache/l2/chroma'); print([col.name for col in c.list_collections()])"

# W3 verification
python -m pytest tests/unit/L4_state/cache/test_gptcache_client.py -v -k "test_cache_hit"
python -m apps_qna --smoke-test --verify-cache
```

---

## Post-Completion

**After this plan completes:**
1. Update `apps-embedding-deferred-scope-f9a3b2` status to **Not Started** (unblocks)
2. Notify dependent plan owner
3. Archive P0 artifacts for reference

---

## Dependencies

**Requires:**
- apps-embedding-gap-analysis-8f7d2e (gap identification) ✅ COMPLETED
- BGE-M3 model available in `agentic_core/embeddings/bge_runtime.py` ✅ EXISTS
- ChromaDB 1.5.5+ installed ✅ VERIFIED

**Blocks:**
- apps-embedding-deferred-scope-f9a3b2 (deferred scope) 🟠 WAITING

---

## Definition of Done

- [ ] DoD-1: Directory `artifacts/cache/l2/chroma` exists and is writable
- [ ] DoD-2: ChromaDB client initializes without error in production path
- [ ] DoD-3: Collection `l2_semantic_cache` created with BGE-M3 embedding function
- [ ] DoD-4: 1024-dim vectors validated on add/query
- [ ] DoD-5: apps_qna requests show cache hits in OTEL traces
- [ ] DoD-6: Smoke test passes: `python -m apps_qna --smoke-test`
- [ ] DoD-7: No regression in existing test suite
- [ ] DoD-8: Token cost metrics show improvement
- [ ] DoD-9: Rollback procedure tested and documented
- [ ] DoD-10: Handoff document created for operations team

---

AG_QUEUE_SEED: plan=apps-qna-l4-chromadb-init-p0-a7e4c3 id=p0-init-start depends_on=apps-embedding-gap-analysis-8f7d2e title="P0: Initialize ChromaDB for apps_qna L4 cache"
