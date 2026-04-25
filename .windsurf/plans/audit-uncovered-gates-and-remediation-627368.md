# Audit Uncovered Gates + Remediation Plan

**Plan ID**: `audit-uncovered-gates-and-remediation-627368`
**Created**: 2026-04-25
**Tier**: T3 (architectural, cross-layer, multi-file, multi-module)
**ADG Snapshot**: `adg_indexed_04252026_0521.sqlite` (regenerated 09:25:03Z)

## Parent Plan Summary

This plan operationalizes the validated findings from the 16-phase ADG technical-debt audit (artifacts: `audit_phase{1..16}*.json`, `audit_validation_final.json`). Of 5,630 raw findings across 10 categories not currently covered by any of the 94 ADG CI gates, **5,482 (97.4%) were validated as real**. This plan delivers (a) 6 new CI gates closing those coverage gaps, then (b) remediation behind those gates so future regressions cannot reintroduce the same defects.

## ADG_HOTSPOT_REPORT

**Surface coverage** (per `adg-canonical-invariants.md` §3): the hotspots
below intersect the **Security Surface** (L5 safety adapters and gatekeepers
enforcing approval/policy), the **Write Surface** (state mutations through
UWG and SovereignBaseAgent paths), the **State Surface** (memory/cache
canonical stores), the **Observability Surface** (L6 trace/audit recorders
and telemetry emitters), and the **Execution Surface** (agent dispatch and
tool-invocation boundaries). Surface intersections drive the impact-score
multipliers in column "Impact".

| Rank | Hotspot Path | Layer | Fan-In | Surface | Archetype | Impact |
|------|-------------|-------|-------:|---------|-----------|-------:|
| 1 | `agentic_core/L5_safety/adapters/human_approval_adapter.py` | L5 | 50 | Security+State | SAFETY_GATEKEEPER | 100.0 |
| 2 | `agentic_core/L5_safety/utils/location_healer_util.py` | L5 | 9 | Exec+Obs+Write | ORCHESTRATOR | 53.6 (cross-4 mainline) |
| 3 | `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | L2 | — | Execution | ORCHESTRATOR | (cross-4 mainline) |
| 4 | `agentic_core/L0_routing/config/path_constants.py` | L0 | 1052 | Obs+State | CENTRAL_DEPENDENCY | 74.4 (truly-blind) |
| 5 | `agentic_core/L0_routing/config/model_registry.py` | L0 | 56 | Obs+State | STATE_NODE | 68.2 (blind) |
| 6 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | L5 | 80 | State | STATE_NODE | (blind) |
| 7 | `BATCH_SIZE` symbol (16 files, 4 layers) | multi | — | None | SSOT_VIOLATION | 64.0 |
| 8 | `BUFFER_SIZE`, `THRESHOLD`, `MAX_RETRIES` symbols | multi | — | None | SSOT_VIOLATION | 60.0 |
| 9 | `ExecutionContext` symbol (5 layers L2-L_OPS) | multi | — | None | SSOT_VIOLATION | 50.0 |
| 10 | `NOTION_API_VERSION` literal (10 occurrences) | L_WINDSURF | — | None | SSOT_VIOLATION | 30.0 |

## ADG_GRAPH_LAYER_EVIDENCE

Materialized views consulted: `mv_hotspot_centrality` (fan_in/fan_out for ranking), `mv_authority_boundary_breaches` (cross-layer SSOT), `mv_zero_caller_infra` (orphan detection cross-check).

Semantic edges relied on: `flows_to`, `resolves_callsite`, `invokes_dynamic`, `reads_from`, `emits_side_effect`, `controls_flow`, `imports`, `calls`.

P-views cross-referenced: `v_p0_apps_direct_infra` (no overlap — these are uncovered categories), `v_p1_mis_layered_infra` (Phase 12 dispatchers overlap with mis-layered), `v_p1_zero_caller_infra` (Phase 15 overlap — proved 33/36 are dynamic-loaded, not zero-caller).

Validation provenance: `artifacts/audit_validation_final.json` records the cross-check method, raw count, validated count, and false-positive rate per category.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | 1.1-1.6 | Implement 6 new CI gates (no enforcement yet) | 12000 | ADG SQLite reachable read-only | Todo | All 6 gates compile + smoke-test passes; baseline JSON written |
| W2 | 2.1-2.3 | SSOT magic-constant consolidation | 6000 | Existing path_constants.py is canonical | Todo | BATCH_SIZE/BUFFER_SIZE/THRESHOLD/MAX_RETRIES consolidated; 200+ removals |
| W3 | 3.1 | NOTION literal SSOT module | 2000 | `.windsurf/scripts/_notion_constants.py` is acceptable location | Todo | 21 hardcoded NOTION_* literals replaced with imports |
| W4 | 4.1 | Observability hooks for 5 truly-blind modules | 4000 | `agentic_core/mixins/L6MetricsEmissionMixin.py` is canonical | Todo | All 5 modules have ≥1 trace/audit edge |
| W5 | 5.1 | Activate gates as ratchet (CI-blocking) | 3000 | Baselines from W1 hold | Todo | Gates added to `.pre-commit-config.yaml` and CI workflows |
| W6 | 6.1 | Final ADG regen + burndown verification | 2000 | All prior waves complete | Todo | Burndown shows P0/P1 stable or improved; new gates green |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| 1.1 | `check_ssot_magic_constants.py` | `ops_scripts/ci/` | Layer detection from ADG | 2000 | Todo |
| 1.2 | `check_observability_on_high_fanin.py` | `ops_scripts/ci/` | Trace-edge pattern breadth | 2000 | Todo |
| 1.3 | `check_external_service_literal_ssot.py` | `ops_scripts/ci/` | Allowlist for SSOT module paths | 2000 | Todo |
| 1.4 | `check_cross_mainline_dispatcher.py` | `ops_scripts/ci/` | Mainline-only filter | 2000 | Todo |
| 1.5 | `check_env_var_in_config_layer.py` | `ops_scripts/ci/` | Edge-based env detection | 2000 | Todo |
| 1.6 | `check_violation_aging_sla.py` | `ops_scripts/ci/` | First-seen timestamp source | 2000 | Todo |
| 2.1 | Consolidate to `path_constants.py` | `agentic_core/L0_routing/config/path_constants.py` and 14 dup files | Backward compat for re-exports | 3000 | Todo |
| 2.2 | Refactor 11+ apps_lic/apps_rg/apps_shared dups | apps_*/config/, apps_*/utils/ | Per-app override semantics | 2000 | Todo |
| 2.3 | Sweep BATCH_SIZE/BUFFER_SIZE/THRESHOLD callers | global | py_compile per file | 1000 | Todo |
| 3.1 | NOTION constants SSOT | `.windsurf/scripts/_notion_constants.py` + 21 callers | Cross-script import path | 2000 | Todo |
| 4.1 | Wire 5 blind modules to L6 emission | 5 specific files | Mixin import location | 4000 | Todo |
| 5.1 | Pre-commit + CI activation | `.pre-commit-config.yaml`, `.github/workflows/` | Baseline drift | 3000 | Todo |
| 6.1 | Final ADG regen + verify | none (read-only) | Background command | 2000 | Todo |

## Gap Register

- Phase 11 (provider egress concentration) deferred — needs adapter-pattern review, not gate-able yet.
- Phase 13 (cycles) — confirmed clean, no action.
- Phase 15 (orphan configs) — only 3 truly orphan, deferred to manual review.

## Out of Scope

- W2-W4 remediation work overlapping with active P0/P1/P2 burndown waves (memory: high-wave1-p1-zero-a13f7c, p1-antipattern-burndown-d1b25e). Those waves continue independently.
- Phase 14 env-var centralization deferred to a separate plan (50 modules, requires environment_config.py SSOT design first).
- Phase 12 cross-mainline dispatcher refactor deferred — gate detects, but actual L5/L2 agent restructuring needs ADR.

## Status

Wave 1 in progress.
