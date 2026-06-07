# ADG Config SSOT Remediation — Deferred Scope (COMPLETED ANALYSIS)

**Slug:** `adg-config-ssot-deferred-d7e3a1`
**Status:** Completed
**Parent Plan:** `adg-config-ssot-audit-c7e4a2` (COMPLETED 2026-05-06)
**Tier:** T3 (cross-layer, config-discipline)
**Completed:** 2026-05-06

## Wave Execution Summary

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | P1 | Memory MCP knowledge_graph schema analysis | ✅ DONE |
| W2 | P2 | Redis cluster topology / Sentinel assessment | ✅ DONE |
| W3 | P3 | ADG schema graduation review | ✅ DONE |
| W4 | P4 | chromadb / vector_db cache layout audit | ✅ DONE |
| W5 | P5 | OTel runtime ADG path resolution analysis | ✅ DONE |
| W6 | P6 | Uber-deferred plan creation | ✅ DONE |

## Gap Register (Completed Analysis)

| Gap ID | Description | P-Band | Finding | Linked to Uber-Deferred Plan |
|--------|-------------|--------|---------|------------------------------|
| G-01 | Memory MCP schema hardcoded in Python | P2 | `_SCHEMA` string in `sqlite_memory_store.py`; no `.cursor/schemas/memory*.sql` | D-01 |
| G-02 | Redis Sentinel only in test compose | P3 | Production uses single-node; Sentinel config exists but profile-gated | D-02 |
| G-03 | ADG generator relocated to `tools/generate/` | P3 | Path changed from `tools/adg/`; some docs may reference old path | D-03 |
| G-04 | Vector cache uses dual SQLite+Chroma | P3 | `gptcache_client.py` has both; no unified cache layout SSOT | D-04 |
| G-05 | Runtime ADG uses different serialization | P3 | `store.py` uses RS/GS separators; diverges from static ADG SQLite | D-05 |

## W1 — Memory MCP knowledge_graph Schema Analysis ✅

**Finding:** Schema is defined inline as `_SCHEMA` string in `tools/memory/sqlite_memory_store.py` (lines 82-108). Migration system exists but uses additive column approach without version tracking.

**SSOT Issue:** No separate `.cursor/schemas/knowledge_graph.schema.sql` file violates SSOT folder routing (§31).

**Recommendation:** Extract schema to canonical location; add version table for migration tracking.

## W2 — Redis Sentinel Topology Assessment ✅

**Finding:** `docker-compose.redis.yml` has Sentinel + replica profile (`--profile sentinel`), but production uses single-node Docker container on port 6379.

**SSOT Issue:** `ADG_REDIS_URL` assumes single-node; no cluster-aware connection handling in `redis_cache.py`.

**Recommendation:** Add Sentinel connection fallback to `RedisCache` class; test with compose profile.

## W3 — ADG Schema Graduation Review ✅

**Finding:** ADG generator moved to `tools/generate/generate_full_adg.py` (from `tools/adg/`). Path resolver at `tools/adg/shared_modules/path_resolver.py` is canonical SSOT.

**SSOT Issue:** Some documentation may reference deprecated paths; no automated redirect.

**Recommendation:** Audit docs for old paths; add compatibility shim if needed.

## W4 — chromadb / vector_db Cache Layout Audit ✅

**Finding:** `gptcache_client.py` implements `NativePersistentCacheClient` with dual backends (SQLite + Chroma). Cache layout varies by backend.

**SSOT Issue:** No unified cache layout schema; chromadb cache path not centralized.

**Recommendation:** Add `VECTOR_CACHE_LAYOUT` SSOT constant; unify cache directory structure.

## W5 — OTel Runtime ADG Path Resolution ✅

**Finding:** Runtime ADG uses custom binary serialization (RS `` / GS `` separators) in `system_learning/runtime_adg/store.py`. Static ADG uses SQLite.

**SSOT Issue:** Constitutional §23 distinction observed (static ≠ runtime), but no unified path resolution.

**Recommendation:** Document runtime ADG path strategy; consider convergence with static ADG SQLite format.

## W6 — Uber-Deferred Plan Created ✅

**Deliverable:** `.cursor/plans/adg-config-ssot-uber-deferred-e8f2a3.md` — see separate plan for implementation backlog.

## Success Criteria (All Met)

- [x] All 5 deferred items (D-01 through D-05) analyzed
- [x] Gap findings documented in Gap Register
- [x] Uber-deferred plan created in Notion
- [x] Current plan marked Completed in Notion
- [x] All changes committed to GitHub

## References

- Parent Plan: `.cursor/plans/adg-config-ssot-audit-c7e4a2.md`
- Uber-Deferred Plan: `.cursor/plans/adg-config-ssot-uber-deferred-e8f2a3.md`
- Constitutional: §22 (graph-layer), §31 (SSOT folder routing), §23 (static vs runtime)
