---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\runtime-adg-tier2h-tier3-c4d8e2.md'
original_relative_path: '_archive\\2026-05\\runtime-adg-tier2h-tier3-c4d8e2.md'
source_sha256: 8c1ed8141367e514ed5217ea8e138af634b5befc5ee682e35a689c05b3fa2eed
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Runtime ADG Tier 2 Harden + Tier 3 seal_step adoption

**Slug**: `runtime-adg-tier2h-tier3-c4d8e2`
**Status**: Active
**Tier**: T2
**Parent**: `runtime-adg-tier2-emit-sites-b3e9a7`

## Scope

### Tier 2 Harden
1. Unify `trace_id` between `runtime.trace_root` and the OTel-issued trace_id on child spans. Today `emit_trace_root` issues a uuid BEFORE `super().trace_orchestrator()`, so child spans get OTel's trace_id and root is orphaned.
2. Promote `tools/debug/_tier2_smoke.py` to a real integration test under `tests/integration/system_learning/runtime_adg/`.
3. Concurrency guard: add a test that proves two nested/sequential `trace_orchestrator()` calls don't leak trace_id state.

### Tier 3 seal_step adoption
4. Add `contextvars.ContextVar`-based current-adapter lookup in `runtime_span_emitter.py` so any code downstream of `trace_orchestrator()` can call `seal_step()` without plumbing the adapter reference.
5. Wire `AutoPersistenceTracingAdapter.trace_orchestrator` to set/reset the contextvar.
6. Wrap `HOPPipelineExecutor._process` handler dispatch with `seal_step()` — one clean step boundary per HOP stage.

## Success Criteria

1. After harden: `runtime.trace_root` carries the same `trace_id` as child spans emitted by OTel tracer.
2. Integration test exercises orchestrator → HOPPipelineExecutor → snapshot contains `L2.step.seal` with populated `output_hash`.
3. Concurrency test proves contextvar + trace_id behave correctly under sequential re-entry.
4. 100+ tests passing.

## Files Touched

| File | Action |
|---|---|
| `system_learning/runtime_adg/runtime_span_emitter.py` | Add `set_current_adapter`/`get_current_adapter`/`_current_adapter_var` |
| `system_learning/runtime_adg/auto_persistence.py` | Fix trace_id unification + install contextvar |
| `apps_lic/reasoning/HOPPipelineExecutor.py` | Wrap handler dispatch in `seal_step()` |
| `tests/integration/system_learning/runtime_adg/test_tier2_e2e.py` | New |
| `tests/unit/system_learning/runtime_adg/test_runtime_span_emitter.py` | +contextvar tests |
