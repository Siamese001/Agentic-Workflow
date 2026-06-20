---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\p1-d2-default-enable-b7e3f9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\p1-d2-default-enable-b7e3f9.md'
source_sha256: 748aa218194517fe2b7fba1782158a2d20149e0dec6dd43879410bbda017ca5c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P1 — Enable D2 Semantic Cache by Default

> Parent: deferred-scope-spine-refinement-5e3d1b
> Scope: Change SEMANTIC_CACHE_D2_ENABLED default from "0" to "1"

## Context

W3 wired `learn()` in the R4 entrypoint, but the D2 cache infrastructure
(`SemanticCacheManager._init_gptcache`) and the R1B pre-flight check in
`apps_rg/__main__.py` both gate on `SEMANTIC_CACHE_D2_ENABLED=1`.
Currently defaults to `"0"` (disabled), making W3's `learn()` dead code
in production.

## Change

Flip the default from `"0"` to `"1"` in both locations:
- `agentic_core/L4_state/utils/memory/semantic_cache_manager.py:_init_gptcache`
- `apps_rg/__main__.py` (R1B pre-flight gate)

The infrastructure already fails gracefully: if ChromaDB/Redis are unavailable,
the cache enters stateless mode. No new failure modes introduced.

## Acceptance

- D2 cache initializes on startup without env flag
- R1B semantic cache check runs without env flag
- Existing `SEMANTIC_CACHE_D2_ENABLED=0` override still works to disable
