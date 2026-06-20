# Wave 2 — Native L2 Persistence (SQLite + ChromaDB, No GPTCache)

Replace the broken `GPTCacheClient` with a native persistent L2 cache backed directly by SQLite (scalar) and ChromaDB `PersistentClient` (vector), then validate snapshot restore across a simulated process restart.

---

## Context

| Item | Finding |
|------|---------|
| gptcache v0.1.1 installed | API is `Cache.init(data_manager, ...)` — completely different from v0.1.44 `init_similar_cache` the client was written against |
| gptcache v0.1.44 | `gptcache.Cache` doesn't exist as importable; `NoneType not callable` at init |
| ChromaDB | `PersistentClient(path=...)` works ✅ — verified upsert + count round-trip |
| Decision | **Option C**: drop gptcache library entirely, implement persistence natively |

---

## Wave Structure

| Phase | File(s) | Action | Risk |
|-------|---------|--------|------|
| **P1** | `gptcache_client.py` | Rewrite to `NativePersistentCacheClient` using SQLite + ChromaDB `PersistentClient`. Keep same public API (`get`, `set`, `search_similar`, `get_stats`, `clear`). | Low |
| **P2** | `semantic_cache_manager.py` | Rename import `GPTCacheClient` → `NativePersistentCacheClient`. Update `_init_gptcache` → `_init_l2_cache`. Update mock-mode check. | Low |
| **P3** | `_test_wave2_snapshot_restore.py` (temp) | Run Phase 1 (write entry), kill process, run Phase 2 (verify restore). Delete after pass. | — |
| **P4** | `tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py` | Update mock patch targets to new class name; add a real persistence round-trip test using `tmp_path`. | Low |
| **P5** | `pyproject.toml` | Remove gptcache from deps if present; add `chromadb` pin. | Low |

---

## P1 — NativePersistentCacheClient design

**SQLite schema** (scalar store, same as gptcache 0.1.1 internal schema):
```sql
CREATE TABLE IF NOT EXISTS l2_cache (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    embedding BLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_access_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**ChromaDB**: `PersistentClient(path=cache_dir/chroma)` — collection `l2_semantic_cache`.

**Embedding**: same `bmg_embed_text` via `BGEEmbedding` (already works).

**`get(query)`**: embed query → ChromaDB `.query()` → if top-1 distance ≤ threshold, fetch response from SQLite by id → return.

**`set(query, response)`**: embed query → upsert into ChromaDB (id=sha256 of query) → insert into SQLite.

**`search_similar(query_text, threshold)`**: same as `get` but return list of `{score, metadata}`.

**`_cache` sentinel**: set to `"real"` on success, `"mock"` on failure — preserves existing mock-mode check in `SemanticCacheManager`.

---

## P2 — SemanticCacheManager changes

- Import rename: `GPTCacheClient` → `NativePersistentCacheClient`
- Method rename: `_init_gptcache` → `_init_l2_cache` (or keep name to avoid blast radius)
- Log strings: `"GPTCache"` → `"L2Cache"`
- `gptcache_enabled` attribute name stays (avoids cascading stat key renames)

---

## P3 — Snapshot restore validation

Two-phase subprocess test:
1. `python script.py --phase 1` → `set("test query", "test response")` → verify `chroma/` dir created and SQLite row inserted
2. `python script.py --phase 2` (fresh singleton) → `get("test query")` → assert non-None

---

## Success Criteria

- [ ] `artifacts/gptcache/chroma/` persists across singleton reset
- [ ] `artifacts/gptcache/l2_cache.db` contains inserted rows
- [ ] Phase 2 recall returns the Phase 1 entry
- [ ] `gptcache_enabled = True` in live process (not mock mode)
- [ ] All existing Wave 4 unit tests pass with patched class name
- [ ] `gptcache` package no longer imported anywhere in production code

---

## Rollback

All changes are confined to 2 files (`gptcache_client.py`, `semantic_cache_manager.py`). Revert both to restore mock-mode behaviour. No schema migrations required (fresh `artifacts/gptcache/` dir).
