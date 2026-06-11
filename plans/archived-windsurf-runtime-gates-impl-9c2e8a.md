---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-impl-9c2e8a.md'
original_relative_path: 'runtime-gates-impl-9c2e8a.md'
source_sha256: d61054487b78f233da3e22ac4e81ba17903ac090c4c7f743d22c0cfeaef4b8f8
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Gates Implementation — All 29 Gates

**Status**: In Progress
**Tier**: T3
**Source spec**: `docs/reference/05_Exit_Evaluation_&_Control/Evaluation_Runtime_Gates.md`
**ADG snapshot**: `04252026_0843`
**Created**: 2026-04-25

## Goal

Implement every runtime gate G01–G29 specified in `Evaluation_Runtime_Gates.md` as a coherent, testable mesh under `agentic_core/L5_safety/runtime_gates/`.

Each gate must:
1. Honor the spec's `Required checks` as deterministic pre-conditions
2. Emit one of the spec's enumerated `Allowed decisions` as a `Disposition`
3. Recognize the spec's `Regression signals` (counters/flags emitted with the decision)
4. Enforce the spec's `Stop condition` (fail-closed when invariant violated)

## Module Layout

```
agentic_core/L5_safety/runtime_gates/
├── __init__.py            # Re-exports
├── types.py               # Disposition, GateContext, GateDecision, RegressionSignal
├── base.py                # RuntimeGate Protocol, GateRegistry
├── g01_request_ingress.py
├── g02_identity_session.py
├── ...
└── g29_learning_firewall.py
```

## Wave Plan

| Wave | Phase IDs | Gates | Focus | Est Tokens | Status |
|---|---|---|---|---|---|
| W1 | W1.1, W1.2 | Framework + G01-G06 | Types/base/ingress/identity/intent/safety/risk/HITL | 7000 | In Progress |
| W2 | W2.1 | G07-G12 | Route/retrieval/evidence/prompt/registry/args | 6000 | Pending |
| W3 | W3.1 | G13-G18 | Trust/egress/fs/memory/privacy/workflow | 6000 | Pending |
| W4 | W4.1 | G19-G24 | Loop/budget/schema/quality/security/replay | 6000 | Pending |
| W5 | W5.1, W5.2 | G25-G29 + commit | Anomaly/exit/UWG/audit/learning + final commit | 5000 | Pending |

## Phase Summary

| Phase | Title | Scope | Pain Points | Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Framework | types.py, base.py, __init__.py | Disposition enum scope; balance protocol vs ABC | 1500 | todo |
| W1.2 | G01-G06 + tests | 6 gate files + 6 test files | Each gate's "Required checks" must be testable in isolation | 5500 | todo |
| W2.1 | G07-G12 + tests | 6 gates + tests | Tighter coupling to L0 RouteContract / C0 retrieval data | 6000 | todo |
| W3.1 | G13-G18 + tests | 6 gates + tests | Trust gate needs origin classifier; fs gate needs sandbox model | 6000 | todo |
| W4.1 | G19-G24 + tests | 6 gates + tests | Replay/determinism gate has cross-cutting state | 6000 | todo |
| W5.1 | G25-G29 + tests | 5 gates + tests | Anomaly gate needs baseline registry stub | 4500 | todo |
| W5.2 | Commit + push | Single commit with all 29 gates | n/a | 500 | todo |

## ADG_HOTSPOT_REPORT

| Target Area | Layer | Archetype | Risk | Notes |
|---|---|---|---|---|
| `runtime_gates/` (NEW) | L5_safety | SAFETY_GATEKEEPER | H | Greenfield; isolated; no fan-in initially |
| `types.py` (NEW) | L5_safety | CENTRAL_DEPENDENCY | M | Will be imported by all 29 gates |
| `base.py` (NEW) | L5_safety | CENTRAL_DEPENDENCY | M | Registry + Protocol — small surface |

Greenfield module — no existing fan-in to disturb. Production wiring of these gates into the L1/L0/C0/L2/L3/L5 pipelines is **out of scope** for this implementation pass and will be tracked as a NEXT_STEP follow-up.

## ADG_GRAPH_LAYER_EVIDENCE

- `mv_dependency_cone_risk`: New module is leaf — no downstream blast radius
- `mv_hotspot_centrality`: 29 leaf files import from 2 shared (`types`, `base`) — low centrality
- Semantic edges: `flows_to`, `verifies_policy` will be emitted by gates per existing `_telemetry` patterns where appropriate
- P-views: V_p1_zero_caller_infra is intentional initial state (gates are wired in NEXT_STEP)

## Success Criteria

- [ ] 29 gate files exist under `agentic_core/L5_safety/runtime_gates/`
- [ ] Each gate has at least 3 unit tests (happy path, invariant violation, regression signal)
- [ ] All py_compile clean
- [ ] All ruff format clean
- [ ] Total test count >= 90 (29 × 3)
- [ ] `__init__.py` exports `Disposition`, `GateDecision`, `GateContext`, `RuntimeGate`, `GATE_REGISTRY`
- [ ] Final commit pushed to `origin/main`

## Out of Scope (deferred)

- Wiring gates into production L0/L1/L2/L3/L5 dispatch — separate NEXT_STEP plan
- Backing baseline registry for G25 anomaly detection — placeholder stub
- HMAC signing infrastructure — gates emit signature placeholder
- Live OpenTelemetry span emission — gates emit dataclass receipts only
