---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\static-runtime-adg-boundary-7c2e1a.md'
original_relative_path: 'static-runtime-adg-boundary-7c2e1a.md'
source_sha256: 9a5935a2e6f341c9372fc139fea7cf0311c4c2166ef97cb914f5bc925f5d2929
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Static vs Runtime ADG Boundary and OpenTelemetry Runtime ADG Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Governing Mental Model

`STATIC ADG = what the system is`

`RUNTIME ADG = what the system did`

Operational anchor:

`IF it requires execution to observe -> RUNTIME ADG`

`IF it exists without execution -> STATIC ADG`

## SCOPE_DECLARATION

Files to modify: 4

1. `docs/reports/plans/static-runtime-adg-boundary-7c2e1a.md` — Reason: canonical plan/report artifact for this phase and required evidence carrier.
2. `agentic_core/adg/extraction/static_scanner.py` — Reason: root module where static-vs-runtime scan territory and relation materialization are defined.
3. `tools/generate_full_adg.py` — Reason: canonical ADG generation entrypoint that must request structure-only scanner behavior.
4. `tests/unit/agentic_core/adg/extraction/test_static_scanner.py` — Reason: direct scanner contract test surface for the new boundary behavior.

Baseline: `git diff --name-only HEAD` was clean before the phase started.

## ROLLBACK_CHECKPOINT

Baseline: `39debb0aae35b099a907d43fd422852496e9de6c`

Rollback command: `git reset --hard 39debb0aae35b099a907d43fd422852496e9de6c`

Acceptance criteria:
- `pytest tests/unit/agentic_core/adg/extraction/test_static_scanner.py` passes
- structure-only scanner mode excludes test/runtime/script paths in scoped tests
- structure-only scanner mode filters runtime-only relations while preserving structural imports in scoped tests
- `tools/generate_full_adg.py` explicitly requests structure-only scanning
- scope remains limited to the declared files for this slice

## SCOPE_REVISION_1

Runtime foundation slice — additional files to modify:

1. `apps_shared/utils/open_telemetry_tracing_adapter_util.py` — Reason: existing tracer seam where completed span metadata can be captured without inventing a second tracing adapter.
2. `system_learning/types/telemetry_types.py` — Reason: existing deterministic telemetry type module to extend for runtime span identity and canonical serialization.
3. `tests/unit/apps_shared/utils/test_open_telemetry_tracing_adapter_util.py` — Reason: direct tracer adapter contract and behavior tests for completed-span capture.
4. `tests/unit/system_learning/types/test_telemetry_types_adg.py` — Reason: closest existing telemetry type test surface; extend it with deterministic runtime-slice behavior checks.
5. `tests/unit/system_learning/stores/test_version_store_adg.py` — Reason: direct L4 file-backed persistence seam to verify deterministic runtime slice persistence.
6. `pyproject.toml` — Reason: canonical dependency declaration for the minimal optional OpenTelemetry runtime stack.

Symbols to create or extend in this slice:
- `OpenTelemetryTracingAdapter.drain_completed_spans`
- `TelemetrySlice.canonical_bytes`
- `create_runtime_telemetry_event`
- `create_telemetry_slice_from_runtime_records`

Acceptance criteria for revision 1:
- tracer adapter can emit a deterministic completed-span snapshot from nested spans using a fake tracer in unit tests
- runtime telemetry records can be materialized into a deterministic telemetry slice regardless of input ordering
- telemetry slices persist idempotently through `FileBackedVersionStore`
- no new storage subsystem is introduced

Static ADG remains the AST-derived design-time graph for modules, imports, symbols, static call graph, class hierarchy, config schemas, tool interfaces, and pipeline definitions.

Runtime ADG is built from OpenTelemetry/L6 evidence and persisted through governed L4 artifacts. It owns traces, spans, actual call chains, agent interactions, tool invocations, failures, retries, healing loops, Path A/B/C/D decisions, timing, ordering, and policy outcomes.

## DEPENDENCY_GRAPH

Evidence source:
- `artifacts/adg/provenance_report_03242026_1428.json`
- `artifacts/adg/closure_validation_report_03242026_1428.json`
- `artifacts/adg/layer_coverage_report_03242026_1428.json`

Observed graph facts from the current static ADG artifact:
- modules scanned: `9015`
- symbols scanned: `255221`
- total entities: `264236`
- report nodes: `194613`
- report edges: `942332`
- artifact digest: `5aae68482dd0793bebe9c2b40295f023add2d595762eda93e953e7d448a7cf5d`
- scanner digest: `50d2dedb4868681ea6eae18be0956770ed06c3d914278f9fc2a6ac502270b6c3`

Relevant edge families for this work unit:
- `imports`
- `calls`
- `covers`
- `violates`
- `writes_through`
- `routes_through`
- `records_execution_trace`
- `observes_runtime_state`
- `dispatches_healing_run`
- `validated_by_safety_plane`

Blast radius for the current boundary patch:
- `agentic_core/adg/extraction/static_scanner.py`
- `tools/generate_full_adg.py`
- `tests/unit/agentic_core/adg/extraction/test_static_scanner.py`

No graph database is introduced. Runtime dependency graphs remain derived from OpenTelemetry evidence and persisted through existing L4 file-backed patterns.

## DEDUP_SEARCH

Symbol to create:
- `_selected_scan_roots`
- `_filter_runtime_only_edges`
- `_NON_STRUCTURAL_SCAN_ROOTS`
- `_RUNTIME_ONLY_RELATION_TYPES`

AST search:
- existing nearby helpers found: `_iter_python_files`, `_repo_relative`, `_stamp_semantic_types_with_stats`
- exact helper for canonical-vs-extended scan root selection: `0` matches
- exact helper for runtime-only relation filtering in static scanner output: `0` matches

Name pattern search:
- `include_tests`, `_SCAN_ROOTS`, `_iter_python_files` found as near matches
- no exact `selected_scan_roots` or `filter_runtime_only_edges` symbol found

Behavioral search:
- scan-root control is currently hard-coded in `_SCAN_ROOTS`
- no existing centralized post-scan runtime-relation filter exists
- existing post-processing only stamps semantics and computes metrics

Registry check:
- not found in current scanner exports or obvious SSOT registries

Decision:
- `create`

Justification:
- the scanner currently lacks a single place to enforce the new static/runtime boundary
- adding a minimal root-selector and runtime-edge filter is lower blast radius than rewriting all visitor logic in one pass

## DEDUP_SEARCH_RUNTIME_FOUNDATION

Symbol to create or extend:
- `OpenTelemetryTracingAdapter.drain_completed_spans`
- `TelemetrySlice.canonical_bytes`
- `create_runtime_telemetry_event`
- `create_telemetry_slice_from_runtime_records`

AST search:
- existing nearby seams found: `OpenTelemetryTracingAdapter._create_span`, `get_tracer`, `TelemetrySlice`, `canonical_bytes`, `create_telemetry_slice`, `FileBackedVersionStore.commit_change_package`
- exact runtime span drain API: `0` matches
- exact helper to materialize runtime span records into deterministic telemetry events/slices: `0` matches

Name pattern search:
- `TelemetrySlice`, `TelemetryEvent`, `canonical_bytes`, and `create_telemetry_slice` found as near matches
- no exact `create_runtime_telemetry_event` or `create_telemetry_slice_from_runtime_records` symbol found

Behavioral search:
- the tracer adapter already owns span lifecycle boundaries through `_create_span`
- `TelemetrySlice` already owns deterministic hashing and content-addressed identity
- `FileBackedVersionStore` already persists any package exposing `canonical_bytes`
- no existing runtime artifact carrier exposes both span identity and deterministic persistence

Registry check:
- no competing runtime trace snapshot class or runtime telemetry slice builder found in obvious SSOT modules

Decision:
- `extend existing + create minimal helpers`

Justification:
- extending `TelemetrySlice` preserves a single deterministic telemetry artifact model instead of introducing a parallel runtime snapshot type
- adding `drain_completed_spans` on the existing tracer keeps runtime capture on the canonical tracing seam
- the resulting runtime slice can persist through `FileBackedVersionStore` without a new storage subsystem

## Gap Analysis

### Static ADG contamination gaps

1. Static scan territory is too broad.
   - Current scanner roots include `tests/`, `ops_scripts/`, `system_learning/`, and `tools/`.
   - This violates the structure-only boundary for canonical static ADG generation.

2. Runtime semantics are materialized directly into the static graph.
   - Runtime-labeled relations such as `records_execution_trace`, `observes_runtime_state`, `dispatches_healing_run`, and related telemetry/healing/event edges are present in static scanner output.
   - These relations answer what happened, not just what could happen.

3. The existing OpenTelemetry adapter surface is contaminated by scanner-visible lifecycle emitters.
   - It can be reused later as an integration seam, but not as the source of truth for static ADG semantics.

### Runtime visibility gaps

The current static ADG still cannot provide deterministic answers to:
- which agent actually ran
- which tool was actually invoked
- which healing loop iteration actually executed
- which Path A/B/C/D route was actually chosen
- which policy outcome actually occurred
- what the ordering/timing of real execution was

Those gaps must be closed in Runtime ADG, not by adding more execution semantics to Static ADG.

## Phase 0 Boundary Implementation Slice

1. Make canonical scanner behavior structure-only by default.
   - Default static scan excludes non-structural roots.

2. Preserve opt-in extended scans for legacy analysis utilities.
   - `include_tests=True` continues to expose the broader maintenance/test surface when explicitly requested.

3. Filter runtime-only relations from static scanner output.
   - Keep structural edges such as `imports` and generic `calls`.
   - Remove execution-observed relations from canonical static output.

4. Make canonical ADG generation explicit.
   - `tools/generate_full_adg.py` should instantiate the scanner with structure-only settings.

5. Add boundary tests first.
   - verify default scanner excludes tests/non-structural territory
   - verify explicit opt-in still includes test roots
   - verify runtime-only relations are removed from static output

## Runtime ADG / OpenTelemetry Plan

### Build source of truth

Runtime ADG will be derived from OpenTelemetry spans and events captured in L6.

Required runtime identity fields:
- `root_trace_id`
- `trace_id`
- `span_id`
- `parent_span_id`
- `semantic_clock`
- `replay_key`
- `policy_hash`
- `route_decision`
- `agent_id`
- `tool_name`
- `outcome`

### Persistence model

Runtime snapshots must be persisted via existing L4 governed file-backed patterns.

Primary reuse target:
- `system_learning/stores/version_store.py`

Constraints:
- content-addressable
- deterministic serialization
- replay-safe snapshot reconstruction
- no graph database

### Runtime ADG edge families

These belong in Runtime ADG materialization, not in Static ADG emission:
- actual call chain edges
- agent interaction edges
- tool invocation edges
- healing transition edges
- HITL escalation edges
- policy outcome edges
- replay proof edges
- timing / ordering edges

## Acceptance Criteria

- canonical static ADG excludes non-structural roots by default
- canonical static ADG excludes runtime-only relation types
- generic structural dependencies remain available for blast-radius and governance analysis
- full runtime dependency reconstruction is delegated to OpenTelemetry + L4 persistence
- no graph database is introduced

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

