---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hardened-adg-query-layer-eliminate-reports-8a3f.md'
original_relative_path: 'hardened-adg-query-layer-eliminate-reports-8a3f.md'
source_sha256: bed309970e839e40dfaa9645cc80e99ec6327e830f0ec4c027079d921fd2358b
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hardened ADG Query Layer — Eliminate Report-Driven Debugging

Replace the fake boundary report generator with direct graph queries to SQLite (authority) and Redis (hot cache), exposing a hardened query service, invariant runner, and debug CLI.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Query Service Core | adg_query_service.py + contracts | A | 16,000 🟢 |
| Wave 2 | Invariant Engine | adg_invariant_runner.py + findings | B | 12,000 🟢 |
| Wave 3 | Debug CLI + Integration | adg_debug_cli.py + orchestrator updates | C | 9,000 🟢 |
| Wave 4 | CI Gates + Parity Check | CI invariant gates + Redis parity | D | 7,000 🟢 |

**Total: 44,000 tokens across 4 waves, all GREEN**

*Token estimates computed via ContextWindowEstimator (code: 0.35 chars/token, JSON: 0.33 chars/token). All waves under 19.7K warning threshold.*

---

## Gap Register

**GAP-1: Report is Fake Diagnostic Dependency**
- The boundary report generator (`generate_full_adg.py:1764-1783`) has hardcoded zeros for `unresolved_imports` and `total_unresolved`
- It does NOT query SQLite or Redis — it returns a template with fake data
- The repair orchestrator trusts this report, missing real violations like `apps_lic` → `archives/` imports
- **Impact**: ADG repair is blind to actual graph defects; debugging requires manual Redis pokes

**GAP-2: No Unified Query Layer**
- No single service to query nodes, edges, import resolution, or boundary violations
- Tools reinvent queries: `sqlite_analyzer.py`, `repair_orchestrator.py`, manual Redis commands
- **Impact**: Inconsistent debugging paths, no invariant enforcement, report-driven workflows

**GAP-3: Graph Facts vs Policy Findings Not Separated**
- Current reports mix "node exists" (fact) with "unresolved import" (finding)
- No way to reproduce findings from (facts + policy pack)
- **Impact**: Non-deterministic debugging, non-replayable decisions

**GAP-4: Redis Not Snapshot-Bound**
- Redis keys are not namespaced by snapshot ID
- No verification that Redis matches SQLite for a given snapshot
- **Impact**: Risk of reading stale cache as authoritative

---

## Execution Plan

### Phase 1 — Query Service Core
**Scope**: Build `tools/adg/services/adg_query_service.py` with unified SQLite/Redis access

**Key Components**:
1. `ADGQueryService` class with snapshot-bound queries
2. Methods: `get_node()`, `get_edges()`, `find_unresolved_imports()`, `get_snapshot_metadata()`
3. Redis acceleration with automatic SQLite fallback
4. Snapshot parity verification on every query

**Commands**:
```bash
# Create service directory
mkdir -p tools/adg/services

# Implementation sequence
# 1. Define contracts in agentic_core/adg/contracts/query_contracts.py
# 2. Implement ADGQueryService with SQLite primary, Redis cache
# 3. Add snapshot lineage verification
# 4. Unit tests in tests/unit/tools/adg/services/test_query_service.py
```

**Acceptance**:
- [ ] `get_node(3939)` returns apps_lic module with 98 import edges
- [ ] `find_unresolved_imports("apps_lic")` returns edges 257243, 257244, 257246
- [ ] Redis cache hit logs metadata; SQLite fallback on cache miss
- [ ] All queries include snapshot_id validation

### Phase 2 — Invariant Engine
**Scope**: Build `tools/adg/services/adg_invariant_runner.py` for deterministic checks

**Key Components**:
1. `InvariantRunner` class with pluggable check suites
2. Checks: `ImportResolutionCheck`, `EntityTypeCheck`, `BoundaryViolationCheck`, `RedisParityCheck`
3. Structured `FindingPacket` output (JSON, not prose)
4. Policy pack separation: graph facts vs policy findings

**Commands**:
```bash
# Implementation sequence
# 1. Define FindingPacket dataclass in contracts
# 2. Implement ImportResolutionCheck (symbol → module parent validation)
# 3. Implement BoundaryViolationCheck (apps_* → archives detection)
# 4. Implement RedisParityCheck (node count, sampled edge hashes)
# 5. Unit tests for each invariant
```

**Acceptance**:
- [ ] `ImportResolutionCheck` flags edge 257243 as `symbol_without_module_parent`
- [ ] `BoundaryViolationCheck` flags archives imports with `forbidden_archive_dependency`
- [ ] `RedisParityCheck` passes when Redis matches SQLite for snapshot 04022026_2140
- [ ] Output is valid FindingPacket JSON, zero prose

### Phase 3 — Debug CLI + Orchestrator Updates
**Scope**: Build `tools/adg/adg_debug_cli.py` and update repair orchestrator

**Key Components**:
1. CLI commands: `show-node`, `show-imports`, `find-unresolved`, `explain-violation`, `compare-snapshot-cache`
2. Replace orchestrator's report consumption with direct query service calls
3. Remove boundary report dependency from repair path
4. Add invariant checks as CI gates

**Commands**:
```bash
# CLI implementation
python tools/adg/adg_debug_cli.py show-node --id 3939 --snapshot 04022026_2140
python tools/adg/adg_debug_cli.py find-unresolved --scope apps_lic
python tools/adg/adg_debug_cli.py explain-violation --edge-id 257243

# Orchestrator update
# 1. Remove BoundaryReportParser dependency from repair_orchestrator.py
# 2. Wire ADGQueryService.detect_deficiencies() instead
# 3. Update run() to call invariant runner for pre-flight checks
```

**Acceptance**:
- [ ] CLI commands return structured JSON, not tables
- [ ] Repair orchestrator no longer reads boundary_report_*.json
- [ ] Orchestrator detects apps_lic → archives imports via query service
- [ ] CI passes with new invariant gates

### Phase 4 — CI Gates + Parity Enforcement
**Scope**: Add CI invariant gates and strict Redis/SQLite parity

**Key Components**:
1. GitHub Actions job: `adg-invariant-gates.yml`
2. Gates: Graph integrity, import resolution, boundary policy, cache parity
3. Fail on any finding with severity >= HIGH
4. Redis snapshot namespacing: `adg:snapshot:<id>:node:<id>`

**Commands**:
```bash
# CI gate
python tools/adg/services/adg_invariant_runner.py --snapshot 04022026_2140 --gate ci

# Redis namespacing migration
# 1. Update adg_redis_ingest.py to prefix keys with snapshot ID
# 2. Update MCP tools to read namespaced keys
# 3. Backward compatibility: fallback to legacy key on miss
```

**Acceptance**:
- [ ] CI fails if unresolved imports exist (severity >= HIGH)
- [ ] CI fails if Redis parity check fails
- [ ] All Redis keys namespaced by snapshot ID
- [ ] Zero report-driven logic in any workflow

---

## Rules

1. **SQLite is the only source of truth** — Redis is a read cache, reports are renderers
2. **Every query must include snapshot_id** — no implicit "latest" assumptions
3. **All findings must be reproducible** — graph facts + policy pack = finding
4. **No orchestrator may consume report files** — query service only
5. **Redis keys must be snapshot-namespaced** — parity checks on every access
6. **Invariants are CI gates** — not manual inspection tasks

---

## Success Criteria

- [ ] `adg_query_service.py` provides unified SQLite/Redis access with snapshot binding
- [ ] `adg_invariant_runner.py` produces deterministic FindingPacket JSON
- [ ] `adg_debug_cli.py` exposes graph queries without report intermediaries
- [ ] Repair orchestrator queries graph directly, ignores boundary report
- [ ] CI invariant gates block on unresolved imports, boundary violations, cache parity failures
- [ ] Redis keys namespaced by snapshot ID with automatic lineage verification

---

## Implementation Commands

```bash
# Full implementation sequence
python -m pytest tests/unit/tools/adg/services/ -v
python tools/adg/adg_debug_cli.py find-unresolved --scope apps_lic
python tools/adg/services/adg_invariant_runner.py --snapshot 04022026_2140 --gate ci
```

---

## Rollback Strategy

If things go wrong:
1. Revert orchestrator to report-driven path (boundary report still exists)
2. Keep legacy Redis keys alongside namespaced keys during transition
3. CI gates start as warnings (severity < CRITICAL), escalate to failures after validation
4. Maintain sqlite_analyzer.py as fallback query path during migration

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Query service coverage | 100% of prior report use cases | Test: all boundary report fields queryable via service |
| Invariant detection rate | >= 95% of actual violations | Test: apps_lic archives imports detected |
| Cache parity | 100% match SQLite/Redis | Test: sampled edge hashes identical |
| CI gate failures | Zero false positives | Test: 10 consecutive clean runs |
| Debug CLI latency | < 500ms per query | Benchmark: 100 random node lookups |

