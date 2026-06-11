---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\adg-config-ssot-redis-otel-deferred-f7a3d2.md'
original_relative_path: '_archive\\2026-05\\adg-config-ssot-redis-otel-deferred-f7a3d2.md'
source_sha256: 5718e7c1ecad070852873933b018b1e0f6c53d37e925aaec166cecc454c4c0e4
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
> **Archived 2026-05-25:** Current repo state sufficient. D-02/D-05 not required; `ADG_REDIS_URL` SSOT + three-bucket `v_runtime_proof` cover needs. Notion Archived.

# ADG Config SSOT — Redis & OTel Deferred Scope

**Slug:** `adg-config-ssot-redis-otel-deferred-f7a3d2`
**Status:** Archived
**Parent Plan:** `adg-config-ssot-uber-deferred-e8f2a3` (COMPLETED 2026-05-06)
**Tier:** T3 (cross-layer, config-discipline)
**Created:** 2026-05-06

## Purpose

Implementation backlog for remaining deferred items from `adg-config-ssot-uber-deferred-e8f2a3`:
- **D-02:** Redis Cluster Topology / Sentinel Migration (G-02)
- **D-05:** OTel Runtime ADG Path Resolution Convergence (G-05)

**This plan is intentionally NOT implemented** — it serves as an activation-ready backlog for future operational needs.

## Deferred Items

### D-02 — Redis Cluster Topology / Sentinel Migration

**Gap:** Production uses single-node Redis; Sentinel config exists only in `docker-compose.redis.yml` test profile.

**SSOT Violation:** `ADG_REDIS_URL` assumes single-node; no cluster-aware connection handling.

**Activation Triggers:**
- Production Redis failover required
- Cache availability becomes critical path
- Sentinel monitoring needed for HA

**Implementation Sketch (when activated):**
1. Add Sentinel connection fallback to `tools/adg/cache/redis_cache.py`
2. Support `REDIS_SENTINEL_HOSTS` env var (comma-separated)
3. Implement master discovery via Sentinel
4. Update `docker-compose.redis.yml` to production-grade topology
5. Add CI test for Sentinel failover scenario
6. Add advisory gate `check_redis_sentinel_config.py`

**Estimated Effort:** ~6k tokens  
**Dependencies:** Redis operational readiness, Docker Desktop cluster testing

---

### D-05 — OTel Runtime ADG Path Resolution Convergence

**Gap:** Runtime ADG uses custom binary serialization (RS/GS separators) in `system_learning/runtime_adg/store.py`; diverges from static ADG SQLite format.

**SSOT Violation:** Constitutional §23 acknowledges distinction, but no unified path resolution strategy.

**Activation Triggers:**
- Runtime ADG needs to query static ADG
- Unified observability dashboard required
- Storage format consolidation needed

**Implementation Sketch (when activated):**
1. Author ADR documenting runtime ADG path resolution strategy
2. Consider runtime ADG SQLite adapter (convergence with static)
3. Add cross-format query bridge if needed
4. Update OTel span ingestion to write to both formats
5. Add validation that runtime and static ADG are queryable together

**Estimated Effort:** ~6k tokens  
**Dependencies:** OTel runtime ADG review (may affect architecture)

## Activation Matrix

| Item | Blocker Risk | Effort | Activation Priority |
|------|--------------|--------|---------------------|
| D-02 | High | 6k | 1 (when HA needed) |
| D-05 | Medium | 6k | 2 (architectural) |

## Success Criteria (When Activated)

- [ ] Selected D-item implemented per sketch
- [ ] CI gates pass (including new gates if added)
- [ ] Parent plan Gap Register updated with "RESOLVED"
- [ ] This plan marked Completed in Notion
- [ ] Git commit with traceable message

## References

- Parent Plan: `.cursor/plans/adg-config-ssot-uber-deferred-e8f2a3.md`
- Grandparent Plan: `.cursor/plans/adg-config-ssot-deferred-d7e3a1.md`
- Great-grandparent Plan: `.cursor/plans/adg-config-ssot-audit-c7e4a2.md`
- Constitutional: §22 (graph-layer), §31 (SSOT folder routing), §23 (static vs runtime)
