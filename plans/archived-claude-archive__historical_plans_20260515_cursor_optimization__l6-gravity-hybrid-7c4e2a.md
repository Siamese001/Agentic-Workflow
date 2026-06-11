---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\l6-gravity-hybrid-7c4e2a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\l6-gravity-hybrid-7c4e2a.md'
source_sha256: ba2781bb68f95de5961ec6b6f9640bf6df4ba47801914cab25d5ad4f27df551a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L6 Cross-Layer Gravity — Hybrid Pragmatic Burndown (Option 1)

Status: **PARTIAL EXECUTION — W1.P1 + W2.P2 DONE 2026-05-01** · Tier: **T2** (execution spans 4 waves, ~22k tok)
Date: 2026-05-01

## Execution Log

### 2026-05-01 — W1.P1 ✅ + W1.P2 ❌ blocked + W2.P2 ✅ pivot

**W1.P1 DONE**: Created `agentic_core/_shared/__init__.py` + `agentic_core/_shared/types/__init__.py` (neutral-layer namespace). Extended `tools/generate/generate_static_adg.py::_infer_layer` at line 247 to classify `agentic_core/_shared/` as `L_SHARED` (next ADG regen will honor this).

**W1.P2 BLOCKED (plan defect — documented as Author-Gate pivot)**: All 4 candidate Category A files (`determinism_types.py`, `path_constants.py`, `human_decision_artifact_types.py`, `mutation_prohibition.py`) fail the `_shared/` inclusion criteria. They are *instrumented envelopes* — each has module-load side effects (`record_execution_trace(...)`, `emit_replay_key(...)`) and imports 30+ emission helpers from `agentic_core.runtime.contracts.lifecycle_trace_contract`. Moving them pure would break trace emission; dragging the trace contract into `_shared/` would pollute the neutral layer. Author-Gate 2026-05-01 pivoted W1.P2 → deferred; executed W2 directly instead.

**W2.P2 DONE (pivot target)**: Moved `agentic_core/L6_observability/utils/integrity_report_generator_util.py` → `ops_scripts/reports/integrity_report_generator_util.py`. Verified preconditions: ADG fan-in = 0 (no consumers to migrate), no mirror test exists, no CLI references, file has `if __name__ == "__main__":` (standalone script pattern consistent with `ops_scripts/reports/apps_rg_layer_audit.py`). AST parse clean post-move. Expected effect on next ADG regen: -9 L6→lower edges (top offender eliminated; total drops 39 → ≤30). Write-sovereignty violation `write_162611` (Non-UWG write path at line 572) also auto-resolves because ops_scripts/ is classified as L_OPS and L_OPS→direct_write is permitted.

**Remaining work**: W2.P1/P3/P4 (adjacent reporter migration + architectural_exceptions.yaml + ADR-081 + ADG regen verification). Plus optional revival of W1.P2 via surgical type-subsection extraction if the 39→≤24 goal demands it.

Scope doc: `docs/reference/_primers/AST Dependency Graphs (ADG)/ADG Mental Model.md` §Layer Gravity
Parent Notion row: `[P1] 2_authority_boundary P0 17 cross-layer authority breaches` (`35027693-f55c-81e3-80e2-e7f0a390f031`) — In Progress → will be Done when this plan ships

## Intent

Reduce 39 L6→lower-layer imports (ADG snapshot `adg_indexed_05012026_0632.sqlite`) by ~50% via pragmatic hybrid:
- Extract Category A (types/path_constants) to a neutral layer
- Move top offender `integrity_report_generator_util.py` + adjacent L6 "reporters" to `L_OPS/`
- Document Categories B + C as accepted architectural exceptions with rationale

## Author-Gate Evidence (2026-05-01)

- **Options scored**: 1=0.89 (hybrid), 2=0.72 (types only), 3=0.78 (full refactor), 4=0.60 (accept all)
- **Selection**: Option 1 — dominance by ≥0.11 over nearest alternative
- **Rationale**: addresses ~50% of violations in single focused T2; keeps risky/expensive categories B+C out of scope; produces deterministic ADR

## TL;DR — Verdict

Zero `mv_authority_boundary_breaches` (17 dead re-exports eliminated in commit `079958b47d` 2026-04-30). The remaining 39 L6→lower imports are real semantic deps. Three categories; this plan addresses two cleanly and ADRs the third.

## Category Breakdown

| Cat | Count | Files/Targets | This Plan |
|---|---:|---|---|
| **A — Types/constants** | ~10 | `L0_routing/types/determinism_types.py` (3), `L0_routing/config/path_constants.py` (3), `L3_orchestration/types/human_decision_artifact_types.py` (2), `L0_routing/enforcement/mutation_prohibition.py` (2) | **W1: Extract to `agentic_core/_shared/`** |
| **B — L5 enforcement calls** | 6 | `three_tier_compliance_enforcer.py` (2), `ssot_structure_validation_enforcer.py` (2), `registry_verification_enforcer.py` (2) | **W3: Accept as documented exception** |
| **C — L2 infrastructure** | 21 | `L2_execution/utils/providers.py` (11), `audit/telemetry_bus.py` (4), `utils/write_gateway.py` (3), `utils/execution_proof_emitter.py` (2), `types/sealed_l2_artifact.py` (1) | **W2 (partial): Move top offender `integrity_report_generator_util.py` (9) + adjacent reporters to `L_OPS/`; W3: remaining ~12 accepted as exception** |

Top offender file: `agentic_core/L6_observability/utils/integrity_report_generator_util.py` (9 imports alone — 23% of total).

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.P1, W1.P2 | Extract Category A types/path_constants to `agentic_core/_shared/` | ~8k 🟢 | No cross-app consumers break on moved imports | 📋 Draft | Category A count drops from ~10 to 0; existing tests pass |
| W2 | W2.P1, W2.P2 | Move `integrity_report_generator_util.py` + 2 adjacent L6 "reporter" files to `L_OPS/` | ~8k 🟡 | Files are true ops-class (report generation), not core observability | 📋 Draft | ≥9 L6→L2 imports migrate to L_OPS→L2 (still valid direction); top offender file empty or moved |
| W3 | W3.P1 | Document Categories B (6) + remaining C (~12) in `config/architectural_exceptions.yaml` with per-edge-class rationale | ~3k 🟢 | Existing exceptions.yaml accepts the shape | 📋 Draft | All residual L6→lower edges either eliminated OR documented; `mv_authority_boundary_breaches` stays at 0 |
| W4 | W4.P1, W4.P2 | Author ADR-081 "L6 Observability Dependency Hygiene"; regenerate ADG; verify violation count drop | ~3k 🟢 | ADR registry writable; `tools/generate_full_adg.py` healthy | 📋 Draft | ADR filed in Notion ADR Registry; fresh ADG shows ≤20 L6→lower edges; Notion row #1 flipped to Done |

Total span: ~22k tokens across 4 waves.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.P1 | Create `agentic_core/_shared/types/` neutral layer | `agentic_core/_shared/__init__.py` (new), `agentic_core/_shared/types/__init__.py` (new) | Neutral layer must not import from L0-L6 at all | 2k | 📋 Draft |
| W1.P2 | Move 4 type modules to `_shared/types/`; update imports repo-wide | `determinism_types.py`, `path_constants.py`, `human_decision_artifact_types.py`, `mutation_prohibition.py` (moved) + back-compat shims at old paths for 90-day deprecation | Back-compat shim pattern per constitutional §3 | 6k | 📋 Draft |
| W2.P1 | Create `L_OPS/integrity_reports/` layer | `L_OPS/__init__.py` (new), `L_OPS/integrity_reports/__init__.py` (new), `docs/architecture/adr/ADR-081-l6-observability-dependency-hygiene.md` (draft) | Confirm L_OPS layer name + path convention matches existing L_TOOLS / L_APP precedent | 2k | 📋 Draft |
| W2.P2 | Move `integrity_report_generator_util.py` + adjacent reporter files; update consumer imports | `integrity_report_generator_util.py` → `L_OPS/integrity_reports/` + 2 adjacent utility files (to be identified via ADG fan-in scan) | Risk: any consumer inside `agentic_core/L6_observability/` must migrate OR import via shim | 6k | 📋 Draft |
| W3.P1 | Extend `config/architectural_exceptions.yaml` with L6 exception set | `config/architectural_exceptions.yaml` (edit — add `l6_downstream_exceptions` section with 3 subgroups: safety_enforcement_callers, execution_providers_consumers, telemetry_bus_subscribers) | Must match existing schema in architectural_exceptions.yaml (inspect before edit) | 3k | 📋 Draft |
| W4.P1 | Author ADR-081 with decision rationale + per-category classification + 90-day shim deprecation calendar | `docs/architecture/adr/ADR-081-l6-observability-dependency-hygiene.md` | Must cross-reference `adg-canonical-invariants.md` §L6 multiplier and ADR-074 if applicable | 2k | 📋 Draft |
| W4.P2 | Regenerate ADG; verify L6→lower count drops by ≥15 (target: 39 → ≤24); flip Notion row #1 to Done; update ADR Registry | `python tools/generate_full_adg.py` run; post-run sqlite query | ADG regen is ~60s runtime; progress bar mandatory per constitutional §16 | 1k | 📋 Draft |

## ADG_HOTSPOT_REPORT

Per constitutional §22 (graph-layer primary driver for refactoring). Query against `adg_indexed_05012026_0632.sqlite`.

| Rank | File | Archetype | Surface | Layer Mult | Fan-In | L6→lower imports | Notes |
|---:|---|---|---|:---:|---:|---:|---|
| 1 | `agentic_core/L6_observability/utils/integrity_report_generator_util.py` | ORCHESTRATOR | Observability | ×0.75 (L6) | TBD | 9 | **W2 move target**. Report generator, not core observability — natural L_OPS fit. |
| 2 | `agentic_core/L6_observability/utils/evaluation/governed_handoff.py` | CENTRAL_DEPENDENCY | State | ×0.75 (L6) | TBD | 3 | W2 candidate (evaluate for L_OPS move) |
| 3 | `agentic_core/L6_observability/utils/evaluation/async_eval_packet.py` | CENTRAL_DEPENDENCY | State | ×0.75 (L6) | TBD | 3 | W2 candidate |
| 4 | `agentic_core/L6_observability/utils/engines/desk_d_governed_board.py` | ORCHESTRATOR | Execution | ×0.75 (L6) | TBD | 3 | W2 candidate — engine file inside observability is unusual |
| 5 | `agentic_core/L2_execution/utils/providers.py` | CENTRAL_DEPENDENCY | Execution | ×1.0 (L2) | 11 (from L6) | — | **Target of 11 imports** — W3 exception documentation target |
| 6 | `agentic_core/L2_execution/audit/telemetry_bus.py` | CENTRAL_DEPENDENCY | Observability | ×1.0 (L2) | 4 (from L6) | — | W3 exception doc target — telemetry publisher |
| 7 | `agentic_core/L2_execution/utils/write_gateway.py` | STATE_NODE | Write | ×1.0 (L2) | 3 (from L6) | — | W3 exception doc target — write-path chokepoint |

Surface intersections (per adg-canonical-invariants §3):
- Rank 1–4 intersect **Observability** (monitoring integrity) — swallowed failures → broken forensics
- Rank 5 intersects **Execution**; Rank 7 intersects **Write** — both critical surfaces where blind import paths matter

## ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22. Queried directly via SQLite (MCP pointed at sibling repo at query time).

Materialized views consulted:
1. `mv_authority_boundary_breaches` — **0 rows** (17 dead re-exports eliminated in commit `079958b47d` 2026-04-30). Proves this plan is NOT closing authority breaches; it addresses gravity violations.
2. `mv_graph_reverse_dependency_hotspots` — `L2_execution/utils/providers.py` surfaces as high-fan-in target across multiple caller layers; confirms exception documentation (not refactor) is correct for Cat C.
3. `mv_hotspot_centrality` — `integrity_report_generator_util.py` centrality within L6 cluster is low (peripheral reporter), confirming L_OPS migration is safe (no risk of orphaning L6 core observability).

Semantic edges used:
- `imports` (primary) — all 39 L6→lower edges quantified above
- `flows_to` — will pre-flight before W2.P2 to confirm moved files don't carry hidden runtime dataflow back into L6
- `resolves_callsite` — will pre-flight before W1.P2 to confirm shim pattern resolves correctly across all call sites

P-views cross-referenced:
- `v_p0_write_bypass_uwg` — `write_gateway.py` is UWG; L6 importing it MUST not bypass write discipline. W3 exception entry will document this.
- `v_p1_mis_layered_infra` — current state, Cat B + C files likely surface here; W3 exception entry brings them into accepted list.
- `v_p1_zero_caller_infra` — check post-W1/W2 that no neutral-layer type becomes orphaned.

## Assumptions, Uncertainty, Risks

### Assumptions

- A-1: `agentic_core/_shared/` as a neutral layer is acceptable (no existing convention against it). Alternative: `infrastructure/types/`. **Resolution**: W1.P1 confirm precedent via `infrastructure/` folder inspection.
- A-2: `L_OPS/` follows same precedent as existing `L_TOOLS/`, `L_APP/`, `L_SHARED/` layers (defined in `agentic_core/adg/severity_bands.py` or similar). **Resolution**: W2.P1 confirm layer-enum definition before creating the folder.
- A-3: `config/architectural_exceptions.yaml` exists and accepts extension. **Resolution**: W3.P1 Phase 0 — read file first.
- A-4: Back-compat shim pattern (re-exports at old paths) preserves ADG authority-boundary hygiene. Risk: re-exports count as edges. Mitigation: shim files use `__all__` sparingly and are tagged with `# guardian: allow-shim-reexport -- 90-day deprecation per ADR-081`.

### Uncertainty

- U-1: Whether `governed_handoff.py`, `async_eval_packet.py`, `desk_d_governed_board.py` are genuine L_OPS candidates or must remain in L6. **Resolution**: W2.P2 Phase 0 — read each file and confirm scope (reporter/orchestrator) before moving.
- U-2: Exact ADR-081 number — confirm next free number in Notion ADR Registry before authoring. Current highest visible: ADR-080.

### Risks

- R-1: Shim pattern introduces new edges that re-trigger authority-boundary classification. Mitigation: W4.P2 post-regen verification; rollback plan in ADR-081.
- R-2: Moving `integrity_report_generator_util.py` breaks an undocumented consumer. Mitigation: W2.P2 pre-flight fan-in scan via `adg_edge_fanin(tgt_id=..., relation_type="imports")`.
- R-3: `_shared/` layer turns into a god-bag if future sessions add unrelated files. Mitigation: ADR-081 includes inclusion criteria (types + constants only; no behavior, no enforcement, no I/O).

## Rollback Checkpoints

Per operational-gates rule. Each wave is atomic-revertable via git.

| Wave | Rollback action | Detection signal |
|---|---|---|
| W1 | `git revert` the move commit; restore back-compat shims | Any L0-L6 module fails to import after W1.P2 |
| W2 | `git revert` the move commit; restore files in L6_observability | L6 downstream consumer breaks |
| W3 | Remove added entries from `architectural_exceptions.yaml` | CI gate detects spurious new exemptions |
| W4 | N/A (doc-only); revert ADR file if content is wrong | ADR review feedback |

## Options (for completeness — Option 1 already selected)

1. **Hybrid pragmatic** ← SELECTED 2026-05-01
2. Type/constant extraction only (rejected — leaves top offender untouched)
3. Full architectural refactor (rejected — multi-day effort, simplicity penalty)
4. Document-as-debt only (rejected — no actual reduction)

Re-authorization required if scope changes mid-execution.

## Execution Prereqs (before any W1 edit)

1. ADG green-light check: `python tools/adg/adg_redis_ingest.py --check` OR `adg_health` (via MCP when pointed at FRESH repo)
2. ADG snapshot fresh (≤1 day old): current `adg_indexed_05012026_0632.sqlite` satisfies
3. `run_contract_gates.py` passes on baseline
4. Branch from `main`: `feat/l6-gravity-hybrid-<date>`
5. Re-auth user confirmation that Option 1 scope is unchanged
