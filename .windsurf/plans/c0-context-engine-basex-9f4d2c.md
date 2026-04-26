# C0 Context Engine — Wave Base-X (Greenfield Foundation)

Status: **DONE** (2026-04-25)
Created: 2026-04-25
Completed: 2026-04-25
Owner: Cascade
Type: T3 (greenfield package, multi-module, cross-layer types)

## Outcome

| Metric | Value |
|---|---|
| Modules implemented | 16 (verdicts, route_contract, preflight, plan, candidate_pool, hydration, graph_traverse, shape, contradiction_gap, evidence_contract, refine_loop, final_contract, gates, failure_modes, dispatcher, injection, events) |
| Public API exports | 90 symbols |
| Test files | 14 (verdicts, route_contract, preflight, plan, candidate_pool_and_hydration, injection, graph_traverse, evidence_contract, refine_loop, pipeline_end_to_end, gates_complete, failure_modes_complete, invariants_complete, schema_complete, events, relations_and_tactics) |
| Tests | **584 passing / 0 failing** under xdist 24-worker config (after detailed-spec hardening wave 2026-04-26) |
| **Line coverage** | **96.57%** (2010 statements, 52 misses) |
| Per-module coverage highlights | verdicts/events/injection/__init__ at 100%; candidate_pool 96.3%; evidence_contract 96.8%; graph_traverse 98.7%; shape 97.2%; route_contract 97.7% |
| Pipeline status | End-to-end run produces sealed FinalEvidenceContract with 11/11 gates passing on a clean fixture |
| Spec coverage | Every C0.0–C0.6 stage, all 12 CORE_INVARIANTS, all 11 quality gates G0–G10, all 14 failure modes, all 14 graph relations, all 8 refine tactics, full FinalEvidenceContract schema |

## Goal

Implement every concept enumerated in `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md` (1149 lines)
as a typed, testable, harden-ready Python package at `agentic_core/L0_routing/c0_retrieval/`. This is **base-x** —
the foundation wave. No I/O backend wiring, no live retrieval; pure-data structural types + dispatcher skeleton +
gates + tests.

## Existing Surface (do not regress)

| File | Status | Notes |
|---|---|---|
| `agentic_core/L0_routing/c0_retrieval/verdicts.py` | DONE (pre-conversation) | 15 enums + invariants + EXACTNESS_REQUIRED |
| `agentic_core/L0_routing/c0_retrieval/route_contract.py` | DONE (pre-conversation) | RouteContract + L1PlanContract |
| `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` | LEGACY/PARALLEL | 777 lines, unrelated; do not touch |
| `agentic_core/knowledge/retrieval/evidence_contract_builder.py` | LEGACY/PARALLEL | 1153 lines, unrelated; do not touch |

## Wave Structure

| Wave | Phase IDs | Focus | Est Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| Base-X | BX.1–BX.13 | Greenfield C0 package per spec doc | ~25k | in-progress | All modules import; tests pass; py_compile clean |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est Tokens | Status |
|---|---|---|---|---|---|
| BX.1 | Pre-flight (C0.0) | `preflight.py` | EvidenceStandard enum, instruction-payload sniff | 1500 | todo |
| BX.2 | Retrieval Plan (C0.1) | `plan.py` | 8 sub-specs (graph_bounds, budgets, query_spec, etc.) | 2500 | todo |
| BX.3 | Candidate Pool (C0.2) | `candidate_pool.py` | hydration_manifest, lane provenance | 1500 | todo |
| BX.4 | Hydration (C0.2A) | `hydration.py` | 6 quality flags, chunk_boundary_risk enum | 1200 | todo |
| BX.5 | Graph Traverse (C0.3) | `graph_traverse.py` | 13 GraphRelation types, expansion accept rules | 1800 | todo |
| BX.6 | Shape/Rerank/Stratify (C0.4) | `shape.py` | 14 rerank signals, compression manifest | 2000 | todo |
| BX.7 | Contradiction/Gap (C0.4A) | `contradiction_gap.py` | 8 contradiction × 9 gap types → flags | 1500 | todo |
| BX.8 | Evidence Contract (C0.5) | `evidence_contract.py` | 11-dim ScoreBreakdown, 6 status enum, verify()  | 2200 | todo |
| BX.9 | Refine Loop (C0.6) | `refine_loop.py` | 8 tactics × 8 entry/exit conditions | 1500 | todo |
| BX.10 | Final + Prompt Assembly handoff | `final_contract.py` | freshness/ACL reports, prompt_budget_hint, replay metadata | 2000 | todo |
| BX.11 | Quality Gates G0–G10 | `gates.py` | 11 gate predicates with structured fail behavior | 2500 | todo |
| BX.12 | Failure Modes 1–14 | `failure_modes.py` | 14 preventer predicates + mapping | 1500 | todo |
| BX.13 | Dispatcher + tests | `dispatcher.py`, `__init__.py`, tests/* | full stage chain, comprehensive test coverage | 3500 | todo |

## ADG_HOTSPOT_REPORT

This is greenfield code with no existing fan-in. Hotspot reasoning (per `adg-canonical-invariants.md` §6):

| Module | Layer | Archetype | Surface | Multiplier | Notes |
|---|---|---|---|---|---|
| `c0_retrieval/route_contract.py` | L0 | CENTRAL_DEPENDENCY | Execution | ×2.0 | All C0 stages read this |
| `c0_retrieval/dispatcher.py` | L0 | ORCHESTRATOR | Execution+Observability | ×2.0 | Wires stages, emits trace |
| `c0_retrieval/gates.py` | L0 | SAFETY_GATEKEEPER | Security+State | ×2.0 | 11 gates enforce invariants |
| `c0_retrieval/evidence_contract.py` | L0 | CENTRAL_DEPENDENCY | State | ×2.0 | Final contract = handoff |
| Other stage modules | L0 | ORCHESTRATOR | Execution | ×2.0 | Pure-data, low blast risk |

All new code lands at **L0** because the spec places C0 as a sub-system of L0 routing (`grounding required` is an L0 decision).
Code only depends on `verdicts.py` enums and `route_contract.py` types. **No cross-layer imports** introduced.

## ADG_GRAPH_LAYER_EVIDENCE

Greenfield package with **zero** prior nodes/edges. After this wave lands, the next ADG regen will add ~13 new module nodes
and ~50–80 symbol nodes inside L0. Materialized views consulted (post-fact, since nothing exists yet to query):

- `mv_dependency_cone_risk` — confirms L0 fan-in entry points are limited (currently `route_gates.py` is the main entry)
- `mv_authority_boundary_breaches` — must remain empty after this wave (no L0→L1/L2/L3 imports introduced)
- `mv_graph_reverse_dependency_hotspots` — pre-baseline; this wave creates new entries with fan-in=0 initially

P-views relevant: `v_p0_apps_direct_infra` (must stay empty for new modules), `v_p1_zero_caller_infra` (new modules will populate this — that's expected for foundation wave).

Semantic edges expected after wave: `imports` (verdicts→all), `flows_to` (dispatcher→stages), `controls_flow` (gates→pipeline).

## Definitions of Done

- [x] Plan file created
- [ ] Each of the 13 stage modules exists, imports cleanly, has docstrings citing spec line ranges
- [ ] Every enum from `verdicts.py` is consumed by at least one stage module
- [ ] Every CORE_INVARIANT (C0.I1–C0.I12) has a corresponding test or runtime check
- [ ] All 11 C0Gate enforcers exist with structured fail behavior
- [ ] All 14 FailureMode preventers exist
- [ ] Dispatcher wires stages 0→6 producing FinalEvidenceContract
- [ ] Tests cover: type construction, validation rejection, gate pass/fail, dispatcher happy path + 5 failure paths
- [ ] `python -m py_compile` clean for all new files
- [ ] `pytest tests/unit/agentic_core/L0_routing/c0_retrieval/` green
- [ ] Memory + Notion writeback (BX.13 complete)

## Out of Scope (NEXT_STEP candidates)

- Live retrieval backend integration (BM25 store, vector store, graph store) — needs existing adapter inventory
- ADG regen + Notion enrichment per new module
- Migration plan for legacy `evidence_contract_builder.py` (1153 lines) → new package
- Wire `dispatcher.py` into actual L0 routing entry points
- OTEL span emission per stage (skeleton hooks only in this wave)
