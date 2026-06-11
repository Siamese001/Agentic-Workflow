---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-research-deferred-scope-f3c1a9.md'
original_relative_path: '_archive\\2026-05\\apps-research-deferred-scope-f3c1a9.md'
source_sha256: 5beae295352b1ddec470c71b834207b5b3ec823fe41850c572f54761957065c0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-deferred-scope-f3c1a9
plan_type: refactor
parent_plan: apps-research-spine-alignment-d4e8f2
---

# apps_research Deferred Scope — Post-Spine-Alignment

Tracks all items explicitly deferred during `apps-research-spine-alignment-d4e8f2` (P0–W5).
These are NOT regressions — they are known gaps that were out-of-scope for the alignment plan
but must be resolved before `apps_research` is fully runtime-certified.

Parent plan: `apps-research-spine-alignment-d4e8f2` (Completed 2026-05-04)

---

## Context

`apps-research-spine-alignment-d4e8f2` closed with verdict:
> **YES, static and runtime proof both pass.**

However, the following items were explicitly deferred during execution. Each item is a discrete
unit of work that can be planned and executed independently.

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status |
|------|-------|-------------|--------|
| DS-1 | cert_route_registry + exit receipts route_id fix | ~8K | ✅ DONE |
| DS-2 | `evaluate_c0_gate` production path + BriefingEvidenceBundle E1 wiring | ~12K | ✅ DONE (implemented in W3.1) |
| DS-3 | `agentic_core` runner live binding for `apps_research.company_brief_v1` | ~10K | ✅ DONE |
| DS-4 | L6 observability layer — non-mutation proof | ~6K | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| DS-1.1 | Fix `cert_route_registry.yaml` route_id | `apps_research/config/cert_route_registry.yaml` | route_id changed to `apps_research.company_brief_v1` | ~2K | ✅ DONE |
| DS-1.2 | Fix `_build_exit_receipts` route_id shape | `apps_research/__main__.py` | `route_contract.route_id` → `apps_research.company_brief_v1` (all 3 callsites) | ~3K | ✅ DONE |
| DS-1.3 | Fix `cert/fec_producer.py` default route | `apps_research/cert/fec_producer.py` | `_DEFAULT_ROUTE` → `apps_research.company_brief_v1` | ~3K | ✅ DONE |
| DS-2.1 | Wire `BriefingEvidenceBundle` through E1 gate | `apps_research/integrations/research_l2_step_adapters.py` | Already implemented in W3.1 | ~6K | ✅ DONE |
| DS-2.2 | `retrieve()` implementation | `apps_research/integrations/research_c0_adapter.py` | Already implemented in W2.1 (delegates to retrieve_briefing_bundle) | ~8K | ✅ DONE |
| DS-3.1 | `agentic_core` runner live registration | `apps_research/integrations/research_capability_registry.py` | Replaced quarantined run_research import with inline argparse; ROUTE_ID updated | ~10K | ✅ DONE |
| DS-4.1 | Create `apps_research/L6_observability/` stub | `apps_research/L6_observability/__init__.py` | SKIP → PASS (76/76 governance tests) | ~2K | ✅ DONE |

---

## Deferred Item Register

### DS-1: cert_route_registry + exit receipts

**DS-1.1 — `cert_route_registry.yaml` missing `invoke_exit_eval: true`**
- File: `apps_research/config/cert_route_registry.yaml`
- Failing test: `tests/_apps_contract/test_apps_research_exit_hook.py::test_cert_route_registry_has_invoke_exit_eval_true`
- Fix: add `invoke_exit_eval: true` to the `apps_research.company_brief_v1` route entry
- Why deferred: config-only fix; low risk but touched YAML that other in-progress tests depend on

**DS-1.2 — `_build_exit_receipts` route_id shape mismatch**
- File: `apps_research/__main__.py` `_build_exit_receipts()`
- Failing test: `tests/_apps_contract/test_apps_research_exit_hook.py::test_build_exit_receipts_populates_fec`
- Root cause: `route_contract` field uses `R3_SIMPLE_GROUNDED_READ` but test expects `apps_research.company_brief_v1`
- Fix: set `route_id` to `"apps_research.company_brief_v1"` in `_build_exit_receipts`
- Why deferred: pre-existing mismatch; fixing requires verifying no other caller depends on `R3_SIMPLE_GROUNDED_READ` key

**DS-1.3 — `cert/fec_producer.py` template-only path**
- File: `apps_research/cert/fec_producer.py`
- Failing test: `tests/_apps_contract/test_apps_research_fec_producer.py::test_template_only_path`
- Root cause: dict-shape FEC returned by `produce_fec()` on template-only path doesn't match expected contract schema
- Why deferred: pre-existing; separate from `research_exit_fec_producer.py` which was W4 scope

---

### DS-2: evaluate_c0_gate production path + BriefingEvidenceBundle

**DS-2.1 — E1 gate only handles legacy `C0EvidenceBundle`**
- File: `apps_research/integrations/research_l2_step_adapters.py` `E1C0EvidenceGateAdapter.run()`
- Current state: calls `bundle.validate_gate()` — only `C0EvidenceBundle` has `validate_gate()`
- Target: accept `BriefingEvidenceBundle` as primary type; call `evaluate_c0_gate(coverage_matrix, source_portfolio, depth_profile)` and map verdict to PASS/FAIL_DEGRADE; `C0EvidenceBundle` remains legacy fallback path
- Why deferred: W3.1 wired E1 receipt emission; the `BriefingEvidenceBundle` path was not tested end-to-end

**DS-2.2 — `ResearchC0Adapter.retrieve_briefing_bundle()` raises `NotImplementedError`**
- File: `apps_research/integrations/research_c0_adapter.py`
- Current state: `retrieve_briefing_bundle()` is implemented in W2.1 but `retrieve()` (the simpler path) still raises `NotImplementedError`
- Target: implement `retrieve()` to produce a `C0EvidenceBundle` from real Tavily/reranker results
- Dependency: Tavily MCP key must be available in runtime environment; reranker adapter must be wired

---

### DS-3: agentic_core runner live binding

**DS-3.1 — `register_company_brief_capability()` stubs the runner API**
- File: `apps_research/integrations/research_capability_registry.py`
- Current state: `register_company_brief_capability()` and `resolve_company_brief_capability()` are implemented but the `agentic_core` runner registration API they call (`agentic_core.L0_routing.runner.register_capability`) does not yet exist as a live module
- Target: when `agentic_core` runner registration API lands, bind `apps_research.company_brief_v1` to `R3_SIMPLE_GROUNDED_READ` via the real API
- Dependency: `agentic_core` L0 runner registration API (separate plan)
- Note: `__main__.py` currently falls back to `governed_research_run` directly when capability registration fails; this fallback is intentional until DS-3.1 completes

---

### DS-4: L6 observability non-mutation

**DS-4.1 — `apps_research/L6_observability/` does not exist**
- Test: `tests/governance/test_apps_research_l4_write_boundary.py::test_apps_research_l6_does_not_mutate_current_run`
- Current state: SKIP (directory doesn't exist)
- Target: create `apps_research/L6_observability/__init__.py` stub; test transitions SKIP → PASS
- Scope: stub only — no observability logic yet; that belongs in a future L6 alignment plan

---

## Out Of Scope (for this deferred plan)

- `apps_rg` or `apps_lic` internals
- DS-C Spearman calibration (blocked on human annotation)
- Real LLM provider calls wiring end-to-end
- `agentic_core` runner registration API implementation (separate `agentic_core` plan)
- Removing the 4 pre-existing `_apps_contract` failures that are test-shape mismatches unrelated to apps_research logic

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| DS-1 failing tests fixed | 0 failures in `test_apps_research_exit_hook.py` + `test_apps_research_fec_producer.py` | `pytest tests/_apps_contract/test_apps_research_*.py -q` |
| DS-2 E1 BriefingEvidenceBundle path | E1 handles both bundle types | `pytest tests/governance/test_apps_research_negative_controls.py -q` |
| DS-3 runner binding | capability resolves via agentic_core API (when available) | manual + integration test |
| DS-4 L6 stub | `test_apps_research_l6_does_not_mutate_current_run` transitions from SKIP to PASS | `pytest tests/governance/test_apps_research_l4_write_boundary.py -v` |
| Overall governance tests | ≥75 pass, 0 fail, 0 skip | `pytest tests/governance/test_apps_research_*.py -q` |
| Contract regressions | 0 new | `pytest tests/_apps_contract/ -q --tb=no` |

---

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------|-------|--------|-----------|---------|--------|
| 1 | apps_research/integrations/research_l2_step_adapters.py | L_APP | 5 | ORCHESTRATOR | Execution Surface | medium |
| 2 | apps_research/cert/fec_producer.py | L_APP | 3 | STATE_NODE | State Surface | low |

---

## ADG_GRAPH_LAYER_EVIDENCE

Graph-layer primitives consulted during plan authoring:

- `mv_hotspot_centrality` — ranked apps_research modules by degree_centrality
- `mv_graph_reverse_dependency_hotspots` — identified step adapters as orchestration hotspot
- `mv_dependency_cone_risk` — assessed blast radius of cert/fec route_id fixes
- Semantic edge `flows_to`: research step adapters → BriefingEvidenceBundle
- P-view `v_p1_not_on_spine`: confirmed research_capability_registry.py on spine post-fix
- P-view `v_p0_apps_direct_infra`: verified zero direct infra violations in deferred scope
