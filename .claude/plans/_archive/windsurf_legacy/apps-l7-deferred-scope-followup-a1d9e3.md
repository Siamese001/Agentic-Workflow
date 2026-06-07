# Apps L7 Deferred Scope Follow-up Plan

**Slug**: `apps-l7-deferred-scope-followup-a1d9e3`
**Tier**: T3
**Status**: Completed (W1 done, W2-W4 split to follow-up)
**Created**: 2026-05-06
**Authors**: Cursor Agent
**Parent**: `apps-l7-coverage-spine-wide-c5e8d2` (W1-W3 completed 2026-05-06)
**Depends On**: `apps-l7-coverage-spine-wide-c5e8d2` (must be Completed)

PLAN_CREATED: slug=apps-l7-deferred-scope-followup-a1d9e3 path=.windsurf/plans/apps-l7-deferred-scope-followup-a1d9e3.md tier=T3

## 1. Problem Statement

The umbrella plan `apps-l7-coverage-spine-wide-c5e8d2` closed the L7 gap for 7 of 8 production apps. Two apps remain outside the spine emission system and do not emit L7 artifacts:

| App | Current Path | Gap |
|---|---|---|
| `apps_eval` | Direct `__main__` shim → L1/L2/L0 without `governed_run` | No spine wrapping at all |
| `apps_repo_brief` | Own integrations runner, direct invocation | No `governed_run` usage |

Additionally, the Fort Knox certification system does not currently bind apps_* L7 artifacts to the RTC-REQ-130..139 chain enumeration.

Finally, 6 legacy entrypoints lack L7 emit but have no current production callers; they should either be wired or retired.

## 2. Goal

Wire the 2 remaining unspined apps into `governed_run` (or create app-specific L7 emit if architectural constraints prevent spine adoption), extend Fort Knox to bind apps_* evidence, and disposition the 6 legacy entrypoints.

## 3. Scope

### Deferred Item 1: apps_eval spine retrofit
**Source**: `apps-l7-coverage-spine-wide-c5e8d2` §13 DEFERRED_SCOPE

apps_eval runs as a direct `__main__` shim that delegates to L1/L2/L0 without using `governed_run` or any L7-emitting entrypoint. Wiring apps_eval into `governed_run` is an architectural change (~10k tokens) requiring:

- Analysis of current entrypoint structure
- Design of EmissionConfig for apps_eval
- Refactor of execution path to use `governed_run` context manager
- Regression testing
- Live verification

**Estimated**: ~10k tokens

### Deferred Item 2: apps_repo_brief spine retrofit
**Source**: `apps-l7-coverage-spine-wide-c5e8d2` §13 DEFERRED_SCOPE

apps_repo_brief invokes its own integrations runner directly without `governed_run`. Same shape as apps_eval gap. Requires:

- Analysis of current entrypoint
- EmissionConfig design
- Path refactoring to `governed_run`
- Testing and verification

**Estimated**: ~8k tokens

### Deferred Item 3: Fort Knox certification extension
**Source**: `apps-l7-coverage-spine-wide-c5e8d2` §13 DEFERRED_SCOPE

The Fort Knox certification compile (`tools/cert/emit_l7_plane_evidence.py`, `tools/certification/generate_100pct_runtime_proof.py`) does not currently include apps_* runtime evidence in its RTC-REQ-130..139 chain enumeration.

After the parent plan lands, this follow-up plan extends Fort Knox to bind apps_* L7 artifacts to the certification universe.

**Estimated**: ~6k tokens

### Deferred Item 4: Legacy entrypoints disposition
**Source**: `apps-l7-coverage-spine-wide-c5e8d2` §13 DEFERRED_SCOPE

5 currently-unused legacy entrypoints lack L7 emit but have no current production callers:

- `integrated_exact_cache_run.py`
- `integrated_fallback_run.py`
- `integrated_managed_workflow_real_run.py`
- `integrated_single_action_run.py`
- `integrated_uwg_block_run.py`
- `integrated_uwg_commit_run.py`

Decision required: wire with L7 emit OR retire/archive. ADR needed.

**Estimated**: ~4k tokens (if retire) or ~12k tokens (if wire all)

## 4. Non-Goals

- No changes to `build_how_trace` input contract
- No modification of L7 schema or HowTrace structure
- No migration of already-wired apps (apps_rg, apps_lic, etc.)
- No changes to the 3 already-L7-wired entrypoints

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | P1.1-P1.4 | apps_eval spine retrofit | ~10k | **✅ COMPLETED** |
| W2 | P2.1-P2.4 | apps_repo_brief spine retrofit | ~8k | Deferred to follow-up |
| W3 | P3.1-P3.3 | Fort Knox extension for apps_* | ~6k | Deferred to follow-up |
| W4 | P4.1 | Legacy entrypoints disposition ADR | ~4k | Deferred to follow-up |

## 6. Success Criteria

- apps_eval emits 4 L7 artifacts on next run
- apps_repo_brief emits 4 L7 artifacts on next run
- Fort Knox certification includes apps_* L7 artifacts in RTC-REQ-130..139
- Legacy entrypoints either emit L7 or are archived

## 7. Risk & Rollback

**Risk**: Medium. apps_eval and apps_repo_brief may have architectural constraints preventing `governed_run` adoption. May require app-specific L7 emit blocks instead.

**Rollback**: Per-wave revert. Each wave is independent.

## 8. References

- Parent: `.windsurf/plans/apps-l7-coverage-spine-wide-c5e8d2.md`
- `apps_eval/__main__.py` — current entrypoint
- `apps_repo_brief/` — current runner structure
- `tools/cert/emit_l7_plane_evidence.py` — Fort Knox binder
- `tools/certification/generate_100pct_runtime_proof.py` — proof generator

## 9. Completion Summary

**W1 COMPLETED 2026-05-06:**
- Modified `apps_eval/__main__.py` to use `governed_run` context manager
- Added EmissionConfig with SINGLE_STEP execution form
- Added `_ensure_route_registry()` helper for governed_run compatibility
- Created regression test `test_governed_run_integration.py`
- Git commit: `8865c87c56`

**Remaining W2-W4 captured in:** `.windsurf/plans/apps-l7-w2-w4-followup-a2e8f4.md`

## 10. Implementation Notice

W1 implemented per user authorization. W2-W4 deferred to follow-up plan per "one wave at a time" instruction.
