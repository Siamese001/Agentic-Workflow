---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\cache-r1ab-residuals-8c4e2a.md'
original_relative_path: 'cache-r1ab-residuals-8c4e2a.md'
source_sha256: 79e19caf85d45dcb3385eb263e0822d97a2202cba95e64a9fe7c09912d88291e
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Cache R1A/R1B — Residual Deferred Scope Plan

**Plan ID**: `cache-r1ab-residuals-8c4e2a`
**Status**: Todo
**Parent Work**: R1A + R1B activation wave (completed 2026-04-23, see session trajectory — `SEMANTIC CACHE L2 PATH: FULLY OPERATIONAL`, 7/7 cache tests passing)
**Tier**: T2 (multi-file, single layer L4)
**Author**: Cascade

---

## Context

R1A (exact cache writeback) and R1B (semantic cache routing) are **unambiguously alive** per session 2026-04-23:
- Top-of-`ExecutionOrchestrator.execute()` short-circuit proven: `test_execute_short_circuits_on_r1a_cache_hit` confirms 2nd identical call skips `_delegate_to_l3`.
- Isolation enforced on both Redis L1 and Chroma+SQLite L2 (via `_metadata` re-verification).
- Live probe passes: Chroma HNSW persists, L2→L1 writeback works, cleanup runs.

Three residual items surfaced during that wave are captured here. None block R1A/R1B runtime correctness — they are production-quality and tech-debt cleanups.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **F4** | F4.1, F4.2, F4.3 | Cache-layer polish (L4) | 6,500 | Todo | All three phases merged; cache tests stay 7/7 green; mypy clean on `semantic_cache_manager.py`; embedding uses real BGE-M3 in prod |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **F4.1** | L2 SQLite corpus/policy filter plumbing | `agentic_core/L4_state/cache/gptcache_client.py`, `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | L2 currently relies on post-query `_metadata` re-verification rather than a SQL `WHERE corpus_version=? AND policy_version=?` filter | 3,000 | Todo |
| **F4.2** | BGE-M3 real-model id | `agentic_core/L4_state/cache/gptcache_client.py:102`, env files, `semantic_cache_manager.py:_EMBEDDING_MODEL_VERSION` | HuggingFace id `sentence-transformers/bge-m3-v1` is invalid → falls back to MiniLM (384-dim, wrong embedding space vs spec 1024-dim) | 2,000 | Todo |
| **F4.3** | mypy + datetime hygiene | `semantic_cache_manager.py`, `gptcache_client.py`, `l1_exact_cache.py` | 15+ `None has no attribute setex/get` mypy errors from optional `redis_client`; `datetime.utcnow()` deprecated in 3 sites | 1,500 | Todo |

---

## Phase F4.1 — L2 SQLite corpus/policy filter plumbing

### Gap
Current flow:
1. `SemanticCacheManager.recall()` calls `_gptcache.get(query, tenant_id=..., embedding_model_id=...)`
2. `NativePersistentCacheClient.get()` queries ChromaDB and filters SQLite by `tenant_id` + `embedding_model_id` only
3. Row returned → caller re-verifies `_metadata.corpus_version` / `_metadata.policy_version` and suppresses if mismatch

This works but is defense-in-depth against the query plan, not the query plan itself. A SQL `WHERE` clause is O(index seek); a post-query filter is O(n) on returned rows.

### Fix
Extend `NativePersistentCacheClient.get()` signature to accept `corpus_version: str = ""` and `policy_version: str = ""`, add them to the SQLite `WHERE` clause when non-empty, remove the post-query re-verification in `semantic_cache_manager.py` (keep only the `namespace` check since Chroma doesn't store it).

### Success Criteria
- `test_populate_d2_cache_writes_isolation_fields` still passes
- Add new test: `test_l2_sqlite_filters_corpus_version` that stores under `corpus_a`, queries with `corpus_b`, asserts SQLite miss (not post-filter suppression)
- Log event changes from `l2_scope_mismatch:*` to `l2_sqlite_miss:*` for corpus/policy divergence

### Files In Scope
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/cache/gptcache_client.py:248-357`
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py:678-745`
- `@c:/Git/Agentic-Workflow/tests/integration/cache/test_l0_d2_semantic_cache_live.py` (new test)

---

## Phase F4.2 — BGE-M3 real-model id

### Gap
Every test run logs:
```
WARNING  sentence_transformers.SentenceTransformer: No sentence-transformers model found
  with name sentence-transformers/bge-m3-v1. Creating a new one with mean pooling.
WARNING  agentic_core.L4_state.cache.gptcache_client: L2_CACHE:
  SentenceTransformerEmbeddingFunction unavailable — using ChromaDB default EF
```
ChromaDB falls back to its default embedding function (MiniLM, 384-dim). Production quality of semantic matching is therefore not BGE-M3; all "semantic" hits in the stack are actually MiniLM-space.

### Fix
- Change `_EMBEDDING_MODEL_VERSION` default from `"bge-m3-v1"` to `"BAAI/bge-m3"` in `semantic_cache_manager.py`
- Change `EMBEDDING_MODEL_ID` / `HIVE_MIND_EMBEDDING_MODEL_VERSION` in `.env` and `.env.example`
- Validate the SQLite `embedding_model_id` column can hold the longer id (already `TEXT`, OK)
- Clear `artifacts/gptcache/chroma/` once to force collection rebuild at new dim 1024
- Add startup check: if `embedding_model_id` in env != model that ChromaDB actually loaded, emit a CRITICAL log

### Success Criteria
- No `SentenceTransformerEmbeddingFunction unavailable` warning in test output
- `chroma.sqlite3` segments embed at 1024-dim (verify via `sqlite3 chroma.sqlite3 ".schema"` after first write)
- Existing 7/7 cache tests still green
- Add `test_chroma_loads_bge_m3_embedding_fn` that asserts the loaded EF's dimension == 1024

### Files In Scope
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py:_EMBEDDING_MODEL_VERSION`
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/cache/gptcache_client.py:85-106`
- `@c:/Git/Agentic-Workflow/.env:36-37`
- `@c:/Git/Agentic-Workflow/.env.example:36-38`

---

## Phase F4.3 — mypy + datetime hygiene

### Gap
- 15+ mypy errors on `semantic_cache_manager.py`: `"None" has no attribute "setex"` / `"get"` on `self.redis_client` — due to `redis_client: RedisClient | None` but unguarded access after `redis_enabled` check
- `l1_exact_cache.py:187`, `gptcache_client.py:653`, `gptcache_client.py:406`, `gptcache_client.py:328` use `datetime.utcnow()` → deprecated in Python 3.12

### Fix
- Add `assert self.redis_client is not None` after `if self.redis_enabled:` guards, OR narrow the type via a `@property` that raises
- Replace all `datetime.utcnow()` with `datetime.now(datetime.UTC)` → returns tz-aware UTC datetime
- One pre-commit that runs `mypy agentic_core/L4_state/utils/memory/` to ratchet forward

### Success Criteria
- `mypy agentic_core/L4_state/utils/memory/semantic_cache_manager.py` → 0 errors
- No `DeprecationWarning: datetime.datetime.utcnow() is deprecated` in test runs
- Cache tests stay 7/7

### Files In Scope
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py` (~10 None-narrow sites)
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/l1_exact_cache.py:187`
- `@c:/Git/Agentic-Workflow/agentic_core/L4_state/cache/gptcache_client.py:328, 406, 653`

---

## Gap Register

| # | Claim | Grade |
|---|-------|-------|
| 1 | F4.1 is a correctness upgrade, not a bug fix — current `_metadata` re-verification is correct but slower | DIRECTLY OBSERVED (code inspection, `semantic_cache_manager.py:688-710`) |
| 2 | F4.2 means production is using MiniLM, not BGE-M3 | DIRECTLY OBSERVED (SentenceTransformer warning on every test run) |
| 3 | F4.3 mypy errors are pre-existing, not introduced by R1A/R1B work | DIRECTLY OBSERVED (IDE lint feedback showed them before my edits) |
| 4 | Fan-in counts are estimates — ADG graph is stale for `semantic_cache_manager.py` | UNRESOLVED — `mcp1_adg_edge_fanin(tgt_id=765, imports)` returned 0 edges; graph needs regen |

---

## Dependencies

- F4.1, F4.2, F4.3 are **independent** (may be executed in parallel or any order)
- Prerequisite: ADG regen (`python tools/generate_full_adg.py`) to refresh fan-in before final wave plan

## Provenance

ADG Provenance: backend=sqlite, snapshot=adg_indexed_(latest).sqlite
Session trajectory: 2026-04-23 cache R1A/R1B activation wave (this chat)
