---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\semantic-cache-reconciliation-0a0f93.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\semantic-cache-reconciliation-0a0f93.md'
source_sha256: 38f2d23287b2e867e0a6c74acd18fa6d657d3ee66a23e844a0a27fbaf7310b3e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Semantic Cache Reconciliation + Dead-Code ADG Gate

Wire `GPTCacheClient` as the persistent Layer 2 backend of `SemanticCacheManager`, and add an ADG generation blocker that fails if any production module has zero non-test/non-ops fan-in edges.

---

## Wave Structure

| Wave | Scope | Checkpoint | Tokens |
|------|-------|------------|--------|
| Wave 1 — Wire GPTCache as L2 | `SemanticCacheManager._init_vector_store` replaced with GPTCacheClient backend | A — tests pass | ~4K 🟢 |
| Wave 2 — Snapshot restore path | `SemanticCacheManager._initialize` loads existing `artifacts/gptcache/gptcache.db` on startup | B — cold start + warm start both verified | ~3K 🟢 |
| Wave 3 — ADG dead-import gate | New `ops_scripts/ci/dead_production_import_gate.py` + wired into `tools/generate/generate_full_adg.py` preflight | C — gate blocks on known disconnected module | ~3K 🟢 |
| Wave 4 — Tests + cleanup | Unit tests for wired path; retire `gptcache_client` singleton duplication; update `prove_layer2_semantic_cache.py` | D — full test suite green | ~3K 🟢 |

---

## Gap Register

**GAP-1: SemanticCacheManager Layer 2 is ephemeral**
- `InMemoryVectorStore._storage{}` is a plain Python dict, allocated fresh every process start
- Promoted "DNA" memories are lost on restart — the `promote_to_long_term` pathway is a no-op across sessions
- Fix: replace `InMemoryVectorStore` as L2 with `GPTCacheClient` which already uses `SQLite + ChromaDB` on disk at `artifacts/gptcache/gptcache.db`

**GAP-2: GPTCacheClient is dead production code**
- `gptcache_client.py` exists at `agentic_core/L4_state/cache/gptcache_client.py` with full persistence implementation
- Zero production fan-in (ADG SQL confirms): only `ops_scripts/ci/` scripts reference it
- Fix: wire it in via Wave 1; Gate: block ADG generation if this situation recurs

**GAP-3: No ADG generation gate for disconnected production modules**
- Sign-off on GPTCache passed because the proof script (`prove_layer2_semantic_cache.py`) ran successfully — but the ADG graph shows it was never imported by production code
- Fix: `dead_production_import_gate.py` queries the freshly-built SQLite before `adg_redis_ingest` runs

---

## Execution Plan

### Phase 1 — Wire GPTCacheClient into SemanticCacheManager (Wave 1)

**Scope**: Replace `_init_vector_store` + `_vector_store` usage in `SemanticCacheManager` with a dual-path backend:
- Layer 1: Redis exact-hash (unchanged)
- Layer 2: `GPTCacheClient` (persistent SQLite+ChromaDB) replacing `InMemoryVectorStore`

**Files touched**:
- `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`
- `agentic_core/L4_state/cache/gptcache_client.py` (expose `search_similar(query, threshold)` method)

**Key changes**:
```python
# In SemanticCacheManager._initialize():
# BEFORE:
self._vector_store = InMemoryVectorStore()
# AFTER:
from agentic_core.L4_state.cache.gptcache_client import GPTCacheClient
self._gptcache = GPTCacheClient(cache_dir="artifacts/gptcache", similarity_threshold=self.similarity_threshold)
```

**Acceptance**: `SemanticCacheManager.get_instance()` constructs without error; `gptcache.db` file created at `artifacts/gptcache/gptcache.db`.

---

### Phase 2 — Snapshot restore on startup (Wave 2)

**Scope**: Verify that `GPTCacheClient` at `artifacts/gptcache/gptcache.db` survives restart and returns hits for previously stored queries. No new code needed if GPTCache's `init_similar_cache` auto-reconnects to existing SQLite — validate this.

**Files touched**:
- `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` (add `_log_snapshot_status` on init)
- `agentic_core/L4_state/cache/gptcache_client.py` (confirm `_init_cache` opens existing DB, not truncate)

**Acceptance**: Store a query in Session A → restart process → recall returns the stored result in Session B (via `gptcache.db`).

---

### Phase 3 — Dead-import ADG generation gate (Wave 3)

**Scope**: New gate script `ops_scripts/ci/dead_production_import_gate.py` that:
1. Opens the freshly-built `adg_indexed_<ts>.sqlite`
2. Queries for all `module` nodes in `agentic_core/` or `apps_*/` layers
3. For each, counts fan-in edges where the source is also a production module (not `L_TEST`, not `L_OPS`)
4. Fails with a list of zero-fan-in modules if any exist

Wire into `tools/generate/generate_full_adg.py` after SQLite is written, before `adg_redis_ingest`:
```python
# After DB finalized:
from ops_scripts.ci.dead_production_import_gate import run_gate
run_gate(sqlite_path)  # raises SystemExit(1) if violations
```

**SQL core**:
```sql
SELECT n.resolved_path, COUNT(e.id) AS fan_in
FROM nodes n
LEFT JOIN edges e ON e.dst_id = n.id
  AND e.relation_type = 'imports'
  AND e.src_id IN (
    SELECT id FROM nodes WHERE layer NOT IN ('L_TEST','L_OPS','L_TOOLS')
  )
WHERE n.entity_type = 'module'
  AND n.layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
GROUP BY n.id
HAVING fan_in = 0
ORDER BY n.resolved_path;
```

**Acceptance**: Running the gate against current SQLite reports `gptcache_client.py` as a violation (confirms it fires correctly). After Wave 1 wires it in, gate passes.

---

### Phase 4 — Tests + cleanup (Wave 4)

**Scope**:
- Add unit test: `tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py` — verifies `SemanticCacheManager.get_instance()` uses `GPTCacheClient`, not `InMemoryVectorStore`, as L2
- Add unit test: `tests/unit/ops_scripts/ci/test_dead_production_import_gate.py` — verifies gate detects zero-fan-in modules
- Update `ops_scripts/ci/prove_layer2_semantic_cache.py` to use the wired path (import from `SemanticCacheManager`, not standalone `GPTCacheClient`)
- Remove the now-dead standalone `_global_gptcache` singleton from `gptcache_client.py` (consolidate into `SemanticCacheManager`)

**Acceptance**: `pytest tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py tests/unit/ops_scripts/ci/test_dead_production_import_gate.py` — all green.

---

## Rules

- `InMemoryVectorStore` stays in place — it is used by `SovereignSemanticCache` (different system); do not remove it
- `GPTCacheClient` must degrade gracefully if `gptcache` package is not installed (already has `_cache = "mock"` fallback — preserve this)
- Gate is fail-closed: SQLite query errors = gate fails (not silently passes)
- No changes to Redis Layer 1 (24h TTL `setex` path) — it is working correctly as a short-term hot cache

---

## Success Criteria

- [ ] `gptcache_client.py` has at least one production fan-in edge in ADG (import from `semantic_cache_manager.py`)
- [ ] `artifacts/gptcache/gptcache.db` persists across `SemanticCacheManager` restarts and returns cache hits
- [ ] `dead_production_import_gate.py` blocks `generate_full_adg.py` if zero-fan-in production modules exist
- [ ] Gate itself is validated by re-running against current SQLite (must report `gptcache_client` before fix)
- [ ] All existing `semantic_cache_manager` tests remain green
- [ ] `InMemoryVectorStore` tests unaffected (it's not removed)

---

## Rollback Strategy

1. `SemanticCacheManager._initialize` change is isolated to `_init_vector_store` — revert one method to restore `InMemoryVectorStore`
2. Gate is additive — removing the `run_gate()` call from `generate_full_adg.py` restores prior behavior
3. `artifacts/gptcache/` directory is gitignored (runtime artifact) — no repo state to undo
