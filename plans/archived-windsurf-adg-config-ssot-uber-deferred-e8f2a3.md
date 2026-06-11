---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-config-ssot-uber-deferred-e8f2a3.md'
original_relative_path: 'adg-config-ssot-uber-deferred-e8f2a3.md'
source_sha256: de5f48c8e07c7c26142e81fa0831c1362480f18997e85a8355a0a5f8fefa1aad
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Config SSOT — Uber-Deferred Implementation Backlog

**Slug:** `adg-config-ssot-uber-deferred-e8f2a3`
**Status:** Completed
**Parent Plan:** `adg-config-ssot-deferred-d7e3a1` (COMPLETED 2026-05-06)
**Tier:** T3 (cross-layer, config-discipline)
**Created:** 2026-05-06
**Started:** 2026-05-06
**Completed:** 2026-05-06

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1 | D-01: Memory MCP schema SSOT | ~4k | ✅ DONE | Schema extracted, version table added, CI gate passing |
| W2 | P2 | D-03: ADG generator path consolidation | ~2k | ✅ DONE | Docs updated, shim created, no broken refs |
| W3 | P3 | D-04: Vector DB cache layout SSOT | ~4k | ✅ DONE | VECTOR_CACHE_LAYOUT constant, unified structure |
| W4 | P4 | D-02: Redis Sentinel migration | ~6k | ⏸️ DEFERRED | Will activate when HA needed |
| W5 | P5 | D-05: OTel runtime ADG convergence | ~6k | ⏸️ DEFERRED | Will activate when format convergence needed |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Memory MCP schema extraction | tools/memory/, .windsurf/schemas/ | Inline schema, no versioning | ~4k | ✅ DONE |
| P2 | ADG generator path consolidation | docs/, tools/adg/, tools/generate/ | Path drift, stale docs | ~2k | ✅ DONE |
| P3 | Vector DB cache layout | agentic_core/L4_state/cache/ | Dual backends, no SSOT | ~4k | ✅ DONE |
| P4 | Redis Sentinel migration | tools/adg/cache/, docker-compose.redis.yml | Single-node prod, test-only Sentinel | ~6k | ⏸️ DEFERRED |
| P5 | OTel runtime ADG convergence | system_learning/runtime_adg/ | Format divergence | ~6k | ⏸️ DEFERRED |

## Completed Waves

### W1 — D-01: Memory MCP knowledge_graph Schema SSOT ✅

**Commit:** `e3c453f168`

**Deliverables:**
- `.windsurf/schemas/knowledge_graph.schema.sql` - Canonical schema
- `.windsurf/schemas/knowledge_graph_migrations.sql` - Migrations
- `tools/memory/sqlite_memory_store.py` - Updated to load from file
- `ops_scripts/ci/check_memory_schema_sync.py` - CI gate
- `tests/unit/tools/memory/test_schema_versioning.py` - 9 tests

**Gap G-01:** ✅ RESOLVED

### W2 — D-03: ADG Generator Path Consolidation ✅

**Commit:** `4bd811b6ac`

**Deliverables:**
- Updated docs with correct paths
- `tools/adg/generate_full_adg.py` compatibility shim
- Updated `tools/adg/shared_modules/path_resolver.py` docstring

**Gap G-03:** ✅ RESOLVED

### W3 — D-04: Vector DB Cache Layout SSOT ✅

**Commit:** `f196e5cf2f`

**Deliverables:**
- `agentic_core/L4_state/contracts/vector_cache_layout.py`
- `agentic_core/L4_state/cache/gptcache_client.py` updated
- `tests/unit/L4_state/cache/test_vector_cache_layout.py` - 14 tests

**Gap G-04:** ✅ RESOLVED

## Deferred to Future Activation

### W4 — D-02: Redis Sentinel Migration ⏸️

**Activation Trigger:** Production Redis failover required

**Remaining Work:**
- Add Sentinel connection to `tools/adg/cache/redis_cache.py`
- Support `REDIS_SENTINEL_HOSTS` env var
- Update `docker-compose.redis.yml` for production

**Gap G-02:** ⏸️ DEFERRED

### W5 — D-05: OTel Runtime ADG Convergence ⏸️

**Activation Trigger:** Runtime ADG needs to query static ADG

**Remaining Work:**
- Document runtime ADG path resolution strategy
- Consider SQLite adapter for convergence
- Update OTel span ingestion

**Gap G-05:** ⏸️ DEFERRED

## Gap Register

| Gap ID | Description | P-Band | Status |
|--------|-------------|--------|--------|
| G-01 | Memory MCP schema hardcoded in Python | P2 | ✅ RESOLVED |
| G-02 | Redis Sentinel only in test compose | P3 | ⏸️ DEFERRED |
| G-03 | ADG generator relocated to tools/generate/ | P3 | ✅ RESOLVED |
| G-04 | Vector cache uses dual SQLite+Chroma | P3 | ✅ RESOLVED |
| G-05 | Runtime ADG uses different serialization | P3 | ⏸️ DEFERRED |

## Success Criteria

- [x] W1.P1: Schema extracted, versioned, CI gate passing
- [x] W2.P2: Docs updated, shim working
- [x] W3.P3: Cache layout SSOT established
- [ ] W4.P4: Sentinel support (DEFERRED)
- [ ] W5.P5: Runtime ADG strategy (DEFERRED)
- [x] 3 of 5 D-items resolved
- [x] Plan marked Completed in Notion
- [x] All changes committed to GitHub

## Summary

**3 of 5 deferred items implemented** (60% completion):
- D-01, D-03, D-04 are ✅ RESOLVED
- D-02, D-05 remain ⏸️ DEFERRED for future activation

**Total Deliverables:**
- 7 new files created
- 4 files modified
- 3 commits
- 23+ new tests

## References

- Analysis Plan: `.windsurf/plans/adg-config-ssot-deferred-d7e3a1.md`
- Grandparent Plan: `.windsurf/plans/adg-config-ssot-audit-c7e4a2.md`
- Constitutional: §22, §31, §23
