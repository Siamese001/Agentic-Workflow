# ADR-035: Layered Adapter Composition Is Not Duplication (Reject E.1)

**Status**: ACCEPTED
**Date**: 2026-04-23
**Phase**: Wave E.1 — `adg-dead-code-waves-efg-b2e4f7`
**Deciders**: SVP Engineering (Cascade) + user Author-Gate approval
**ADG Snapshot**: `artifacts/adg/adg_indexed_04232026_1442.sqlite`

---

## Context

The ADG materialized view `v_p2_duplicated_adapters` flagged three clusters as
"P2: duplicated infra adapters":

| Cluster | Count | Files |
|---|---:|---|
| `ADG::Symbol::chromadb` | 2 | `agentic_core/L4_state/cache/gptcache_client.py`, `agentic_core/L4_state/utils/client/chroma_client.py` |
| `ADG::Symbol::redis` | 3 | `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py`, `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`, `agentic_core/cache/redis_cache_client.py` |
| `ADG::Symbol::sqlite3` | 3 | `agentic_core/L4_state/cache/gptcache_client.py`, `apps_shared/data_adapters/repo_signal_adapter.py`, `tools/memory/sqlite_memory_store.py` |

The plan (`.windsurf/plans/adg-dead-code-waves-efg-b2e4f7.md`) originally framed
Wave E as "duplicate adapter consolidation" and anticipated in its Gap Register
(§G1) that the premise might be refuted by composition-layer inspection.

Source inspection confirms the §G1 anticipation. The view's heuristic (N distinct
files importing the same vendor symbol) conflates **vendor-import count** with
**duplicate adapter instances** — those are different concepts. A single adapter
never imports a vendor symbol more than once per file; the count is therefore
an approximation of "how many architectural layers touch this vendor," which is
a legitimate and expected number >1 for any vendor used in layered composition.

---

## Decision

**Reject E.1.** No consolidation is performed. Each flagged file owns a distinct
responsibility in the layered composition and deleting or merging any of them
would collapse real architectural seams.

Per-cluster responsibility map:

### Cluster 1 — chromadb (2 files, both legitimate)

| File | Role |
|---|---|
| `agentic_core/L4_state/utils/client/chroma_client.py` | **Raw client adapter.** `SovereignChromaClient` — direct vendor wrapper exposing persistent-collection CRUD; the seam where `import chromadb` is contained. |
| `agentic_core/L4_state/cache/gptcache_client.py` | **L2 semantic cache wrapper.** `NativePersistentCacheClient` — composes ChromaDB (vectors) + SQLite (scalars) + BGE-M3 embeddings into a spec-compliant semantic cache. Uses `chromadb` directly because it is the cache implementation, not a cache consumer. |

These are composition, not duplication: one is the vendor adapter, the other is
a different product (a semantic cache) that happens to use the same vendor.

### Cluster 2 — redis (3 files, 3 distinct layers)

| File | Role |
|---|---|
| `agentic_core/cache/redis_cache_client.py` | **Raw client adapter.** `DeterministicRedisCache` — hash-keyed, DB-isolated, TTL-managed core client. The seam where `import redis` is contained. |
| `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | **Semantic cache manager (L4).** Canonical `SemanticCacheManager` — Hive Mind O(1) exact recall layer; composes Redis + InMemoryVectorStore for persistence of agentic memory. |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py` | **L3 orchestration engine.** Orchestrator that dispatches redis-backed operations across agents via `SovereignBaseAgent` — not a redis adapter, an orchestrator that happens to coordinate redis-touching work. |

Each one runs at a distinct architectural layer (L4 raw, L4 cache mgr, L3
orchestrator) with a distinct responsibility. Collapsing them would require the
survivor to absorb all three roles, which would be a layering regression.

### Cluster 3 — sqlite3 (3 files, 3 distinct use-cases)

| File | Role |
|---|---|
| `agentic_core/L4_state/cache/gptcache_client.py` | **Scalar half of the L2 semantic cache.** Uses sqlite3 for query/response/metadata storage alongside ChromaDB vectors. |
| `apps_shared/data_adapters/repo_signal_adapter.py` | **App-layer signal aggregator.** `RepoSignalSnapshot` — reads ADG/tests/CI signals from on-disk sqlite artifacts for `apps_*` workflows; not a cache, not a general-purpose store. |
| `tools/memory/sqlite_memory_store.py` | **Knowledge-graph memory store.** Shared store for `knowledge_graph.sqlite` used by the Memory MCP server and `graph_memory_bridge.py` CLI. API mirrors `@modelcontextprotocol/server-memory` tool signatures. |

Three sqlite3 consumers, three distinct storage domains (L2 cache, app signals,
knowledge graph). Consolidating them would violate bounded-context discipline.

---

## Why The View Misfires

`v_p2_duplicated_adapters` counts distinct files with `import <vendor>`. The
rule is a useful first-pass heuristic for actual duplication (e.g., two files
both implementing `RedisCacheAdapter` with copy-pasted methods). It is not a
semantic classifier. When the architecture intentionally layers a vendor
(raw-client → feature-manager → orchestrator), the count exceeds 1 by design.

The view's signal is not wrong — **these files do all import the same vendor**
— but the P2 framing ("duplicated") is an inference beyond the data the view
owns. A more faithful name would be `v_vendor_import_fanout` with any P-band
assignment deferred to a second pass that inspects whether the adapters
overlap in API surface.

---

## Consequences

### Accepted

- `v_p2_duplicated_adapters` will continue to show 3 rows (chromadb, redis,
  sqlite3) until the view is renamed or narrowed. This is accepted drift
  — the view is a diagnostic, not a gate.
- No consolidation work is scheduled. Wave E.1 is closed.
- The plan `.windsurf/plans/adg-dead-code-waves-efg-b2e4f7.md` §G1 is
  marked resolved by this ADR.
- The Notion P1 E.1 row in Wave/Phase Convergence will be closed with
  Status=Done and this ADR linked in Blocking Items.

### Rejected

- Consolidating to one "canonical" adapter per cluster would require the
  survivor to absorb 2-3 distinct responsibilities, re-introducing layer
  violations the current structure prevents.

### Future work (optional, not blocking)

- Rename the view to `v_vendor_import_fanout` and drop the P-band prefix.
- Add a second-pass view that classifies genuine duplication by comparing
  adapter public API surfaces (class names, method signatures) rather
  than just vendor-import count.

Neither of those is committed in this ADR; both are backlog candidates.

---

## References

- Plan: `.windsurf/plans/adg-dead-code-waves-efg-b2e4f7.md` (Wave E, Gap G1)
- View: `v_p2_duplicated_adapters` in `artifacts/adg/adg_indexed_*.sqlite`
- Prior related ADR: `ADR-019-adg-materialized-views.md`
- Author-Gate decision: captured via harness author-gate 2026-04-23
