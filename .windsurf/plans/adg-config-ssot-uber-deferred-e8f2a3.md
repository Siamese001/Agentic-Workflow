# ADG Config SSOT — Uber-Deferred Implementation Backlog

**Slug:** `adg-config-ssot-uber-deferred-e8f2a3`
**Status:** Not Started
**Parent Plan:** `adg-config-ssot-deferred-d7e3a1` (COMPLETED 2026-05-06)
**Tier:** T3 (cross-layer, config-discipline)
**Created:** 2026-05-06

## Purpose

Consolidated implementation backlog for the 5 deferred items analyzed in parent plan `adg-config-ssot-deferred-d7e3a1`. **This plan is intentionally NOT implemented** — it serves as a triage-ready backlog for future activation when operational needs require.

## Deferred Items Backlog

### D-01 — Memory MCP knowledge_graph Schema SSOT

**Gap:** Schema hardcoded in `tools/memory/sqlite_memory_store.py` (inline `_SCHEMA` string); no `.windsurf/schemas/knowledge_graph.schema.sql` file.

**SSOT Violation:** Constitutional §31 (SSOT folder routing) — schemas should live in `.windsurf/schemas/`.

**Activation Trigger:**
- Memory MCP schema needs versioning for migration
- Multiple schema consumers need shared definition
- Schema corruption incident occurs

**Implementation Sketch:**
1. Extract `_SCHEMA` to `.windsurf/schemas/knowledge_graph.schema.sql`
2. Add schema version table with migration tracking
3. Update `sqlite_memory_store.py` to load schema from file
4. Add CI gate ensuring schema file matches Python constant

**Estimated Effort:** ~4k tokens
**Dependencies:** Memory MCP stability review

---

### D-02 — Redis Cluster Topology / Sentinel Migration

**Gap:** Production uses single-node Redis; Sentinel config exists only in `docker-compose.redis.yml` test profile.

**SSOT Violation:** `ADG_REDIS_URL` assumes single-node; no cluster-aware connection handling.

**Activation Trigger:**
- Production Redis failover required
- Cache availability becomes critical path
- Sentinel monitoring needed for HA

**Implementation Sketch:**
1. Add Sentinel connection fallback to `tools/adg/cache/redis_cache.py`
2. Support `REDIS_SENTINEL_HOSTS` env var (comma-separated)
3. Implement master discovery via Sentinel
4. Update `docker-compose.redis.yml` to production-grade topology
5. Add CI test for Sentinel failover scenario

**Estimated Effort:** ~6k tokens
**Dependencies:** Redis operational readiness, Docker Desktop cluster testing

---

### D-03 — ADG Generator Path Consolidation

**Gap:** ADG generator moved from `tools/adg/` to `tools/generate/`; documentation may reference old paths.

**SSOT Violation:** Path drift without migration guide or compatibility shim.

**Activation Trigger:**
- User confusion about correct ADG tool location
- Import errors from stale documentation
- CI scripts reference deprecated paths

**Implementation Sketch:**
1. Audit all docs for deprecated `tools/adg/generate_full_adg.py` references
2. Update references to `tools/generate/generate_full_adg.py`
3. Add compatibility shim at old path (redirect + deprecation warning)
4. Update `tools/adg/shared_modules/path_resolver.py` docstring

**Estimated Effort:** ~2k tokens
**Dependencies:** ADG schema graduation plan completion

---

### D-04 — Vector DB Cache Layout SSOT

**Gap:** `gptcache_client.py` implements dual backends (SQLite + Chroma) with no unified cache layout schema.

**SSOT Violation:** Cache paths scattered; no `VECTOR_CACHE_LAYOUT` constant.

**Activation Trigger:**
- Cache corruption or invalidation needs
- Cache directory structure confusion
- Multiple vector cache consumers need shared layout

**Implementation Sketch:**
1. Define `VECTOR_CACHE_LAYOUT` SSOT in `agentic_core/L4_state/contracts/` or `.windsurf/schemas/`
2. Unify SQLite + Chroma cache directory structure
3. Add cache layout validation to `NativePersistentCacheClient`
4. Document cache invalidation procedures

**Estimated Effort:** ~4k tokens
**Dependencies:** Vector DB config audit (separate from ADG)

---

### D-05 — OTel Runtime ADG Path Resolution Convergence

**Gap:** Runtime ADG uses custom binary serialization (RS/GS separators) in `system_learning/runtime_adg/store.py`; diverges from static ADG SQLite format.

**SSOT Violation:** Constitutional §23 acknowledges distinction, but no unified path resolution strategy.

**Activation Trigger:**
- Runtime ADG needs to query static ADG
- Unified observability dashboard required
- Storage format consolidation needed

**Implementation Sketch:**
1. Document runtime ADG path resolution strategy
2. Consider runtime ADG SQLite adapter (convergence with static)
3. Add cross-format query bridge if needed
4. Update OTel span ingestion to write to both formats

**Estimated Effort:** ~6k tokens
**Dependencies:** OTel runtime ADG review (may affect architecture)

## Activation Matrix

| Item | Blocker Risk | Effort | Dependencies | Recommended Activation Order |
|------|--------------|--------|--------------|------------------------------|
| D-01 | Low | 4k | None | 1 (isolated) |
| D-03 | Low | 2k | None | 2 (quick win) |
| D-04 | Medium | 4k | Vector audit | 3 |
| D-02 | High | 6k | Ops coordination | 4 (when HA needed) |
| D-05 | Medium | 6k | OTel review | 5 (architectural) |

## Success Criteria (When Activated)

- [ ] Selected D-item implemented per its sketch
- [ ] CI gates pass (including new gates if added)
- [ ] Parent plan Gap Register updated with "RESOLVED"
- [ ] Notion status updated (this plan → In Progress → Completed)
- [ ] Git commit with traceable message

## References

- Analysis Plan: `.windsurf/plans/adg-config-ssot-deferred-d7e3a1.md`
- Grandparent Plan: `.windsurf/plans/adg-config-ssot-audit-c7e4a2.md`
- Constitutional: §22 (graph-layer), §31 (SSOT folder routing), §23 (static vs runtime ADG)
