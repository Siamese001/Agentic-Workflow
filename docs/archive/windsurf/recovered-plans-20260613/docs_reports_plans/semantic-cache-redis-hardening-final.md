# Semantic Cache / Redis Hardening — Final Accurate Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Status: COMPLETE (all gaps resolved, regressions fixed)

---

## Background

The previous session's sprint plan introduced several regressions due to incorrect
assumptions about module structure. This document is the authoritative record of
every gap found by AST analysis and every fix applied, including regression fixes.

---

## File Inventory (Changed)

| File | Role |
|------|------|
| `agentic_core/L4_state/memory/semantic_cache_manager.py` | Core Hive Mind — primary target |
| `agentic_core/L4_state/memory/in_memory_vector_store.py` | FAISS adapter — broken ghost imports fixed |
| `agentic_core/L4_state/types/vector_store_types.py` | BaseVectorStore ABC — broken ghost imports fixed |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py` | L4 hybrid cache — async/sync + dict store + docstring |
| `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | Redis agent — broken `__new__` singleton |
| `agentic_core/config/core/constants_config.py` | Feature flags — `USE_REDIS_CACHE` default |
| `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py` | Orchestrator factory — invalid `super()` call |
| `agentic_core/mixins/redis_cache_mixin.py` | Cache mixin — routing through broken agent |
| `agentic_core/L4_state/workflow_engines/redis_cache_client.py` | Duplicate — tombstoned |
| `tests/unit/test_semantic_cache_redis_hardening.py` | Invariant test suite — new file |

---

## Ghost Import Root Cause (Discovered This Session)

`agentic_core.semantic_memory` **does not exist** anywhere in the repository.

Both `in_memory_vector_store.py` and `vector_store_types.py` imported from it:
```python
# BROKEN (module doesn't exist)
from agentic_core.semantic_memory.interfaces import BaseVectorStore
from agentic_core.semantic_memory.models import MemoryItem, MemoryQuery
```

Correct paths:
```python
# FIXED
from agentic_core.L4_state.types.vector_store_types import BaseVectorStore
from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery
```

Actual `MemoryItem` schema (`agentic_core/L4_state/types/memory_item_types.py`):
```python
class MemoryItem(BaseEntity):
    content: str          # text content
    embedding: list[float]
    metadata: dict[str, Any]
    score: float | None   # only populated on retrieval
```

Actual `MemoryQuery` schema:
```python
class MemoryQuery(BaseModel):
    vector: list[float]              # query embedding — NOT 'text'
    top_k: int = 5
    filter_metadata: dict | None = None
```

**No `id`, `text`, `payload`, `namespace` fields exist on either model.**

---

## All Gaps Fixed

### Sprint 1 — Runtime Crashes (C1–C5)

| ID | File | Bug | Fix |
|----|------|-----|-----|
| C1 | `semantic_cache_manager.py` | `await` on sync `redis_client.setex()` in `learn_async()` | Removed `await` |
| C2 | `RedisSovereignAgent.py` | `__new__` calls undefined `get_redis_sovereign()` | Replaced `__new__` with `_init()` method |
| C3 | `sovereign_semantic_cache.py` | `async def cache_file/invalidate` awaiting sync client | Converted to sync methods |
| C4 | `constants_config.py` | `USE_REDIS_CACHE = "false"` by default | Changed to `"true"` |
| C5 | `sovereign_redis_orchestrator.py` | Free factory function calls `super().heal_repository()` | Removed invalid `super()` call |

### Sprint 2 — Degraded Behaviour (H1–H4)

| ID | File | Bug | Fix |
|----|------|-----|-----|
| H1 | `semantic_cache_manager.py` | Layer 2 was O(N) numpy dict scan | Replaced with `InMemoryVectorStore` (FAISS-backed) |
| H2 | `semantic_cache_manager.py` | `promote_to_long_term()` had `except Exception: pass` on Redis TTL extension | Replaced with `Logger.warning(...)` |
| H3 | `sovereign_semantic_cache.py` | Wrong Redis API: `ttl=` kwarg, no bytes encoding | Fixed to `ttl_seconds=`, value encoded as `bytes` |
| H4 | `redis_cache_mixin.py` | Routed through broken `RedisSovereignAgent` | Replaced with `get_hot_cache()` |

### Sprint 3 — Structural Cleanup (M1–M4)

| ID | File | Bug | Fix |
|----|------|-----|-----|
| M1 | `semantic_cache_manager.py` + `sovereign_semantic_cache.py` | Stale "Pinecone" references in docstrings/class body | Updated to InMemoryVectorStore |
| M2 | `semantic_cache_manager.py` | `_should_sample_trace()` used `random.random()` — non-deterministic | Hash-based deterministic sampling from `trace_id` |
| M3 | `L4_state/workflow_engines/redis_cache_client.py` | Duplicate full Redis client implementation | Tombstoned with redirect comment |
| M4 | `tests/unit/test_semantic_cache_redis_hardening.py` | No invariant test coverage | Created comprehensive test suite |

### Session 2 Regressions Fixed

| ID | File | Regression | Fix |
|----|------|------------|-----|
| R1 | `semantic_cache_manager.py` | `_init_vector_store()` reset `_vector_store` back to `{}` after `InMemoryVectorStore` was assigned | Removed the reassignment — `_init_vector_store()` now only sets `vector_store_enabled = True` |
| R2 | `semantic_cache_manager.py` | `recall()` (sync method) contained `await self._vector_store.query()` | Replaced with sync `loop.run_until_complete()` pattern using real `MemoryQuery(vector=...)` |
| R3 | `semantic_cache_manager.py` | `update_feedback_score()` called `async promote_to_long_term()` with `return self.promote_to_long_term(...)` (no await, no loop) | Wrapped in `asyncio.ensure_future` / `loop.run_until_complete` |
| R4 | `semantic_cache_manager.py` | `learn()` and `learn_async()` called `self.sanitizer.sanitize(context)` twice | Collapsed to single sanitization before hash computation |
| R5 | `semantic_cache_manager.py` + `in_memory_vector_store.py` | Promoted `MemoryItem` with wrong fields (`id`, `text`, `payload`, `namespace`) | Fixed to use actual schema: `content`, `embedding`, `metadata` (payload stored in `metadata["payload"]`) |
| R6 | `semantic_cache_manager.py` | Imported from `agentic_core.semantic_memory.models` (non-existent) | Fixed to `agentic_core.L4_state.types.memory_item_types` |
| R7 | `in_memory_vector_store.py` | Ghost import of `agentic_core.semantic_memory.interfaces` and `.models` | Fixed to real module paths |
| R8 | `vector_store_types.py` | Same ghost import | Fixed to real module path |
| R9 | `sovereign_semantic_cache.py` | `_vector_store` still a plain `dict[str, dict]` | Replaced with `InMemoryVectorStore()` |
| R10 | Tests | `MemoryItem`/`MemoryQuery` used with wrong fields | Rewritten to use real schema |

---

## Canonical Architecture (Post-Fix)

```
SemanticCacheManager (singleton, thread-safe)
├── Layer 1: Redis (Working Memory, 24h TTL)
│   └── DeterministicRedisCache via redis.from_url()
│       ├── TCP pre-check before connect
│       └── Bounded LRU fallback if unavailable
└── Layer 2: InMemoryVectorStore (Long-Term DNA, promotion-gated)
    ├── FAISS IndexFlatIP primary path (if faiss installed)
    └── Pure-Python cosine fallback
    └── MemoryItem schema: {content, embedding, metadata{namespace, payload, ...}}
    └── Query via: MemoryQuery(vector=..., filter_metadata={"namespace": ns})
```

```
SovereignSemanticCache
├── Redis: get_hot_cache() -> DeterministicRedisCache (sync API, ttl_seconds=, bytes value)
└── InMemoryVectorStore (replaces legacy plain-dict _vector_store)
```

```
RedisCacheMixin
└── get_hot_cache() [canonical singleton, not RedisSovereignAgent]
```

---

## Key Invariants

1. **Single Redis client**: Only `DeterministicRedisCache` via `get_hot_cache()` / `get_coordination_cache()`
2. **Sync/async boundary**: `recall()`, `learn()`, `learn_async()` are sync (no `await`). `promote_to_long_term()` and `upsert()` are async. Sync callers use `loop.run_until_complete()`.
3. **MemoryItem schema**: `content` (str), `embedding` (list[float]), `metadata` (dict), `score` (float|None). No `id`, `text`, `payload`, `namespace` top-level fields.
4. **MemoryQuery schema**: `vector` (list[float]), `top_k` (int), `filter_metadata` (dict|None). No `text`, `namespace`, `threshold` fields.
5. **No ghost imports**: `agentic_core.semantic_memory.*` does not exist. All imports from `agentic_core.L4_state.types.*`.
6. **Deterministic sampling**: `_should_sample_trace(trace_id)` uses SHA-256 hash, not `random.random()`.
7. **Redis enabled by default**: `USE_REDIS_CACHE = "true"` in constants.

---

## Test Coverage

`tests/unit/test_semantic_cache_redis_hardening.py` covers:

- C1: No `await` on sync Redis client in `learn_async()`
- C2: `RedisSovereignAgent` instantiation without `NameError`
- C3: `SovereignSemanticCache` sync method signatures
- C4: `USE_REDIS_CACHE` defaults to `True`
- C5: `get_sovereign_redis_orchestrator()` factory doesn't call `super()`
- H1: `_vector_store` is `InMemoryVectorStore` with `_faiss_index` + `_storage`
- H2: Redis TTL extension failure is logged (not swallowed)
- H3: `SovereignSemanticCache.cache_file()` uses `ttl_seconds=` + bytes
- H4: `RedisCacheMixin` source has no `RedisSovereignAgent` import (AST-verified)
- M1: `SemanticCacheManager` source has no "Pinecone" string
- M2: `_should_sample_trace(trace_id)` is deterministic for same input
- M3: `L4_state/workflow_engines/redis_cache_client.py` is tombstoned
- M4: Full recall/learn/promote cycle + `get_stats()` alias

---

## Run Tests

```
python -m pytest tests/unit/test_semantic_cache_redis_hardening.py -v
```

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

