---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_antipattern_persistence_wave7.md'
original_relative_path: 'RCA_antipattern_persistence_wave7.md'
source_sha256: 7bbf79ef9606d544e469650a01c8e0aa052c5e247841d9d8d3f3794b2f0fb440
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Antipattern Persistence Despite Removal Commits

**Date**: March 14, 2026
**Investigator**: Cascade AI
**Severity**: High - Misleading metrics causing incorrect Wave 7 scope

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The ADG reports **4,409 dead_imports** and **1,528 antipatterns** for Wave 7 burndown, despite multiple commits claiming to have removed these violations. Root cause: **ADG was generated BEFORE the Wave 1-6 anomaly fix commits were applied**, creating a temporal ordering issue where the index reflects pre-fix code state.

## Timeline Analysis

### ADG Generation
- **Timestamp**: `03142026_0655` (March 14, 2026 at 06:55 AM)
- **SQLite mtime**: Sat Mar 14 06:57:08 2026
- **Last commit before generation**: `42e204508f` - "test(W1-W6): ADG anomaly fix regression suite - 64 guardian tests"

### Wave 1-6 Anomaly Fixes (Applied AFTER ADG generation)
1. **c5757503a1** - fix(A-05): strip UWG imports from validators/ territory
2. **9947570353** - fix(A-07+A-01): GovernanceAgent dedup + validators/ mutation boundary
3. **fe07ad4399** - fix(A-02+A-04): PascalSovereigntyAgent + CodeJanitorAgent territory move
4. **894da0a36f** - fix(A-06): eliminate all 5 violates layer boundary edges
5. **9330ce939d** - fix(A-03+A-08): dependencygraph_validator UWG strip + StructuralValidatorAgent tempfile
6. **84fa913abb** - fix(A-11+A-13+A-14): confidence gate + gravity_leak_validator + read-only open audit

### ADG Regeneration
- **81b4d050b0** - "regen: ADG index after Wave 1-6 anomaly fixes" (AFTER the fixes)

## Current ADG State (Stale)

### Edge Relation Counts from SQLite
```
imports: 48,787
dead_imports: 4,409  ← STALE (pre-Wave 1-6 fixes)
antipattern: 1,528   ← STALE (pre-Wave 1-6 fixes)
covers: 7,868
violates: 2          ← Should be 0 after A-06 fix
```

### Redis Cache Status
- **Redis keys**: 170,621 keys loaded
- **Cache timestamp**: `03132026_1424` (March 13, 2026)
- **SQLite path**: `adg_indexed_03142026_0655.sqlite`
- **Status**: Redis cache is HOT but contains stale data from pre-fix ADG

## Root Cause

**Temporal Ordering Violation**: The ADG index at `03142026_0655` was generated from code state at commit `42e204508f`, which was BEFORE the Wave 1-6 anomaly fixes (commits A-01 through A-14) were applied. The subsequent commit `81b4d050b0` claims to regenerate the ADG "after Wave 1-6 anomaly fixes", but the artifacts in `artifacts/adg/` still have the `03142026_0655` timestamp, indicating they were NOT actually regenerated.

## Evidence

### 1. ADG Artifact Timestamps
All artifacts in `C:\Git\Agentic-Workflow\artifacts\adg\` have timestamp `03142026_0655`:
- `adg_indexed_03142026_0655.sqlite`
- `adg_file_graph_03142026_0655.json`
- `adg_governance_graph_03142026_0655.json`
- `adg_snapshot_03142026_0655.json`

### 2. Git Log Sequence
```
81b4d050b0 regen: ADG index after Wave 1-6 anomaly fixes  ← Claims regen
42e204508f test(W1-W6): ADG anomaly fix regression suite  ← ADG generated here
84fa913abb fix(A-11+A-13+A-14): confidence gate...        ← Fix applied AFTER
9330ce939d fix(A-03+A-08): dependencygraph_validator...   ← Fix applied AFTER
894da0a36f fix(A-06): eliminate all 5 violates edges     ← Fix applied AFTER
fe07ad4399 fix(A-02+A-04): PascalSovereigntyAgent...     ← Fix applied AFTER
9947570353 fix(A-07+A-01): GovernanceAgent dedup...      ← Fix applied AFTER
c5757503a1 fix(A-05): strip UWG imports...               ← Fix applied AFTER
```

### 3. Historical Anti-Pattern Removal Commits
Previous commits claiming complete removal:
- `4fc4497ab3` - "Complete anti-pattern burndown: 0 violations across all 7 categories"
- `78ba9c8278` - "fix: ADG anti-pattern burndown -- 72 violations suppressed to 0 new"
- `e82ab8b1ca` - "feat: Phase 1-2 Anti-Pattern Burndown (1862→0)"
- `1597b1138f` - "feat: Eliminate silent swallower anti-pattern - 640→0 violations"

These commits DID remove antipatterns, but the ADG was never regenerated after those fixes, so the index still reflects the OLD code state.

## Impact

### Wave 7 Scope Inflation
The Wave 7 plan proposes burning down:
- **4,409 dead_imports** (likely already fixed)
- **1,528 antipatterns** (likely already fixed)

This represents **~6,000 violations** that may not actually exist in the current codebase.

### Wasted Effort Risk
Without regenerating the ADG first, Wave 7 work will:
1. Target violations that no longer exist
2. Generate false-positive fixes
3. Create unnecessary churn
4. Waste development time

## Remediation

### Immediate Actions Required

1. **Regenerate ADG from current HEAD**
   ```bash
   python C:\Git\Agentic-Workflow\tools\generate_full_adg.py
   ```

2. **Re-ingest into Redis**
   ```bash
   python C:\Git\Agentic-Workflow\tools\adg\adg_redis_ingest.py --force
   ```

3. **Verify actual violation counts**
   ```python
   import sqlite3
   conn = sqlite3.connect('artifacts/adg/adg_indexed_<NEW_TIMESTAMP>.sqlite')
   cursor = conn.cursor()
   cursor.execute("SELECT relation_type, COUNT(*) FROM edges WHERE relation_type IN ('dead_imports', 'antipattern') GROUP BY relation_type")
   print(cursor.fetchall())
   ```

4. **Revise Wave 7 scope** based on actual current violation counts

### Process Improvement

**Constitutional Amendment Required**: Add ADG staleness check to pre-commit hooks:
- Block commits if ADG timestamp < last code-modifying commit
- Require ADG regeneration after any structural refactoring
- Add ADG generation timestamp to commit message template

## Lessons Learned

1. **ADG regeneration must be atomic** - The commit claiming "regen: ADG index after Wave 1-6 anomaly fixes" did NOT actually regenerate the artifacts (timestamps unchanged)

2. **Timestamp verification is critical** - Always verify artifact timestamps match claimed regeneration

3. **Pre-work protocol violation** - Wave 7 planning violated the ADG pre-work protocol: "NEVER skip ADG — no query, analysis, refactor, or code change begins without verifying ADG cache"

4. **Stale cache is worse than no cache** - A hot Redis cache with stale data is more dangerous than a cold cache, because it appears valid but contains incorrect information

## Conclusion

The antipatterns were NOT reintroduced. The ADG simply never saw the fixes because it was generated from pre-fix code state. Wave 7 scope is based on stale data and must be recalculated after ADG regeneration.

**Next Step**: Run `/adg-redis-refresh` workflow to regenerate ADG from current HEAD before proceeding with any Wave 7 work.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

