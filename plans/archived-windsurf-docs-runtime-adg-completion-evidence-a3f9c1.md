---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\runtime-adg-completion-evidence-a3f9c1.md'
original_relative_path: 'runtime-adg-completion-evidence-a3f9c1.md'
source_sha256: 3a64b413a8e09cc852cd3637f56e29c648b3fb70fca9d4690733decaf0ea4eef
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime ADG Completion Evidence

**Date:** 2025
**Status:** COMPLETE — all scope items verified

---

## Design Decision: Snapshot-based Runtime ADG

**Choice:** Per-execution-trace snapshot (Option B)

**Rationale:**
- Each agent execution has a natural boundary: one OTel trace
- Snapshot captures the full execution graph atomically at trace end
- Content-addressed by trace_id + span tree hash = deterministic, idempotent, safe to replay
- Fits exactly into existing `TelemetrySlice` + `FileBackedVersionStore` seam
- No new storage subsystem required
- "What the system did" during one run = one snapshot

**Pipeline:**
```
[Agent execution]
    → spans buffered in OpenTelemetryTracingAdapter._completed_spans
    → drain_completed_spans() at trace boundary
    → RuntimeADGMaterializer.materialize(spans, mission) → RuntimeADGSnapshot
    → RuntimeADGStore.persist(snapshot) → version_id (via FileBackedVersionStore)
```

---

## Files Created / Modified

### New: `system_learning/runtime_adg/` package

| File | Purpose |
|------|---------|
| `snapshot.py` | `RuntimeADGNode`, `RuntimeADGEdge`, `RuntimeADGSnapshot` — frozen dataclasses, content-addressed |
| `materializer.py` | `RuntimeADGMaterializer.materialize()` — spans → snapshot; parent-child + temporal edges |
| `store.py` | `InMemoryRuntimeADGStore`, `FileBackedRuntimeADGStore` — L4 persistence wrappers |
| `__init__.py` | Public surface + ADG wiring |

### New: `tests/unit/system_learning/runtime_adg/`

| File | Tests |
|------|-------|
| `test_snapshot.py` | 17 tests — frozen dataclasses, content-addressing, order-independence, hashing |
| `test_materializer.py` | 22 tests — node extraction, parent-child edges, temporal edges, mission inference |
| `test_store.py` | 16 tests — persist, idempotency, trace index, file reload, retrieval |
| `test_pipeline.py` | 5 tests (E2E) + 5 API surface tests — tracer→drain→materialize→persist |

### Fixed: `apps_shared/utils/runtime_observability_spans_util.py`
- Was broken: undefined symbols (`TelemetryEvent`, `push_span`, `append_event`, `span_stack`)
- Fix: added imports from `runtime_observability_collectors_util`
- Added 6 canonical constants from `pipeline_constants_config`
- Unblocked 8 previously-skipping tests

---

## Test Evidence

```
tests/unit/system_learning/runtime_adg/           60 passed
tests/unit/apps_shared/utils/                     15 passed (runtime-specific)
tests/unit/agentic_core/adg/extraction/           18 passed
tests/unit/system_learning/types/                  pass (telemetry_types_adg)
tests/unit/system_learning/stores/                 pass (version_store_adg)
TOTAL (combined run):                            157 passed, 0 failed
```

Broader regression run (system_learning + agentic_core ADG):
```
278 passed, 119 skipped (pre-existing optional-dep skips), 0 failed
```

Ruff (I001, F, E on changed files): **All checks passed**

---

## Architecture Coverage

### Static ADG (what the system IS)
- `ADGStaticScanner` — scans structural roots only (excludes `tests/`, `tools/`, `ops_scripts/`, `system_learning/`)
- `_filter_runtime_only_edges` — strips runtime-themed edges from static output
- Boundary enforced: 3 tests in `test_static_scanner.py::TestStaticRuntimeBoundary`

### Runtime ADG (what the system DID)
- `OpenTelemetryTracingAdapter.drain_completed_spans()` — captures all spans with full identity (trace_id, span_id, parent_span_id, layer, component)
- `RuntimeADGMaterializer` — converts spans → immutable `RuntimeADGSnapshot` graph
- `RuntimeADGSnapshot.canonical_bytes()` — deterministic serialisation for content-addressing
- `FileBackedRuntimeADGStore` — persists via existing L4 `FileBackedVersionStore`
- `InMemoryRuntimeADGStore` — test/single-process variant
- Trace index (`_trace_index.json`) — maps trace_id → version_id, survives reload

### System Learning Integration
- `RuntimeADGSnapshot.canonical_bytes()` is consumed by `FileBackedVersionStore.commit_change_package()`
- `FileBackedVersionStore` already emits telemetry and calls `SystemLearningMemoryBridge`
- Runtime snapshots feed system learning automatically through existing L4 seam

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

