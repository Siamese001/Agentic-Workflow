# P0 Target Matrix — 2026-03-15

**Base:** 3,010 modules with `calls` edges

## Thresholds & Targets

| Metric | Threshold | Target Modules | Current Modules | Current % | Deficit | Status |
|---|---:|---:|---:|---:|---:|---|
| trace coverage (records_execution_trace) | 90% | 2,709 | 1,803 | 59.9% | 906 | ✗ |
| guardrail coverage (applies_guardrail) | 80% | 2,408 | 1,180 | 39.2% | 1,228 | ✗ |
| policy binding (reads_policy_state) | 95% | 2,860 | 1,335 | 44.4% | 1,525 | ✗ |
| state authority (union of state edges) | 100% | 3,010 | 1,333 | 44.3% | 1,677 | ✗ |
| evaluation linkage (invokes_eval) | 80% | 2,408 | 201 | 6.7% | 2,207 | ✗ ⚠ |
| replay key (emits_replay_key) | 90% | 2,709 | 76 | 2.5% | 2,633 | ✗ |
| determinism digest (emits_determinism_digest) | 90% | 2,709 | 76 | 2.5% | 2,633 | ✗ |
| trace signing (signs_execution_trace) | 90% | 2,709 | 1,161 | 38.6% | 1,548 | ✗ |

## Wireable vs Non-Wireable Dimensions

**Directly wireable** (module-level emit call insertion):
- records_execution_trace → `_emit_records_execution_trace`
- applies_guardrail → `_emit_applies_guardrail`
- reads_policy_state → `_emit_reads_policy_state`
- snapshots_state → `_emit_snapshots_state`
- emits_replay_key → `emit_replay_key`
- emits_determinism_digest → `emit_determinism_digest`
- signs_execution_trace → `_emit_signs_execution_trace`

**Not directly wireable** (requires actual code patterns):
- invokes_eval — detected by `_DynamicExecutionVisitor` when modules use `eval()`, `exec()`, `importlib`
- reads_runtime_state — detected by `_AttributeVisitor` attribute access patterns

## Micro-Wave Plan

Total deficit modules (missing ≥1 wireable dimension): **2,952**
Waves needed at 15 modules/wave: **~197 waves**

Priority order (highest ROI → wire all 7 dimensions per module):
1. Modules missing all 7 wireable dims (highest ROI per file touch)
2. Modules missing 6 dims
3. ... descending to 1 dim
