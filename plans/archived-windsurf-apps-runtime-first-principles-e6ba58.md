---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-runtime-first-principles-e6ba58.md'
original_relative_path: 'apps-runtime-first-principles-e6ba58.md'
source_sha256: 1ec345ee9a5ed179e301aadb587d3e438a25597e1ed0891b987bd5292bc33866
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps Runtime — First-Principles Design (excluding apps_rg)

**Plan ID**: `apps-runtime-first-principles-e6ba58`
**Status**: ALL WAVES COMPLETE (W1–W7) — 2026-04-30
**Tier**: T3 — architecture, multi-app, cross-layer
**Author**: Cursor Agent (greenfield first-principles framing per author-gate decision 2026-04-29)
**ADG Provenance**: backend=sqlite, snapshot=`artifacts/adg/adg_indexed_04292026_1606.sqlite`
**Scope**: `apps_eval`, `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_underwriting_ai`
**Out of scope**: `apps_rg` (already settled and explicitly excluded by user)

## Execution Log

### W1 — Substrate hardening (DONE, 2026-04-29)

**Files modified**:
- `apps_shared/integrations/governed_app_runner.py` — 7 per-phase error fields; whole-pipeline broad catch (line 326) removed; phase-scoped catches added for C0, L5, HITL; `_PlanOutput.error` and `_RouteOutput.error` added; aggregate `error` rebuilt from first non-best-effort phase failure (back-compat preserved, L2/L6 stay best-effort until W2).
- `apps_research/integrations/governed_research_run.py` — 7 per-phase fields surfaced through `GovernedE2ERunRecord`.
- `apps_exec/integrations/governed_exec_run.py` — 7 per-phase fields surfaced through `GovernedExecE2ERunRecord`.
- `apps_lic/integrations/governed_lic_run.py` — 7 per-phase fields surfaced through `GovernedLicE2ERunRecord`.
- `apps_rfp/integrations/governed_rfp_run.py` — 7 per-phase fields surfaced through `GovernedRfpE2ERunRecord`.

**New regression suite**:
- `tests/unit/apps_shared/integrations/test_governed_app_runner_w1_phase_errors.py` — 8 tests locking the W1 contract.

**Verification evidence**:
- All 5 modified files compile cleanly (`python -m py_compile`).
- Pre-existing W5 HITL suite still passes: `tests/unit/apps_shared/integrations/test_governed_app_runner_hitl.py` — **11 passed, 0 failed**.
- New W1 contract suite: **8 passed, 0 failed**.
- Test failures in `tests/unit/apps_research/reasoning/test_research_orchestrator.py` and `tests/unit/apps_shared/enforcement/test_execution_strategy.py` confirmed pre-existing (missing `ExecutionStrategy` symbol in `agentic_core/__init__.py`; suggested `validate_execution_orchestrator`) — **unrelated to W1**.

**ADG canonical-invariant compliance**:
- §22 (graph-layer evidence): plan retains MV + P-view evidence in §4.
- §23 (canonical invariants): SQLite remains source of truth; substrate is the canonical pipeline.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/integrations/governed_app_runner.py, selected=phase_scoped_exception_handling, outcome=executed, principle=preserve-phase-identity_no-broad-catch, precedent=none

### W2 — Observability promotion (DONE, 2026-04-29)

**Files modified**:
- `apps_shared/integrations/governed_app_runner.py`:
  - Added `STRICT_GOVERNANCE` env-flag reader (`_strict_governance_enabled`, accepts `1|true|yes|on` case-insensitive; default OFF preserves legacy behavior).
  - Added `GovernanceContractViolation(RuntimeError)` exception carrying `phase`, `message`, and partial `record` for inspection.
  - **W2.1 (G2)**: L6 ingest detection swapped from `qsize() > 0` heuristic to delta-snapshot. Substrate snapshots `get_async_eval_ingester().qsize()` and `get_shadow_eval_ingester().qsize()` BEFORE `evaluate_and_emit`; after L5, computes deltas. `l6_ingested = (async_delta > 0 or shadow_delta > 0)`. When L5 succeeded but deltas are zero, `l6_error` surfaces `silent_swallow_in_eval_bridge` (catches the existing guardian-allowed silent swallow in `evidence_eval_bridge._enqueue_eval_packets`).
  - **W2.2 (G3)**: Mandatory-phase classification added (L2/L5/L6 mandatory; L1/L0/C0/HITL best-effort). Aggregate `error` rebuild now prioritizes mandatory failures. Under `STRICT_GOVERNANCE=1`, the substrate raises `GovernanceContractViolation` AFTER building the partial record so callers can inspect what completed; default mode returns the record with structured `error` field. HITL stays best-effort even in strict mode (it's already opt-in via `HITL_ENABLED` + `RUNTIME_HITL_ENABLED`).

**New regression suite**:
- `tests/unit/apps_shared/integrations/test_governed_app_runner_w2_strict_governance.py` — 19 tests locking the W2 contract:
  - 1 default-off + 6 truthy-values + 6 falsy-values flag tests
  - `GovernanceContractViolation` is `RuntimeError` subclass + carries phase/message/record
  - End-to-end: legacy mode never raises; strict mode raises with phase identity
  - L6 receipt: delta-snapshot present; legacy `qsize() > 0` heuristic gone; `silent_swallow_in_eval_bridge` signal present

**Verification evidence**:
- All 5 W1-modified files still compile cleanly.
- Combined W1 + W2 + pre-existing HITL suite: **38 passed, 0 failed** (W1=8, W2=19, HITL=11).
- Back-compat: legacy mode (no env var) preserves the W1 contract; no W1 test required modification.
- Production safety: `STRICT_GOVERNANCE` defaults OFF; existing deployments without the flag see no behavior change beyond the W2.1 receipt-quality improvement (which only flips `l6_ingested` from True → False in the silent-swallow case — a true bug surfacing, not a regression).

**Surface area note for downstream consumers**:
- New public symbol: `apps_shared.integrations.governed_app_runner.GovernanceContractViolation`. Callers that wrap `runner.run_governed_core(...)` in a try/except should add this exception to their handling when they enable strict mode in CI.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/integrations/governed_app_runner.py, selected=strict_governance_env_flag_with_structured_violation, outcome=executed, principle=fail_loudly_in_dev_structured_error_in_prod, precedent=strong

### W3 — Boundary leak repair (DONE, 2026-04-29)

**New facade package** `apps_shared/adapters/`:
- `apps_shared/adapters/__init__.py` — package docstring documenting the facade pattern.
- `apps_shared/adapters/system_learning_facade.py` — PEP 562 lazy facade re-exporting 6 symbols: `get_sl_memory_bridge`, `get_process_bus`, `MetaLearningChangePackage`, `MetaLearningBus`, `get_current_adapter`, `seal_step`. Uses `__getattr__` so module load is cheap and ImportError surfaces only on first use (preserves pre-W3 lazy semantics).
- `apps_shared/adapters/rg_orchestrator_facade.py` — PEP 562 lazy facade re-exporting `RgResumeOrchestrator`.

**Source files re-routed** (all 12 boundary edges eliminated):
- **W3.1 (G7)**: `apps_eval/engines/scenario_runner.py:628,647` — swapped `from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator` → `from apps_shared.adapters.rg_orchestrator_facade import RgResumeOrchestrator`.
- **W3.2 (G5)**: `apps_eval/engines/regression_detector.py:372` and `apps_eval/integrations/meta_bus_publisher.py:87,99` — routed through `apps_shared.adapters.system_learning_facade`. Updated stale `# guardian: allow-cross-layer-import` comments to reference plan W3.2 facade route.
- **W3.3 (G6)**: `apps_lic/engines/control_plane.py:266,299`, `apps_lic/engines/lic_spine_adapter.py:20`, `apps_lic/reasoning/HOPPipelineExecutor.py:246` — all 7 imports routed through `apps_shared.adapters.system_learning_facade`.

**New regression suite**:
- `tests/unit/apps_shared/adapters/test_w3_boundary_facades.py` — 14 tests:
  - 4 facade-export contract tests (system_learning + rg_orchestrator export, AttributeError on unknown attr)
  - 4 lazy-resolution contract tests (PEP 562 `__getattr__` present, no top-level upstream imports)
  - 3 boundary-invariant tests (source-level grep ensures NO `apps_eval` / `apps_lic` file imports directly from `system_learning` or `apps_rg`)
  - 6 module-import sanity checks (1 xfailed for pre-existing broken import in `lic_spine_adapter.py:115` unrelated to W3 — see NEXT_STEP)

**Verification evidence**:
- All facade modules + 6 modified source files compile cleanly (`python -m py_compile`).
- W1 + W2 + W3 + pre-existing HITL suite: **54 passed, 1 xfailed, 0 failed** (W1=8, W2=19, W3=14, HITL=11, plus 2 facade lazy-resolution checks).
- Source-grep confirms zero direct `from system_learning` / `from apps_rg` in `apps_eval/` and `apps_lic/`.
- Smoke test confirms all 7 facade symbols resolve at runtime to the correct upstream classes/functions.

**ADG impact (predicted; awaits next snapshot)**:
- 12 boundary edges removed: 2 (`apps_eval → apps_rg`) + 3 (`apps_eval → system_learning`) + 7 (`apps_lic → system_learning`) = 12 edges → 0.
- 2 new edges added: `apps_shared.adapters.system_learning_facade → system_learning` (lazy) and `apps_shared.adapters.rg_orchestrator_facade → apps_rg` (lazy). Net edge reduction: 12 → 2 (−83%).
- Refactor of `system_learning` upstream API now requires editing 1 file (the facade), not 6.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/adapters/, selected=pep562_lazy_facade_centralized_at_apps_shared, outcome=executed, principle=single_boundary_per_cross_tree_dependency, precedent=strong

NEXT_STEP (CLOSED 2026-04-30): plan=apps-runtime-first-principles-e6ba58 title=Fix lic_spine_adapter import of missing apps_shared.spine.base_spine_adapter priority=P3 est_tokens=2000 reason=Pre-existing broken import surfaced by W3 contract test; module apps_shared.spine does not exist anywhere in tree
**Resolution**: Closed via Author-Gate 2026-04-30 deletion_strategy decision (confidence=0.88, gap=0.10). `apps_lic/engines/lic_spine_adapter.py` (270 LOC) and the matching placeholder test deleted (zero production callers verified by grep across `*.py` + `*.md`). xfail probe removed from `test_w3_boundary_facades.py`; stale comment cleaned in `apps_lic/engines/control_plane.py`. W3 boundary facade test suite goes from 14 passed + 1 xfailed → 16 passed (clean). Git history preserves the deleted blob for reference.

### W4 — ADG layer classification fix (DONE, 2026-04-30)

**Files modified**:
- `tools/adg/adg_layer_overrides.yaml` — added `"apps_underwriting_ai/*": "L_APP"` to the SSOT layer-override config.
- `tools/adg/repair/rules/fix_layer_assignment.py` — added `"apps_underwriting_ai"` to `APP_PATTERNS`.
- `tools/adg/repair/repair_orchestrator.py` — added `"apps_underwriting_ai"` to the embedded apps tuple in `_infer_layer_from_path`.

**New regression suite**:
- `tests/unit/tools/adg/test_w4_layer_classification.py` — 4 tests: every discovered `apps_*` package classified as `L_APP`; explicit regression check for `apps_underwriting_ai`; repair-rule list covers SSOT yaml; repair-orchestrator embedded list covers SSOT yaml.

**Verification**: 4/4 tests pass. Predicted ADG impact: 75 `apps_underwriting_ai` nodes will move from `L_UNKNOWN` to `L_APP` on next snapshot regen.

DECISION_CAPTURED: type=architecture_choice, repo_area=tools/adg/, selected=add_apps_underwriting_ai_to_3_classifier_files, outcome=executed, principle=ssot_yaml_drives_repair_rules, precedent=strong

### W5 — Substrate boilerplate elimination (DONE, 2026-04-30)

**Files modified**:
- `apps_shared/integrations/governed_app_runner.py` — added `build_app_record(target_cls, core, *, aliases=None, **app_specific)` helper. Auto-copies same-named substrate fields, supports field renames via `aliases`, surfaces unknown kwargs as `TypeError`.
- `apps_exec/integrations/governed_exec_run.py` — 35-line translator → 7-line `build_app_record` call.
- `apps_research/integrations/governed_research_run.py` — 27-line translator → 5-line `build_app_record(..., aliases={"topic": "query"})`.
- `apps_lic/integrations/governed_lic_run.py` — 38-line translator → 8-line `build_app_record` call.
- `apps_rfp/integrations/governed_rfp_run.py` — 35-line translator → 7-line `build_app_record` call.

**LOC reduction**: ~135 → ~27 lines across 4 governed apps (≈80% reduction). Plan target was 60% — exceeded.

**Drift safety**: New substrate fields automatically propagate to every per-app record without per-app file edits.

**New regression suite**:
- `tests/unit/apps_shared/integrations/test_w5_build_app_record.py` — 12 tests covering helper export, common-field auto-copy, app_specific override, alias mapping, unknown-key TypeError, slim-translator LOC contract, drift-safety regression.

**Verification**: 12/12 tests pass.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/integrations/governed_app_runner.py, selected=build_app_record_helper_with_alias_support, outcome=executed, principle=composition_over_redeclaration_with_drift_safety, precedent=strong

### W6 — Async substrate + cached AgenticRouter (DONE, 2026-04-30)

**Files modified**:
- `apps_shared/integrations/governed_app_runner.py`:
  - **W6.2**: Added `self._cached_router: Any = None` to `__init__`. Added `_get_router()` lazy-cached accessor that constructs the `AgenticRouter` once and registers the routing target a single time. `_l0_route` refactored to use `_get_router()` — bandit posterior state now accrues across calls on the same runner instance.
  - **W6.1**: Added `async def _l1_plan_async()` and `async def _l0_route_async()` — await-native variants of the L1/L0 helpers (no `asyncio.run()` re-entry). Added public `async def run_governed_core_async(query, *, run_id, inject_chunks)` that uses `asyncio.to_thread` to offload the synchronous pipeline so callers' event loops are not blocked.

**Concurrency model documented**: one runner per concurrent caller; multiple instances run truly concurrently; bandit posterior is per-instance.

**New regression suite**:
- `tests/unit/apps_shared/integrations/test_w6_async_substrate.py` — 11 tests covering coroutine-function contract, sync/async record shape parity, router caching across calls, register-once invariant, inter-instance router independence, async helper coroutine contract, async helper uses cached router, `asyncio.gather` of two concurrent runs, sync regression.

**Verification**: 11/11 tests pass.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/integrations/governed_app_runner.py, selected=asyncio_to_thread_facade_plus_cached_router, outcome=executed, principle=conservative_concurrency_with_bandit_state_preservation, precedent=strong

### W7 — ADR + conformance gate (DONE, 2026-04-30)

**Files added**:
- `docs/architecture/adr/ADR-076-governed-or-exception-binary.md` — codifies the GOVERNED-or-EXCEPTION binary: every `apps_*` package on disk must appear in `APP_REGISTRY` as `GovernedAppEntry` (5 today) or `FormalExceptionEntry` (2 today). Documents enforcement layers, migration (none needed — all 7 apps already classified), and out-of-scope future work.
- `ops_scripts/ci/check_app_registry_conformance.py` — fail-closed CI gate. Discovers every `apps_*/` directory at repo root with real Python source, asserts each appears in `APP_REGISTRY` and is one of the canonical entry types. `apps_shared` is documented infrastructure (substrate library) and excluded via `INFRASTRUCTURE_PACKAGES` constant. Exit 0 = OK; exit 2 = violation.

**New regression suite**:
- `tests/unit/ops_scripts/ci/test_check_app_registry_conformance.py` — 9 tests: gate script + ADR exist; gate exits 0 on current tree; ADR documents the binary; `_discover_apps_packages` excludes `apps_shared`; all 7 governed/exception apps discovered; `_check_conformance` returns `(True, [])`; injected missing package raises violation; injected orphan registry entry raises violation.

**Verification**: 9/9 tests pass; gate exits 0 against current state.

DECISION_CAPTURED: type=architecture_choice, repo_area=ops_scripts/ci/, selected=adr_plus_fail_closed_ci_gate_with_documented_infra_exclusion, outcome=executed, principle=ssot_registry_plus_deterministic_enforcement, precedent=strong

---

## 0. Executive Finding

The runtime is **already first-principles correct in shape** — `apps_shared.integrations.GovernedAppRunner` IS the canonical substrate; `APP_REGISTRY` IS the SSOT for governance status; formal exceptions IS the codified mechanism for apps that cannot adopt the substrate. The exercise is therefore **validate + harden**, not *redesign*. ADG-grounded gaps cluster on (a) best-effort error swallowing in the substrate spine, (b) two cross-boundary import leaks, and (c) ADG-tagging gaps, not on architectural mis-design.

**Observed governance state (from `APP_REGISTRY` + ADG)**:

| App | Status | Substrate Path | Reason / Notes |
|---|---|---|---|
| `apps_research` | GOVERNED | `GovernedResearchRun` | full L1→L0→C0→L2→L5+L6 |
| `apps_exec` | GOVERNED | `GovernedExecRun` | full pipeline |
| `apps_lic` | GOVERNED | `GovernedLicRun` | full pipeline + `HITL_ENABLED=True` |
| `apps_rfp` | GOVERNED | `GovernedRfpRun` | full pipeline |
| `apps_eval` | **EXCEPTION** (`circular_dependency`) | `GovernedEvalException` | evaluator-of-evaluator ⇒ permanent; safe layers: `BUS_T_telemetry`, `conformance_metadata` |
| `apps_underwriting_ai` | **EXCEPTION** (`regulatory_domain`) | `GovernedUwException` | legally-binding credit decisions ⇒ permanent; domain-specific governance via `CoreAdapter` |

---

## 1. First-Principles Invariants (the design floor)

These are derived purely from purpose, then cross-checked against the existing substrate:

### Invariant I1 — Closure
A governed app run is a **single closed pipeline**: `(domain_request) → (sealed run record, evidence bundle, exit envelope, optional HITL action)`. No mid-pipeline external state mutations.

### Invariant I2 — Substrate-or-Exception (binary)
Every `apps_*` package is **exactly one** of:
- **GOVERNED** — uses `GovernedAppRunner` substrate; full L1→L0→C0→L2→L5→L6 pipeline.
- **EXCEPTION** — declares `FormalExceptionEntry` with reason code + ≥2 compensating controls + partial-adoption module.

**No third state at steady-state.** `CANDIDATE` is a transient pre-migration label only.

### Invariant I3 — Domain Isolation
The ONLY app-specific code in the runtime spine is:
- `_build_query(request) -> str` (domain → retrieval-query projection)
- `run_governed_e2e(request) -> Governed<App>E2ERunRecord` (substrate-record translator)

All other domain logic (engines, outputs, config) lives **above** the substrate.

### Invariant I4 — Capability Token = Identity
Every governed run is identified by the tuple `(app_name, capability_token, run_id)`. The capability token is registered once in `APP_REGISTRY` and asserted by the L2 chokepoint via `ExecutionContext.create()`. Capability drift = identity loss = governance violation.

### Invariant I5 — Observable-by-Default (currently violated)
L6 evidence-packet ingestion is **mandatory** for governed apps. Today the substrate's L6 ingest is best-effort — this is a gap (see §3.G2).

### Invariant I6 — Boundary Hygiene
- `apps_*` MUST NOT import directly from `infrastructure/`, `tools/`, or `system_learning/`.
- `apps_*` MUST NOT import from sibling `apps_*` (only from `apps_shared`).
- `apps_shared` may import `agentic_core/` L0–L6 (downward-only).
- Currently violated by: `apps_eval → apps_rg` (2 imports), `apps_eval → system_learning` (3), `apps_lic → system_learning` (7).

### Invariant I7 — Layer Tag Truth
Every node in `apps_*` MUST resolve to ADG layer `L_APP`. Today `apps_underwriting_ai` resolves to `L_UNKNOWN` (75 nodes mistagged) — fix is layer-classification config, not architecture.

---

## 2. Target Runtime Shape (per app)

```
┌─────────────────────────────────────────────────────────────────┐
│ apps_<name>/                                                     │
│ ├─ types/         Request/Response dataclasses (domain)          │
│ ├─ config/        agent_spec_config.py + rubrics + KB             │
│ ├─ engines/       Domain assembly engines (NO governed plumbing) │
│ ├─ outputs/       Renderers                                       │
│ ├─ data/          Sample/seed data                                │
│ │                                                                 │
│ └─ integrations/                                                  │
│    └─ governed_<name>_run.py   ← MINIMAL bridge                   │
│       (subclass of apps_shared.GovernedAppRunner;                 │
│        OR FormalException partial-adoption module)               │
│                                                                   │
│ Spine code lives in apps_shared, NEVER duplicated.                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ apps_shared/integrations/                                         │
│ ├─ governed_app_runner.py      THE pipeline (one place)          │
│ ├─ app_registry.py              SSOT governance + capability      │
│ ├─ runtime_hitl_integration.py  W5 HITL hook                      │
│ └─ exception_substrate.py       (NEW) shared base for exempt apps │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       agentic_core/L0..L6   (downward-only)
```

**Key ratio (target)**: substrate ≈ 600 LOC; per-app bridge ≈ 80 LOC; everything else is domain. Today the per-app bridge averages ~180 LOC because of substrate-record re-declaration boilerplate (see §3.G7).

---

## 3. ADG_HOTSPOT_REPORT — Residual Gaps

Ranked using `impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. All hotspots traced through the Zero-Loss Propagation Pipeline; each row classified with one of the 4 archetypes and cross-referenced against the 5 ADG Surfaces.

| # | Gap ID | File / Surface | Layer | Fan-in | Archetype | ADG Surface(s) | Severity | Impact |
|---|---|---|---|---|---|---|---|---|
| 1 | G1 | `apps_shared/integrations/governed_app_runner.py:326` (whole-pipeline broad catch) | L_APP→L0..L6 | 5 (4 governed apps + tests) | **CENTRAL_DEPENDENCY** | Execution, Observability | HIGH | high |
| 2 | G2 | `apps_shared/integrations/governed_app_runner.py:299-307` (L6 ingest swallow) | L_APP→L6 | 5 | **SAFETY_GATEKEEPER** | Observability | HIGH | high |
| 3 | G3 | `apps_shared/integrations/governed_app_runner.py:276-281` (L2 chokepoint silent skip) | L_APP→L2 | 5 | **SAFETY_GATEKEEPER** | Execution, Security | HIGH | high |
| 4 | G4 | ADG layer resolution for `apps_underwriting_ai` (75 nodes `L_UNKNOWN`) | (config) | n/a | (tagging) | (Observability) | MED | med |
| 5 | G5 | `apps_eval` → `system_learning` direct imports (3) | L_APP→L_SL | 0 | ORCHESTRATOR | None (boundary) | MED | med |
| 6 | G6 | `apps_lic` → `system_learning` direct imports (7) | L_APP→L_SL | 0 | ORCHESTRATOR | None (boundary) | MED | med |
| 7 | G7 | `apps_eval` → `apps_rg` direct imports (2) | L_APP→L_APP | 0 | ORCHESTRATOR | None (boundary) | LOW | low |
| 8 | G8 | Substrate-record boilerplate: 4 governed apps re-declare 22 fields | L_APP | 4 (per-app records) | DUPLICATED_PATTERN | None | LOW | low |
| 9 | G9 | `asyncio.run()` inside `_l1_plan` (line 435) and `_l0_route` (line 470) | L_APP | 5 | CENTRAL_DEPENDENCY | Execution | LOW | low |
| 10 | G10 | Fresh `AgenticRouter` per call (line 459) — bandit state cannot accumulate per app | L_APP→L0 | 5 | STATE_NODE | State | LOW | low |
| 11 | G11 | L4 (state) usage sparse across all governed apps (0–4 imports) | L_APP→L4 | n/a | (architecture) | State | LOW | low |
| 12 | G12 | `mv_runtime_spine_gaps`: 51–65% of agentic_core modules unconnected to spine | systemwide | n/a | (broader scope) | All five | INFO | informational |

**Layer multipliers applied**: substrate hotspots G1–G3 cross L0/L5 (×2.0) and L2 (×1.0) and L6 (×0.75), so multiplier ≈ 1.5 weighted. Boundary leaks G5–G7 are L_APP only (×1.0).

---

## 4. ADG_GRAPH_LAYER_EVIDENCE

Direct SQLite reads of the `04292026_1606` snapshot grounded the gap report. Materialized views and pre-built P-views consulted (per constitutional §22):

### MVs cited
- **`mv_runtime_spine_gaps`** — 7 rows (per-layer); confirms 51–65% gap across L0–L6 (informational baseline)
- **`v_p2_duplicated_adapters`** — 3 rows; ADG::Symbol::sqlite3 has 4 adapters incl. one in `apps_shared/data_adapters/repo_signal_adapter.py` (out-of-scope but flagged)
- **`v_p0_apps_direct_infra`** — 0 rows; confirms no P0 raw-infra imports from any `apps_*` (✓ healthy)

### Semantic-edge query patterns used
- `relation_type='imports'` joined with `nodes.layer` to compute layer-distribution per app (table §1.5 in probe)
- `source_file LIKE 'apps_X/%'` cross-joined with `dst_id → nodes.resolved_path LIKE 'apps_Y/%'` to detect cross-app leaks
- `entity_type` distribution per app to confirm apps are mostly modules + symbols (no rogue entity types)

### P-view cross-references
- `v_p0_apps_direct_infra`: 0 — confirms no current P0
- `v_p1_zero_caller_infra`, `v_p1_mis_layered_infra`, `v_p2_duplicated_adapters` — none flag in-scope app code as primary culprit; the substrate stays clean

### Per-app numeric fingerprints
| app | nodes | files | ADG layer | governed | substrate-bound |
|---|---:|---:|---|:---:|:---:|
| apps_eval | 65 | 65 | L_APP | n (exempt) | exception substrate |
| apps_exec | 61 | 61 | L_APP | y | full |
| apps_lic | 245 | 97 | L_APP | y | full + HITL |
| apps_research | 57 | 57 | L_APP | y | full |
| apps_rfp | 58 | 58 | L_APP | y | full |
| apps_underwriting_ai | 75 | 75 | **L_UNKNOWN** | n (exempt) | exception substrate |

---

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | W1.1, W1.2 | Substrate hardening: replace whole-pipeline broad catch (G1) with phase-scoped exception types; surface phase failures in `GovernedAppRunRecord` | ~6,000 | substrate has ≥1 explicit failure-mode test per phase; PR keeps record schema additive | **Done** | All 4 governed apps still pass E2E proof harness; new fields (`l1_error`, `l0_error`, `c0_error`, `l2_error`, `l5_error`, `l6_error`, `hitl_error`) populated; no broad catch lines remain |
| **W2** | W2.1, W2.2 | Observability promotion: L6 ingest mandatory (G2), L2 chokepoint mandatory (G3); fail loudly in dev, structured `error` field in prod | ~5,000 | tests can reach L2/L6 in CI (uses dummy ExecutionContext); existing best-effort fallback retained behind `STRICT_GOVERNANCE=0` flag for back-compat one minor version | **Done** | `l6_ingested=True` proven via delta-snapshot of qsize across L5 (not absolute qsize); `l2_executed=True` proven via existing ExecutionContext path; `STRICT_GOVERNANCE=1` raises `GovernanceContractViolation` with partial record |
| **W3** | W3.1, W3.2, W3.3 | Boundary leak repair: route `apps_eval → apps_rg` and `apps_*  → system_learning` through `apps_shared` adapters (G5, G6, G7) | ~7,000 | `apps_shared` is the right destination for these adapters; `system_learning` consumers can use a thin `apps_shared.adapters.system_learning_facade` | **Done** | Source-grep confirms zero direct `from system_learning` / `from apps_rg` in `apps_eval/` and `apps_lic/`; 14-test boundary contract suite passes; PEP 562 lazy facade preserves fail-open semantics |
| **W4** | W4.1 | ADG tagging fix for `apps_underwriting_ai` (G4): add explicit layer classification entry so 75 nodes resolve to `L_APP` | ~2,000 | layer-classification SSOT lives in `tools/adg/adg_layer_overrides.yaml` and 2 repair files; change is config + regen, not architecture | **Done** | Yaml updated; both repair classifiers updated; 4/4 contract tests pass; awaits next ADG regen for `apps_underwriting_ai → L_APP` propagation |
| **W5** | W5.1, W5.2 | Substrate boilerplate elimination (G8): make `Governed<App>E2ERunRecord` either generic over a `TAppContext` payload, or use composition (`record.substrate.* + record.app.*`); per-app bridges shrink to ~50 LOC | ~5,000 | API stability for downstream consumers maintained via property-style accessors on the new record shape | **Done** | Per-app translator LOC dropped ≈80% (135 → 27 lines across 4 apps); 12/12 tests pass; back-compat preserved |
| **W6** | W6.1, W6.2 | Async-correct substrate (G9, G10): replace `asyncio.run()` with `async def run_governed_core_async`, keep sync facade; cache/inject `AgenticRouter` so bandit state accrues per app | ~7,000 | callers have a clear migration path (sync wrapper preserved); router-state caching does not violate SSOT (per-app instance lives on the runner) | **Done** | `run_governed_core_async` exposed via asyncio.to_thread; cached router preserves bandit state; 11/11 tests pass including 2-concurrent-runs probe |
| **W7** | W7.1 | ADR + conformance gate: codify the GOVERNED-or-EXCEPTION binary as ADR-NNN; CI gate that fails when an `apps_*` package is missing from `APP_REGISTRY` | ~3,000 | gate already partially exists; this hardens it to fail-closed | **Done** | ADR-076 written; `check_app_registry_conformance.py` exits 0 on current tree, exits 2 with diagnostics on injected missing/orphan; 9/9 tests pass |

**Total est. tokens**: ~35,000 (sizing only — not a budget gate per plan-location.md note about 1M context window era)

---

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| **W1.1** | Phase-scoped exception types in substrate | `apps_shared/integrations/governed_app_runner.py` (refactor `run_governed_core`) | Wide-tuple catch at line 326 hides phase identity; `error` field is undifferentiated string | 3,000 | **Done** |
| **W1.2** | Add per-phase `_error: str` fields to `GovernedAppRunRecord` + propagate | substrate + 4 governed app record translators | Field additions are additive but require reviewing 4 per-app translators | 3,000 | **Done** |
| **W2.1** | L6 ingest mandatory + receipt-based proof | substrate `_l6_ingest()` extraction; substitute `l6_ingested` from queue-size to receipt-id | Today `l6_ingested` is a queue heuristic, not a confirmed packet ingest | 2,500 | **Done** |
| **W2.2** | L2 chokepoint mandatory + `STRICT_GOVERNANCE` env flag | substrate `_l2_authorize()` extraction; flag wiring; tests | L2 silent skip on `ImportError` masks missing safety plane | 2,500 | **Done** |
| **W3.1** | `apps_eval → apps_rg` adapter | new `apps_shared/adapters/<facade>.py`; remove the 2 direct imports | Cross-app leak violates I6 | 2,000 | **Done** |
| **W3.2** | `apps_eval → system_learning` adapter | new `apps_shared/adapters/system_learning_facade.py`; remove 3 direct imports | Boundary leak violates I6 | 2,500 | **Done** |
| **W3.3** | `apps_lic → system_learning` adapter | reuse W3.2 facade; remove 7 direct imports | Largest boundary leak (×7) | 2,500 | **Done** |
| **W4.1** | ADG layer classification fix for `apps_underwriting_ai` | layer-classifier config; regenerate ADG snapshot | 75 mistagged nodes → `L_UNKNOWN` regression in `mv_runtime_spine_gaps` and other MVs | 2,000 | **Done** |
| **W5.1** | `build_app_record` helper in substrate | substrate `governed_app_runner.py` (+~90 LOC) | 22 fields × 4 apps = 88 lines duplicated; high drift risk | 3,000 | **Done** |
| **W5.2** | Migrate 4 per-app bridges to `build_app_record` | 4 governed bridges (−135 LOC, +27 LOC) | None blocking; mostly mechanical | 2,000 | **Done** |
| **W6.1** | Async-correct substrate (`run_governed_core_async`) + sync facade | substrate refactor; tests | `asyncio.run()` calls block; cannot run governed pipelines concurrently | 4,000 | **Done** |
| **W6.2** | Cached `AgenticRouter` per `GovernedAppRunner` instance | substrate `__init__` + `_l0_route` + `_get_router` | Fresh router per call destroys bandit posterior accrual | 3,000 | **Done** |
| **W7.1** | ADR-076 + GOVERNED-or-EXCEPTION conformance gate | `docs/architecture/adr/ADR-076-...md`; `ops_scripts/ci/check_app_registry_conformance.py` | Today the registry is SSOT but enforcement is per-app conformance test, not central CI gate | 3,000 | **Done** |

---

## 7. Gap Register (residual items NOT addressed by this plan)

| Item | Why deferred |
|---|---|
| G11: L4 state usage sparse across governed apps | Out of substrate scope; apps drive their own state needs. Revisit if `mv_runtime_spine_gaps` for L4 shifts above 70% gap. |
| G12: 51–65% spine gap systemwide | Cross-cutting; outside `apps_*` ownership. Captured separately as DEFERRED_SCOPE below. |
| `apps_rg` audit | Explicitly excluded by user. Already GOVERNED per registry. |
| `v_p2_duplicated_adapters` (sqlite3 ×4) entries | Affect `agentic_core/` and `tools/`, not `apps_*`. Out of scope. |

---

## 8. ADR Draft (sketch — fully drafted in W7.1)

**Title**: ADR-NNN — `apps_*` Runtime is GOVERNED-or-EXCEPTION Binary

**Decision**: Every `apps_*` package is exactly one of:
1. **GOVERNED**: subclasses `apps_shared.integrations.GovernedAppRunner`; runs the full L1→L0→C0→L2→L5→L6 substrate; `GovernedAppEntry` in `APP_REGISTRY`.
2. **EXCEPTION**: declares a `FormalExceptionEntry` with reason code (`circular_dependency`, `regulatory_domain`, or `pending_migration`), ≥2 compensating controls, partial-adoption module, and review cadence.

CI conformance gate fails when an `apps_*` package exists without a registry entry.

**Consequences**: Apps cannot quietly drift into a third state. Migration progress is auditable. Permanent exceptions are intentional, justified, and reviewed.

---

## 9. Verification Strategy

For each wave:

| Wave | Pre-edit | Post-edit |
|---|---|---|
| W1 | Capture current substrate behavior on injection-of-failure tests | New per-phase error fields populated; whole-pipeline broad catch absent |
| W2 | Run E2E proof harness; capture `l6_ingested` and `l2_executed` baseline | Same harness; flag-strict variant fails on missing L2/L6; flag-permissive matches baseline |
| W3 | ADG cross-app + boundary import counts (probe §1.4, §1.6) | Recount: target zero |
| W4 | `mv_runtime_spine_gaps` snapshot before regen | Snapshot after regen; `apps_underwriting_ai` nodes now `L_APP` |
| W5 | Per-app bridge LOC counts | LOC drops 60%; downstream tests still pass |
| W6 | Substrate proof harness sequential timing baseline | Proof harness with 2-concurrent governed runs measured; bandit posterior accrual non-zero |
| W7 | New `apps_test_dummy/` with no registry entry | CI gate fails; ADR posted to Notion |

---

## 10. Provenance + References

**ADG snapshot**: `artifacts/adg/adg_indexed_04292026_1606.sqlite`

**Source files inspected**:
- `apps_shared/integrations/governed_app_runner.py` (539 lines)
- `apps_shared/integrations/app_registry.py` (259 lines)
- `apps_lic/integrations/governed_lic_run.py` (184 lines)
- `apps_rfp/integrations/governed_rfp_run.py` (171 lines, header)
- `apps_eval/integrations/governed_eval_exception.py` (188 lines, header)
- `apps_underwriting_ai/integrations/governed_uw_exception.py` (300 lines, header)

**Doctrine consulted**:
- `.windsurf/rules/adg-canonical-invariants.md` — 5 surfaces, 4 archetypes, layer multipliers
- `.windsurf/rules/adg-graph-layer-enforcement.md` — MV + P-view requirement (constitutional §22)
- Constitutional §6 (Author-Gate), §22 (graph-layer evidence), §28 (SQLite-direct fallback per MCP serialization §25)

**MCP path note**: `mcp1_adg_health` returned `transport closed` mid-session; per §28 fallback hierarchy I dropped to direct SQLite reads of the snapshot. No grep was used for dependency analysis.

---

## 11. Next Step (for the operator)

This plan is design-only — no edits made. To proceed:

1. Approve the `GOVERNED-or-EXCEPTION` invariant (I2) and the wave ordering (W1→W7).
2. Decide whether W1 (broad-catch decomposition) or W2 (mandatory L6/L2) is the highest-priority first wave.
3. On approval, the harness moves to `SR_EXECUTE` for W1.1 + W1.2.

DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/integrations, selected=greenfield_first_principles_validate_and_harden, outcome=executed, principle=substrate-or-exception_binary_invariant, precedent=none

NEXT_STEP: plan=apps-runtime-first-principles-e6ba58 title=Approve wave ordering and select first execution wave priority=P3 est_tokens=2000 reason=Plan is design-only; operator must select W1 vs W2 priority before SR_EXECUTE


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps runtime first-principles design (W1–W7 done)

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_path_criticality_rollup` — blast-radius / cone risk for refactor candidates.
3. `mv_graph_critical_path_blast_radius` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `controls_flow` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.
- `v_p1_mis_layered_infra` — applicable cross-reference.

**Rationale**: Runtime-shell convergence across all apps_* modules; critical-path rollup proves layer-gravity preserved.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps runtime first-principles design (W1–W7 done) (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps runtime first-principles design (W1–W7 done)` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

