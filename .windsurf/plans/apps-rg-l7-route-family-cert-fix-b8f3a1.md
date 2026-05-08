# Plan: apps_rg L7 Route Family Coverage Certification Fix

**Slug**: `apps-rg-l7-route-family-cert-fix-b8f3a1`
**Tier**: T2 (3 files, single concern, single layer L7_auditability + runtime/entrypoints)
**Created**: 2026-05-08
**Status**: Completed

PLAN_CREATED: slug=apps-rg-l7-route-family-cert-fix-b8f3a1 path=.windsurf/plans/apps-rg-l7-route-family-cert-fix-b8f3a1.md

## Problem Statement

The mandatory L7 Route Family Coverage Matrix shows `0/9 CERTIFIED` after a successful apps_rg run. RCA on 2026-05-07 identified two root causes:

1. **Contract mismatch** — `_route_contract_emitted()` at `@c:\Git\Agentic-Workflow-FRESH\agentic_core\L7_auditability\coverage\route_family_l7_coverage.py:329-336` requires `payload.request_id` AND `payload.trace_root`. Three emission sites all write `route_contract.json` without those fields:
   - `@c:\Git\Agentic-Workflow-FRESH\agentic_core\runtime\entrypoints\integrated_r4_deterministic_pipeline_run.py:798-810` (apps_rg's actual emitter)
   - `@c:\Git\Agentic-Workflow-FRESH\agentic_core\runtime\entrypoints\integrated_r4_lic_pipeline_run.py` (apps_lic parity)
   - `@c:\Git\Agentic-Workflow-FRESH\apps_shared\spine_emission\context.py:525-537` (cross-app surface)

2. **Cache staleness** — R1A exact-cache hits return frozen artifacts. L7 evidence emitted before the writer-reader contract was tight remains permanently NOT_CERTIFIED. (Out of scope here — see DEFERRED_SCOPE.)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1   | P1.1, P1.2 | Patch the 3 route_contract emission sites to include `request_id` + `trace_root` in payload | ~6k | Cascade may run R1A cache bypass to verify | ✅ DONE | All 3 sites emit `payload.request_id` + `payload.trace_root` |
| W2   | P2.1, P2.2 | Run apps_rg with R1A cache bypass; verify fresh L7 matrix shows R4_SINGLE_ACTION CERTIFIED | ~4k | apps_rg is invocable end-to-end | ✅ DONE | Console L7 table shows `1/9 CERTIFIED` and R4_SINGLE_ACTION row marks `✅ CERTIFIED ✅ REAL_RUNTIME` |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| P1.1 | Patch agentic_core R4 entrypoints | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`, `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | request_id + trace_root must already be in scope at emission point | ~3k | ✅ DONE |
| P1.2 | Patch apps_shared spine_emission context | `apps_shared/spine_emission/context.py` | Same payload addition for cross-app emit surface | ~2k | ✅ DONE |
| P2.1 | Force fresh apps_rg run (cache bypass) | Delete `artifacts/apps_rg/runs/r4_72afb54f/` OR change input fingerprint | R1A is sticky; need clean-slate for verification | ~1k | ✅ DONE |
| P2.2 | Verify L7 matrix output | Read `agentic_core_l7_route_family_coverage.json` + console formatter | Must see R4_SINGLE_ACTION row CERTIFIED + `summary.certified=1` | ~3k | ✅ DONE |

## ADG_HOTSPOT_REPORT

| Rank | Node | File | Layer | Fan-in (imports) | Archetype | Surface | Impact |
|------|------|------|-------|-----------------:|-----------|---------|-------:|
| 1 | `ADG::Module::agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` (id=1739) | `agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` | L_UNKNOWN (L6 observability semantics) | 0 (newly emitted; not yet projected) | SAFETY_GATEKEEPER | Observability | Low — read-only classifier, no callers depend on its mutation surface |
| 2 | `ADG::Module::agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` (id=2353) | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | L_RUNTIME (L3 orchestration semantics) | 0 (newly emitted; called by apps_rg `__main__`) | ORCHESTRATOR | Execution + Observability | Medium — exclusive R4 entrypoint for apps_rg; payload-shape change is additive |
| 3 | `ADG::Module::apps_shared/spine_emission/context.py` | `apps_shared/spine_emission/context.py` | apps_shared (cross-app surface) | (broad — used by apps_eval, apps_exec, etc.) | CENTRAL_DEPENDENCY | Execution + Observability | Medium — payload-shape change is additive, but multi-app surface |

**Surface intersection**: All three nodes intersect Observability (L7 evidence). #2 also intersects Execution (R4 spine entrypoint). #3 intersects Execution (cross-app spine). No intersection with Security, Write, or State surfaces.

**Layer multipliers**: L6 ×0.75, L3 ×1.75. The R4 entrypoint dominates impact ranking but the change is additive (new payload keys), so blast radius is bounded.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05052026_0722.sqlite

## ADG_GRAPH_LAYER_EVIDENCE

Three graph-layer primitives consulted; due to recent emission of these nodes, semantic edges and MV rows are not yet populated. Falling back to direct reads via `adg_nodes_by_file` + `adg_edge_fanin(imports)`.

1. **MV `mv_hotspot_centrality`** — neither route_family_l7_coverage nor integrated_r4_deterministic_pipeline_run appear in the top hotspot rows; impact is contained.
2. **Semantic edge `flows_to`** — no `flows_to` edges out of these nodes are projected yet; the change is at the artifact-emission boundary, not control flow.
3. **P-view `v_p2_anti_pattern_density`** — neither file has a P0/P1 anti-pattern row; payload patches do not introduce new anti-patterns.
4. **`adg_edge_fanin` (imports)** — fan_in=0 for all three module ids (newly emitted snapshot), so blast radius is bounded by current callers (apps_rg `__main__` → R4 entrypoint; apps_eval/apps_exec → spine_emission/context).

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05052026_0722.sqlite

## Files In Scope

- `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` (P1.1)
- `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` (P1.1)
- `apps_shared/spine_emission/context.py` (P1.2)

## Out of Scope (Deferred)

DEFERRED_SCOPE: id=l7-cache-refresh title="Refresh L7 evidence on R1A cache hit" rationale="cache writeback path is the L0.6 gap already tracked in spine trace; separate fix from contract patch" parent_plan=apps-rg-l7-route-family-cert-fix-b8f3a1

DEFERRED_SCOPE: id=l7-verifier-fail-closed title="Make verify_agentic_core_l7_route_family_coverage.py fail-closed when exercised family is NOT_CERTIFIED" rationale="needs separate gate scoping; not blocking the contract patch" parent_plan=apps-rg-l7-route-family-cert-fix-b8f3a1

## Verification Steps (W2)

1. Delete or rename `artifacts/apps_rg/runs/r4_72afb54f/` to bypass R1A cache.
2. Run: `python -m apps_rg --target-company "Brown & Brown" --target-role "Senior Vice President, IT Strategy & Innovation" --jd apps_rg/scripts/jd_brown_brown_svp_it_strategy_20260507.json`
3. Inspect new run dir's `agentic_core_l7_route_family_coverage.json`:
   - `summary.certified` MUST be `1` (not 0).
   - R4_SINGLE_ACTION row MUST have `certification_status="CERTIFIED"`, `proof_class="REAL_RUNTIME"`, `route_contract_emitted=true`, `artifact_manifest_bound=true`.
4. Console output L7 table MUST show `Certified ✅ 1/9` and `R4_SINGLE_ACTION ✅ CERTIFIED ✅ REAL_RUNTIME`.

## Rollback

Each patch is additive (adds two payload keys). Rollback = `git revert <commit>` of the W1 commit. No state migration needed.

## References

- RCA conversation: 2026-05-07 21:13 UTC-04
- Source file: `@c:\Git\Agentic-Workflow-FRESH\agentic_core\L7_auditability\coverage\route_family_l7_coverage.py:329-336` (classifier)
- Source file: `@c:\Git\Agentic-Workflow-FRESH\agentic_core\runtime\entrypoints\integrated_r4_deterministic_pipeline_run.py:795-810` (apps_rg emitter)
