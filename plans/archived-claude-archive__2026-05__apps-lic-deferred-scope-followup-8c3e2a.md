---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-lic-deferred-scope-followup-8c3e2a.md'
original_relative_path: '_archive\\2026-05\\apps-lic-deferred-scope-followup-8c3e2a.md'
source_sha256: b40b9314856682f7f320b749964b014e6e17d5395a2aa81fd4d8df5fb79fcf4c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Deferred Scope Follow-up Plan

> **Slug:** apps-lic-deferred-scope-followup-8c3e2a  
> **Status:** Not Started (in Notion)  
> **Origin:** apps-lic-p2p3-deferred-scope-execution W1-W6 gap register  
> **Created:** 2026-05-05

---

## 1. Executive Summary

This plan captures deferred scope items from the apps_lic P2/P3 deferred scope execution (W1-W6) that require external dependencies, production configuration, or were intentionally descoped from the initial implementation. These items are **non-blocking** for the core multi-touch infrastructure but required for production hardening.

---

## 2. Deferred Scope Register

### Gap G1: C0 Retrieval Sources Population

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Description** | C0 retrieval sources not yet populated |
| **Impact** | FEC stays template-only (no grounded evidence) |
| **Owner** | C0 team |
| **Source Wave** | W4 |
| **Effort** | ~2-3 days |

**Details:**
- Research bridge implemented with forward-compatible C0 retrieval path
- Template path works (research_snippets + competitive_signals)
- C0 path requires upstream C0 retrieval service to populate `c0_retrieval_sources`
- No code changes needed in apps_lic — data source issue only

**Acceptance Criteria:**
- [ ] C0 retrieval service provides sources for apps_lic queries
- [ ] `c0_retrieval_sources` present in run_context
- [ ] FEC producer outputs `grounded=True` with C0 data
- [ ] End-to-end test with real C0 data passes

---

### Gap G2: Redis Coordination Fabric Production Config

| Attribute | Value |
|-----------|-------|
| **ID** | G2 |
| **Description** | Redis coordination fabric requires production configuration |
| **Impact** | Scheduling may fail in production |
| **Owner** | Infra team |
| **Source Wave** | W2-W3 |
| **Effort** | ~1-2 days |

**Details:**
- TouchScheduler and WakeHandler implemented
- Redis fabric integration code complete
- Requires production Redis cluster configuration
- Connection strings, failover, monitoring need setup

**Acceptance Criteria:**
- [ ] Production Redis cluster provisioned
- [ ] Connection configuration deployed
- [ ] Health checks passing
- [ ] Failover tested
- [ ] Touch scheduling works end-to-end in prod

---

### Gap G3: Identity Service L4 Storage Schema Migration

| Attribute | Value |
|-----------|-------|
| **ID** | G3 |
| **Description** | Identity service L4 storage needs schema migration |
| **Impact** | Context loss on restart (no persistence) |
| **Owner** | L4 team |
| **Source Wave** | W2-W3 |
| **Effort** | ~3-5 days |

**Details:**
- Identity propagation implemented (in-memory)
- ContextCarryForwardBridge works for active session
- L4 storage schema exists (`apps_lic_identity_context`)
- Migration from legacy identity format needed

**Acceptance Criteria:**
- [ ] Schema migration script written
- [ ] Legacy identity data migrated
- [ ] Context survives restart
- [ ] Rollback tested

---

## 3. Additional Deferred Items

### W4: Real apps_research Integration

**Current State:**
- Bridge implemented with GovernedResearchRun integration
- C0 retrieval wiring complete
- Uses mock/fail-soft when service unavailable

**Deferred:**
- Real apps_research service connectivity
- End-to-end integration testing with live service
- Performance tuning for research latency

**Acceptance Criteria:**
- [ ] Service discovery configured
- [ ] Health checks pass
- [ ] Latency < 2s for standard queries
- [ ] Fail-soft verified when service down

---

### W5: Production Migration Run

**Current State:**
- Migration script implemented (dry-run, execute, verify)
- Rollback runbook documented
- Tested with mock data

**Deferred:**
- Real campaign inventory from production
- Actual migration execution (pending infra readiness)
- Post-migration verification with real data

**Acceptance Criteria:**
- [ ] Production inventory scanned
- [ ] Compatibility report reviewed
- [ ] Dry-run successful
- [ ] Maintenance window scheduled
- [ ] Migration executed
- [ ] Verification complete

---

### W6: Production E2E Test Execution

**Current State:**
- 12 E2E tests implemented
- 16 performance benchmarks defined
- All passing in test environment

**Deferred:**
- Execution against production-like environment
- Load testing at production scale
- Performance baseline establishment

**Acceptance Criteria:**
- [ ] E2E tests pass in staging
- [ ] Load test 10k+ touches
- [ ] Performance baseline recorded
- [ ] Latency targets verified

---

## 4. Wave Structure

| Wave | Focus | Dependencies | Est. Effort | Status |
|------|-------|--------------|-------------|--------|
| D1 | C0 Data Source Integration | C0 team | 2-3 days | Not Started |
| D2 | Redis Production Config | Infra team | 1-2 days | Not Started |
| D3 | L4 Schema Migration | L4 team | 3-5 days | Not Started |
| D4 | Production Migration | All above | 2-3 days | Not Started |
| D5 | E2E/Perf Validation | D1-D4 | 2-3 days | Not Started |

---

## 5. Dependencies & Blockers

### External
- **C0 retrieval service** must expose sources for apps_lic queries
- **Redis production cluster** must be provisioned and configured
- **L4 identity storage** must accept apps_lic schema

### Cross-Team
- C0 team owns G1
- Infra team owns G2
- L4 team owns G3
- apps_lic team coordinates D4-D5

---

## 6. Success Criteria

- [ ] All 3 gaps (G1, G2, G3) closed
- [ ] Production migration completed
- [ ] E2E tests pass in production
- [ ] Performance targets met at scale
- [ ] Monitoring and alerting active

---

## 7. Related Documents

- Parent Plan: `.windsurf/plans/apps-lic-p2p3-deferred-scope-execution.md`
- W1-W6 Implementation: See git history for W1-W6 commits
- Rollback Runbook: `docs/runbooks/apps_lic_migration_rollback.md`

---

## 8. Notes

This is a **tracking-only plan**. No implementation work is scoped here — all implementation was completed in W1-W6. This plan tracks external dependencies and production hardening work.

---

*Generated: 2026-05-05*  
*Owner: apps_lic team*
