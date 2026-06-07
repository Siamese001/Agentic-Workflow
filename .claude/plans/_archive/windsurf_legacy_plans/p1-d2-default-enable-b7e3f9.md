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
