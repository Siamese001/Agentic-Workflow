# W4.2 — Reflexion ↔ Retriever Binding

**Plan**: `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Wave/Phase**: W4.2
**Date**: 2026-04-24
**Status**: Spec — implementation deferred
**Relates-to**: ADR-060 (CRAG/Self-RAG loop), `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py`
**Tier**: T2 (spec, no code changes)

---

## 1. The Question

The repo already operates a **Reflexion engine** at L3
(`reflexion_engine.py`, `reflexion_types.py`) — a verbal-RL pattern that
reflects on agent task outcomes and adjusts subsequent attempts. ADR-060
introduces a **retrieval-scoped reflective loop** at L1. The question:
how do these relate without conflating layers, duplicating code, or
violating layer gravity?

## 2. The Two Reflexions Are Different

| Dimension | L3 Reflexion (existing) | L1 Retrieval Reflexion (ADR-060, new) |
|---|---|---|
| **Layer** | L3 orchestration | L1 cognition |
| **Reflects on** | Agent task outcome (did the plan succeed?) | Chunk relevance (does this evidence answer the query?) |
| **Trigger** | Task completion / failure / partial success | Each retrieval pass within a single query |
| **Loop horizon** | Episode-scoped (multi-turn task) | Sub-query-scoped (≤ 3 iterations within one tool call) |
| **Expansion vocabulary** | Plan rewrites, alternate tool sequences | Query rewrites, graph hops, transform swaps |
| **Output shape** | Updated agent memory, next-attempt plan | Updated query, expansion strategy, abstain signal |
| **Determinism floor** | Idempotent agent state | Deterministic chunk scoring (cached) |

They are **structurally analogous**, **semantically distinct**. Treating
them as one would force L1 retrieval to depend on L3 orchestration —
violating layer gravity (L1 may not import from L3).

## 3. Binding Contract

The two reflexions share **only** the data shape, not the executor:

```
agentic_core/runtime/types/reflection_types.py    (lives below both)
    @dataclass
    class ReflectionTrace:
        iteration: int
        evidence_in: <T>
        verdict: ReflectionVerdict
        rationale: str
        next_action: ReflectionNextAction | None
        emitted_at: datetime

    class ReflectionVerdict(Enum):    # shared enum
        ACCEPT
        REVISE
        ABORT

    class ReflectionNextAction(Enum):
        REWRITE_QUERY    # L1 retrieval scope
        GRAPH_HOP        # L1 retrieval scope
        TRANSFORM_SWAP   # L1 retrieval scope
        REPLAN           # L3 orchestration scope
        RETRY_TOOL       # L3 orchestration scope
        ABSTAIN          # both scopes
```

`reflection_types.py` lives at `agentic_core/runtime/types/` (already a
dependency floor for both L1 and L3). Each reflexion engine instantiates
the dataclass with its own type bound for `evidence_in`:

- L3: `evidence_in = TaskOutcome`
- L1: `evidence_in = list[GradeVerdict]` (per ADR-060 §2)

## 4. Where the Code Lives

| Concern | Module | Layer |
|---|---|---|
| Shared dataclass + enums | `agentic_core/runtime/types/reflection_types.py` | runtime/types (sub-L0 floor) |
| L3 task-reflexion executor | `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py` (existing) | L3 |
| L1 retrieval-reflexion executor | `agentic_core/L1_cognition/reasoning/retrieval_reflexion.py` (new, ADR-060) | L1 |
| Retrieval grader (LLM-backed) | `agentic_core/L1_cognition/reasoning/retrieval_grader.py` (new, ADR-060) | L1 |
| Rolling memory of past reflections | Already in L3 reflexion; **NOT** in L1 (each retrieval pass is fresh) | — |

## 5. Why L1 Reflexion Has No Cross-Query Memory

The L3 reflexion engine accumulates lessons across attempts so the agent
gets smarter task-by-task. L1 retrieval reflexion deliberately **does
not** accumulate cross-query memory:

1. Cross-query learning belongs to the **embedding model + reranker
   training**, not to a query-time loop.
2. Carrying state across queries entangles cache invalidation with
   reflection state — a classical correctness trap.
3. Per-query reflection budget is already constrained (≤ 3 iters); a
   memory bank would create silent feedback loops on similar queries.

Per-corpus calibration (e.g. "this corpus benefits from step-back more
than HyDE") lives in the **W6.2 agentic router**, not here. The router
reads aggregated W5.3 telemetry and updates routing weights offline.

## 6. Determinism + Replay

Both reflexions emit `ReflectionTrace` records. A reflection's
`next_action` decision is reproducible from `(evidence_in, verdict,
grader_identity)` plus the tier in which it ran. ADR-060's grader cache
enforces this for L1; the L3 reflexion engine already has its own
checkpoint discipline.

Replay invariant: feeding identical `(query, corpus_snapshot,
grader_identity)` to the L1 retrieval reflexion produces an identical
sequence of `ReflectionTrace` records (modulo wall-clock fields).

## 7. Out of Scope for W4.2

- Implementing either reflexion executor — owned by ADR-060 (L1) and the
  existing L3 module (no change).
- Cross-layer reflection unification (one engine for both). Explicitly
  rejected per §2/§3.
- Hooking either reflexion into the runtime HITL exit-control plane
  (ADR-023) — separate concern.

## 8. Open Questions

1. Should `RETRY_TOOL` (currently L3-only) ever be a valid `next_action`
   for L1 retrieval reflexion when the failing component is a tool the
   retriever invoked (e.g. ADG MCP unavailable)? **Tentative no** —
   L1 should signal upward, not retry tools itself. Confirm during
   ADR-060 implementation.
2. Should the dataclass live one level lower in `agentic_core/__init__`
   adjacent to constitutional invariants? Not necessary at v1 since
   `runtime/types/` is already a clean floor.

## 9. Acceptance

This binding is accepted when:
1. `agentic_core/runtime/types/reflection_types.py` exists with the
   shared dataclass + enums.
2. ADR-060 is accepted and `retrieval_reflexion.py` consumes the shape.
3. The existing L3 `reflexion_engine.py` is refactored to use the same
   shape (one-line type-bind change; no behaviour change). CI-gate
   `check_layer_gravity.py` confirms L1 → L3 imports remain forbidden.

## 10. References

- ADR-060 — CRAG/Self-RAG retrieval loop
- `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py`
- `agentic_core/L3_orchestration/types/reflexion_types.py`
- Constitutional rule: `boundary-enforcement.md` (layer gravity)
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
