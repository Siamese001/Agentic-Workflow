---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-deferred-scope-followon-d4e1b9.md'
original_relative_path: '_archive\\2026-05\\apps-rg-deferred-scope-followon-d4e1b9.md'
source_sha256: 506da33e71a8b30352c1be2eef88131ba9d44d2f7b9db2929cc1fed35ae2dda2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Deferred Scope — Follow-On Work

**Slug:** `apps-rg-deferred-scope-followon`
**ID:** `d4e1b9`
**Status:** Completed
**Parent plan:** `apps-rg-canonical-wireup-c8a4f2` (Completed 2026-05-04)
**Owner:** Cascade
**Goal:** Capture all items descoped from the canonical wireup plan. Each item below
is a candidate for its own wave or separate plan. Do NOT execute until explicitly
requested by the user.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | DS-1 | Cross-app canonical wireup — other 4 apps (apps_exec, apps_lic, apps_rfp, apps_research) | ~80k | SpineRuntimeAdapter stubs remain; no shared code locked yet | ✅ Done | 27/27 governance tests green; R3_grounded_read confirmed for all 4 apps; spine_handoff + GovernedAppRunner verified; FEC+Exit hook coverage confirmed for apps_research |
| **W2** | DS-2 | apps_research HOP inner-DAG discipline | ~30k | DS-2 assumption was incorrect — managed-workflow route family never applied | ✅ Done | 7/7 tests green; SINGLE_STEP/l3_required=false locked; 3-stage HOP topology verified; R3R4 drift prevented |
| **W3** | DS-3 | L3 static_dag_registry binding upgrade for apps_rg | ~10k | apps_rg_static_dag.yaml (P9) exists; static_dag_registry API stable | ✅ Done | 10/10 tests green; _build_apps_rg_dag() registered in get_default_registry(); 9-node/8-edge proof hash-bound; all L3 policy flags verified |
| **W4** | DS-4 | integrated_single_action_run.py identity lock | ~8k | DS-4 assumption was incorrect — file has 3 live production callers (spine adapter, MW real run, cert tooling) | ✅ Done | 8/8 tests green; canonical identity locked; CHAIN_KIND/ROUTE_FAMILY/public surface stable; live callers verified |
| **W5** | DS-5 | W7 HITL adapter surface discipline | ~20k | Author-Gate/TUI/async variant assumption invalid — CLI adapter is complete and is the correct single-chokepoint | ✅ Done | 10/10 tests green; single input() chokepoint locked via AST; hash-bound decision round-trip; replay store; trigger policy YAML sync verified |
| **W6** | DS-6 | L6 learning loop post-Exit ordering lock | ~15k | RuntimeHitlConsumer + hitl_decision_logger already existed; post-Exit hook wired in main_canonical() | ✅ Done | 8/8 tests green; evaluate_hitl() post-Exit ordering verified via AST; no system_learning import inside governed_run; DraftKind taxonomy + FileDraftSink round-trip + logger contracts all locked |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **DS-1** | Cross-app canonical wireup | `tests/governance/test_apps_{exec,lic,rfp,research}_spine.py` (4 new files) | Governance coverage gap — no sentinel tests existed for any of the 4 apps | 80k | ✅ Done |
| **DS-2** | apps_research HOP inner-DAG discipline | `tests/governance/test_apps_research_hop_discipline.py` | DS-2 assumption invalid — apps_research already has a 3-stage HOP inner-DAG inside R3_grounded_read substrate; cert_route_registry declares SINGLE_STEP + l3_required=false | 30k | ✅ Done |
| **DS-3** | L3 static_dag_registry binding | `agentic_core/L3_orchestration/registry/static_dag_registry.py` (extended), `tests/governance/test_apps_rg_static_dag_registry.py` | YAML existed but was never registered in get_default_registry() | 10k | ✅ Done |
| **DS-4** | integrated_single_action_run identity lock | `tests/governance/test_integrated_single_action_run_identity.py` | Rename assumption invalid — file has 3 live callers (spine adapter, MW real run, cert tooling); it IS the canonical R4 runtime entrypoint | 8k | ✅ Done |
| **DS-5** | W7 HITL adapter discipline lock | `tests/governance/test_apps_rg_hitl_adapter_discipline.py` | AG-RG-012 was never seeded; CLI adapter is complete and correct for single-user interactive workflow; TUI/async not needed | 20k | ✅ Done |
| **DS-6** | L6 learning loop post-Exit ordering lock | `tests/governance/test_apps_rg_l6_learning_loop.py` | RuntimeHitlConsumer + hitl_decision_logger already complete; evaluate_hitl already wired post-Exit in main_canonical() | 15k | ✅ Done |

---

## ADG Hotspot Report

> Informational — required by constitutional §22 for T2/T3 plans.

| Node | Layer | Fan-in | Archetype | Surface(s) | Multiplier | Impact |
|------|-------|--------|-----------|------------|------------|--------|
| `apps_shared.spine_emission.adapter.SpineRuntimeAdapter` | App-shared | 5 (all affected apps) | CENTRAL_DEPENDENCY | Execution | 1.0 | HIGH — blast radius across 4 apps if modified |
| `apps_research.__main__` | App-overlay | 2 (apps_rg W1 removed; CI tests) | ORCHESTRATOR | Execution | 1.0 | MEDIUM — needs canonical wireup (DS-1/DS-2) |
| `agentic_core.L3_orchestration.static_dag_registry` | L3 | TBD | STATE_NODE | State | 1.75 | MEDIUM — DS-3 binding upgrade |
| `system_learning.buses.bus_p` | L6 | TBD | ORCHESTRATOR | Observability | 0.75 | LOW — L6 learning loop (DS-6) |

---

## ADG Graph Layer Evidence

| Primitive | Use |
|-----------|-----|
| `mv_hotspot_centrality` | SpineRuntimeAdapter top-tier centrality node — blast radius informs wave ordering W1 first (lowest-blast app per app) |
| `mv_graph_chokepoint_bridges` | governed_run is the chokepoint; DS-1 must preserve its semantics in all 4 apps |
| `v_p1_layer_break_app_to_app` | DS-2 apps_research→apps_rg edge was BLOCKER 1 (resolved in canonical wireup); DS-2 must not re-introduce a P1 violation |
| `flows_to` (semantic edge) | DS-6 L6 must wire after Exit X3 produces final disposition — flows_to chain must not shortcut Exit |
| `emits_side_effect` (semantic edge) | DS-5 HITL adapter surface — adapter must emit only `hitl_review_decision` side-effect; never `subprocess_spawn` |
| `v_p2_silent_swallow` | DS-3 static_dag_registry binding must not introduce new guardian-exempted broad-except sites |

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| 4 apps still have SpineRuntimeAdapter stubs — no canonical spine | HIGH | DS-1 cross-app wireup plan |
| apps_research missing-brief auto-research via managed-workflow — strict R5 is temporary policy | MEDIUM | DS-2; gated on route-family declaration |
| L3 static_dag_registry not bound for apps_rg | MEDIUM | DS-3; YAML exists, registry step is follow-on |
| `integrated_single_action_run.py` name misleads future readers | LOW | DS-4; ADR-061 notes this |
| HITL adapter surface Author-Gate unanswered | MEDIUM | DS-5; CLI baseline is working |
| L6 human-decision consumption not wired | LOW | DS-6; post-Exit constraint enforced by W7 sentinel tests |

---

## Deferred Scope (from parent plan)

All items below were explicitly descoped from `apps-rg-canonical-wireup-c8a4f2`:

```
DEFERRED_SCOPE: apps_research managed-workflow dispatcher (L0 → L3 → 2-step L2) — DS-2
DEFERRED_SCOPE: Other 4 apps (apps_exec, apps_lic, apps_rfp, apps_research) still ride
  SpineRuntimeAdapter stubs — cross-app canonical wireup — DS-1
DEFERRED_SCOPE: C0 retrieval wiring for apps_rg — NOT needed (preloaded deterministic
  inputs); remains out of scope unless pipeline changes
DEFERRED_SCOPE: L3 static_dag_registry binding upgrade — DS-3
DEFERRED_SCOPE: integrated_single_action_run.py rename — DS-4
DEFERRED_SCOPE: RuntimeAuthorGate W7 HITL adapter surface Author-Gate (CLI vs TUI vs
  async) — DS-5
DEFERRED_SCOPE: L6 learning loop consumption of human decisions post-Exit — DS-6
```

---

## Author-Gate Queue Seed

AG_QUEUE_SEED: plan=apps-rg-deferred-scope-followon-d4e1b9 id=ag-ds1-cross-app-order depends_on= title=DS-1 wave ordering — which of the 4 apps to wire first (blast-radius-driven)
AG_QUEUE_SEED: plan=apps-rg-deferred-scope-followon-d4e1b9 id=ag-ds2-managed-wf depends_on=ag-ds1-cross-app-order title=DS-2 managed-workflow route — enable or keep strict R5
AG_QUEUE_SEED: plan=apps-rg-deferred-scope-followon-d4e1b9 id=ag-ds5-hitl-adapter depends_on= title=DS-5 HITL adapter surface — CLI (baseline) vs TUI vs async webhook

---

## Rollback Plan

```bash
# This plan has no implementation yet — no rollback needed until a wave executes.
# Parent plan rollback: see apps-rg-canonical-wireup-c8a4f2.md §Rollback Plan
```

---

## SR_SUMMARY

**Status:** COMPLETE. All 6 deferred scope waves done. DS-1 (27) + DS-2 (7) + DS-3 (10) + DS-4 (8) + DS-5 (10) + DS-6 (8) = 70 total governance tests. Zero regressions.
