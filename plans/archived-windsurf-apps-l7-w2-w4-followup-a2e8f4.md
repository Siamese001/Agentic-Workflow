---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-l7-w2-w4-followup-a2e8f4.md'
original_relative_path: 'apps-l7-w2-w4-followup-a2e8f4.md'
source_sha256: dd2f2279c8db45c1f266da0745b92ff541d11222aab576c8e841d9f28968ef20
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps L7 W2-W4 Follow-up Plan

**Slug**: `apps-l7-w2-w4-followup-a2e8f4`
**Tier**: T3
**Status**: Draft
**Created**: 2026-05-06
**Authors**: Cursor Agent
**Parent**: `apps-l7-deferred-scope-followup-a1d9e3` (W1 completed)
**Depends On**: `apps-l7-deferred-scope-followup-a1d9e3`

PLAN_CREATED: slug=apps-l7-w2-w4-followup-a2e8f4 path=.windsurf/plans/apps-l7-w2-w4-followup-a2e8f4.md tier=T3

## 1. Problem Statement

This plan captures the remaining 3 waves (W2-W4) from `apps-l7-deferred-scope-followup-a1d9e3` after W1 (apps_eval spine retrofit) was completed.

## 2. Scope

### Wave 2: apps_repo_brief spine retrofit
**Estimated**: ~8k tokens

apps_repo_brief invokes its own integrations runner directly without `governed_run`. Requires:
- Analysis of current entrypoint
- EmissionConfig design  
- Path refactoring to `governed_run`
- Testing and verification

**Success Criteria**: apps_repo_brief emits 4 L7 artifacts on next run

### Wave 3: Fort Knox certification extension
**Estimated**: ~6k tokens

Extend Fort Knox certification (`tools/cert/emit_l7_plane_evidence.py`, `tools/certification/generate_100pct_runtime_proof.py`) to bind apps_* L7 artifacts to RTC-REQ-130..139 chain enumeration.

**Success Criteria**: Fort Knox certification includes apps_* L7 artifacts

### Wave 4: Legacy entrypoints disposition
**Estimated**: ~4k tokens (if retire) or ~12k tokens (if wire all)

Disposition 6 legacy entrypoints lacking L7 emit:
- `integrated_exact_cache_run.py`
- `integrated_fallback_run.py`
- `integrated_managed_workflow_real_run.py`
- `integrated_single_action_run.py`
- `integrated_uwg_block_run.py`
- `integrated_uwg_commit_run.py`

**Decision**: Wire with L7 emit OR retire/archive (ADR required)

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W2 | P2.1-P2.4 | apps_repo_brief spine retrofit | ~8k | Draft |
| W3 | P3.1-P3.3 | Fort Knox extension for apps_* | ~6k | Draft |
| W4 | P4.1 | Legacy entrypoints disposition ADR | ~4k | Draft |

## 4. Implementation Notice

This plan is NOT to be implemented until explicitly authorized. Implement one wave at a time per instruction.
