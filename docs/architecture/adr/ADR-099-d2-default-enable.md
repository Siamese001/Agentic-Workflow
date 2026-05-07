# ADR-099: Enable D2 Semantic Cache by Default

**Status**: ACCEPTED
**Date**: 2026-05-07
**Phase**: P1 (deferred-scope-spine-refinement-5e3d1b)
**Deciders**: Cascade + user Author-Gate
**ADG Snapshot**: `artifacts/adg/adg_indexed_20260507.sqlite`

---

## Context (SCQA)

- **Situation**: The D2 semantic cache (`SemanticCacheManager`) provides
  R1B semantic recall and post-run `learn()` writeback for apps_rg. W3
  (plan `agentic-spine-diagram-refinement-a3f7c2`) wired `learn()` in
  the R4 entrypoint. The infrastructure fails gracefully to stateless
  mode when ChromaDB/Redis are unavailable.

- **Complication**: The cache was gated behind `SEMANTIC_CACHE_D2_ENABLED`
  env var defaulting to `"0"` (disabled). This made W3's `learn()` dead
  code in production — the spine diagram implied D2 was active, but it
  was opt-in only.

- **Question**: Should D2 semantic cache be enabled by default?

- **Answer**: Yes. Flip the default from `"0"` to `"1"` in all three
  gate locations.

---

## Decision

Enable D2 semantic cache by default. Change `os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0")`
to `os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "1")` in:
- `agentic_core/L4_state/utils/memory/semantic_cache_manager.py:_init_gptcache`
- `apps_rg/__main__.py` R1B pre-flight gate
- `apps_rg/__main__.py` R1B post-run store gate

Override remains available via `SEMANTIC_CACHE_D2_ENABLED=0`.

---

## Consequences

### Positive
- W3 `learn()` call is no longer dead code.
- R1B semantic cache provides actual recall on subsequent runs.
- Spine diagram accurately reflects runtime behavior.

### Negative
- ChromaDB/SQLite initialization runs on every cold start.
- Slight latency increase (~50ms) on first cache access.
- Mitigated by graceful fallback to stateless mode.

### Neutral
- Existing `SEMANTIC_CACHE_D2_ENABLED=0` override still works.

---

## Alternatives Considered

1. **Auto-enable on first successful L2**: Complex, unpredictable timing.
   Rejected — explicit env flag is simpler and more debuggable.
2. **Keep disabled, document opt-in**: Perpetuates the gap between diagram
   and reality. Rejected.
3. **Remove the gate entirely**: Too aggressive — operators need a kill
   switch. Rejected.

---

## References

- Plan: `.windsurf/plans/p1-d2-default-enable-b7e3f9.md`
- Commit: `6c0bf44`
- Parent: `deferred-scope-spine-refinement-5e3d1b`
