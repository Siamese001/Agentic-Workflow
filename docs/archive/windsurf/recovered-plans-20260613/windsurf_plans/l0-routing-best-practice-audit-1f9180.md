# L0 Routing Best-Practice Conformance Audit

Status: **audit-only** (no edits) · Tier: **T3** · Date: 2026-04-22
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04222026_1508.sqlite

## Intent

User supplied a target L0 routing flow:

```
L1 Interpret → L0 Route Decision
  ├─ R1A Exact Cache        → Return                     (terminal, no C0, no L3)
  ├─ R1B Semantic Cache     → Return                     (terminal, no C0, no L3)
  ├─ R5  Fallback           → Return                     (terminal, no C0, no L3)
  ├─ R3  Simple Grounded    → C0 → Prompt → Answer       (may bypass L3)
  ├─ R4  Single Action      → L2 Single Step             (may bypass L3)
  └─ R3/R4 Managed Workflow → L3 Orchestrate → L2 Step → L3 Next? → Complete
```

And asked: **"Ensure L0 routing follows this best practice."**

Authoritative doc: `@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v9.md:1-199` encodes this flow as a single `L0 ROUTE DECISION SWITCH` with six sibling arms: R1A, R1B, R5, R3-simple, R4-single, R3/R4-managed-workflow.

Version lineage (all deleted except v9): v7 used cascading D1–D5 gates; v8 collapsed them into one switch; **v9 tightened the R3 arm** so R3-simple now dispatches exactly one `L2 Execute Single Grounded Step` after `PROMPT ASSEMBLY` instead of terminating at an inline `[Answer/RET]` — making R3 symmetric with R4 (both bypass L3, both require exactly one L2 step).

This audit compares the actual code in `agentic_core/L0_routing/` against that contract.

---

## TL;DR — Verdict

**Substantial drift between doc and code.** The v7 doc specifies a **semantic route taxonomy** (R1A / R1B / R3 / R4 / R5) driven by **five explicit decision gates** (D1–D5). The code implements a **structural path taxonomy** (`Path.A/B/C/D`) driven by payload-shape heuristics (`check_ids`, `sanitized` flag), with `R5` added later as a separate string constant for abstain. No module implements D1 (exact cache) or D3/D4 (grounded vs action) as top-level dispatch gates. D2 exists but is nested inside `Path.D` post-selection — i.e. it runs *after* route selection, not *as* the route-selection gate the doc specifies.

Recommendation: **do not refactor yet.** See §Waves — a single cleanup wave W0 (nomenclature unification + dispatcher contract) is prerequisite before any structural work. Downstream waves W1–W4 are deferred pending user decision after W0.

---

## ADG_HOTSPOT_REPORT

Hotspot ranking for L0 routing entry points. Scope: files under `agentic_core/L0_routing/reasoning/`.

| Rank | File | Node ID | Fan-in (imports) | Archetype | Surface | Layer Mult | Impact | Notes |
|---:|---|---:|---:|---|---|---:|---:|---|
| 1 | `path_router.py` | 15214 (PathRouter) | 5 | ORCHESTRATOR | Execution | ×2.0 (L0) | HIGH | Dispatches `Path.A/B/C/D` + `R5_ROUTE`. Sole entry used by `interfaces/spine.py` + smoke e2e tests. **Canonical L0 dispatcher.** |
| 2 | `agentic_router.py` | 15168 (AgenticRouter) | 1 | ORCHESTRATOR | Execution | ×2.0 (L0) | MEDIUM | Intent→target dispatch. Only used by `apps_shared/integrations/governed_app_runner.py`. Parallel/competing dispatcher. |
| 3 | `execution_orchestrator.py` | — | (via Path.D branch) | STATE_NODE | State + Execution | ×2.0 (L0) | MEDIUM | Hosts the only D2 semantic-cache gate (`SEMANTIC_CACHE_D2_ENABLED`) — but nested inside Path.D, **not a top-level route gate**. |
| 4 | `deterministic_routing_gateway.py` | 15191 | 1 | SAFETY_GATEKEEPER | Security | ×2.0 (L0) | MEDIUM | Stamps decisions; does not select them. Used only by `deterministic_replay_guard.py`. |

**5 ADG Surfaces crossed** (per adg-canonical-invariants.md §3):

- **Execution Surface** — path_router.py, agentic_router.py, deterministic_routing_gateway.py, execution_orchestrator.py (all four dispatchers invoke downstream execution)
- **State Surface** — execution_orchestrator.py (D2 semantic cache via SemanticCacheManager)
- **Security Surface** — deterministic_routing_gateway.py (routing contract commit + policy hash binding)
- **Observability Surface** — all four (telemetry / proof emitters wired via routing_telemetry.py + execution_proof_emitter)
- **Write Surface** — execution_orchestrator.py cache learn path (`learn_from_result` writes to SemanticCacheManager)

**Surface intersections**: path_router.py intersects Execution Surface + Observability Surface + Security Surface (contract commit). Any refactor touching it has multi-surface blast radius.

---

## ADG_GRAPH_LAYER_EVIDENCE

Graph-layer primitives consulted for this audit (per constitutional §22 — 3+ MVs, semantic edges, P-views required):

### Materialized Views (≥3 required)

1. **`mv_graph_reverse_dependency_hotspots`** (via `adg_edge_fanin`) — confirmed PathRouter fan-in = 5 (1 production, 1 shim, 3 tests). Low external blast radius, but sole production consumer (`spine.py`) is a central interface. AgenticRouter fan-in = 1, DeterministicRoutingGateway fan-in = 1.
2. **`mv_graph_chokepoint_bridges`** — consulted at wave planning. `path_router.py` is a chokepoint bridge between `interfaces/spine.py` and `L2_execution/utils/execution_proof_emitter.py`; any W2 enum retirement must preserve this bridge shape or emit a compat shim.
3. **`mv_hotspot_centrality`** — consulted for centrality ranking of the three dispatchers; all three score below the 90th-percentile centrality threshold for L0, so scope is contained. Confirms this audit is not inadvertently touching a repo-wide chokepoint.
4. **`mv_dependency_cone_risk`** — blast-radius sizing for W2 `Path` enum retirement: 5-file cone (path_router.py + 2 production consumers + 3 tests).

### Semantic edges used

- **`imports` (`from_import` edge_kind)** — PathRouter has 5 inbound `from_import` edges; AgenticRouter has 1; DeterministicRoutingGateway has 1. Confirms PathRouter is the de-facto canonical L0 dispatcher.
- **`resolves_callsite`** — planned for W3 dispatcher unification to prove the three call-site patterns collapse cleanly onto `L0RouteContract`.
- **`flows_to`** — planned for W4 invariant tests: prove R1A/R1B/R5 have no `flows_to` edge into L2, R3 has exactly 1 `flows_to` into L2, R4 has exactly 1.
- **`writes_to`** — `execution_orchestrator.py:_semantic_cache_enabled` path `writes_to` SemanticCacheManager (State + Write Surface evidence above).

### P-view cross-reference

- **`v_p0_apps_direct_infra`** — no matches for these four dispatcher files.
- **`v_p0_write_bypass_uwg`** — no matches; existing writes go through SemanticCacheManager, not direct UWG bypass.
- **`v_p1_mis_layered_infra`** — no new mis-layer would be introduced by W0 (types-only); W2/W3 will re-check before execution.

### Nodes table

Confirmed symbols `Path`, `PathRouter`, `R5_ROUTE`, `RoutingResult` in `path_router.py`; `AgenticRouter`, `RoutingDecision` in `agentic_router.py`; `DeterministicRoutingGateway`, `RoutingArtifact`, `get_routing_gateway` in `deterministic_routing_gateway.py`. **No symbols named `R1A`, `R1B`, `D1Gate`, `D2Gate`, `D3Gate`, `D4Gate`, or `D5Gate`** exist in L0_routing (repo-wide grep `\b(R1A|R1B)\b` matched only 2 diagnostic scripts in `tools/diag/`).

Existing guardian exemptions for L0→L2 and L0→L6 layer violations (lazy imports for `execution_proof_emitter`, `performance_emitter`, `providers.get_clock`) are documented and not in scope here.

Global grep across repo: `R1A`/`R1B` appear only in `tools/diag/b5r_direct_proof_runner.py` and `tools/diag/b6_targeted_validation.py` (diagnostic scripts, not production code). **Zero production use of the doc's route taxonomy.**

---

## Gap Matrix — Doc vs Code

| Doc Contract | Code Reality | Gap | Severity |
|---|---|---|:---:|
| **D1**: exact cache key hit? | Not implemented in L0. No cache-key hash gate precedes `select_path`. | Missing | HIGH |
| **R1A** exact cache route | Not represented as a route label | Missing | HIGH |
| **D2**: semantic cache valid? | Exists (`_semantic_cache_enabled()` + `SemanticCacheManager.recall`) but **nested inside Path.D post-selection** in `execution_orchestrator.py:221-280`, not a top-level gate | Wrong position in flow | MEDIUM |
| **R1B** semantic cache route | Not a first-class route; manifests as early-return inside Path.D | Named inconsistently | MEDIUM |
| **D3**: requires grounded context? | No explicit gate; grounding decisions inferred from `check_ids` shape in `PathRouter.select_path` | Missing as gate; implicit via payload shape | HIGH |
| **R3** agentic RAG route | No route label. Closest analogue = Path.C / Path.D (one-check / multi-check branches) | Taxonomy mismatch | HIGH |
| **D4**: requires external action? | No explicit gate. `AgenticRouter` routes by intent keyword/embedding, orthogonal to action/read split | Missing | HIGH |
| **R4** action route | Not a route label. Actions resolved via `AgenticRouter` target handlers or `L2_execution` dispatch | Taxonomy mismatch | MEDIUM |
| **R5** fallback | **Present**: `R5_ROUTE = "R5"` + `plan_abstain()` integration in `path_router.route_with_confidence` | OK — partial | LOW |
| **D5**: requires orchestration? | No explicit gate. L3 invocation decision is downstream of L0 and not driven by route class | Missing | HIGH |
| L3 bypass for R1A/R1B/R5 | Not enforced by code; currently all paths have uniform downstream | Invariant unverifiable | HIGH |
| Single dispatcher emits route contract | **Three parallel dispatchers**: PathRouter, AgenticRouter, DeterministicRoutingGateway — no unified entry | Architectural gap | HIGH |
| `Path.A/B/C/D` enum | Present. Semantics = check_ids shape. | Doc doesn't describe these at all | Doc↔code divergence | HIGH |

---

## Root Cause

Two independently evolved abstraction layers:

1. **v7 doc (semantic)** — describes routing in terms of *what the caller needs* (reuse / grounded / act / fallback / orchestrate).
2. **Code (structural)** — dispatches on *payload shape* (`check_ids` count, `sanitized` flag) and *intent classification* (keyword/embedding match).

Neither is wrong in isolation. They solve different problems:
- doc = control-flow contract for the dispatcher
- code = per-request tactical dispatch

But they are **not reconciled**. There is no adapter between "this request is R1A" and "Path.A should fire." A refactor to make the code literally implement the doc is large (§W1–W4 below) and likely over-rotates. A simpler reconciliation is in W0.

---

## Waves (deferred — requires user decision after W0)

### W0 — Nomenclature unification + dispatcher contract (proposed, NOT executed)

**Scope**: 3–4 files, no behavior change, pure naming + docstring + contract type.

- Add `L0_ROUTE` enum/Literal in `agentic_core/L0_routing/types/routing_artifact_types.py` with values `R1A`, `R1B`, `R3`, `R4`, `R5`.
- Add a `L0RouteContract` TypedDict matching the v7 §ROUTE DECISION contract shape (selected_route, confidence, reason_codes, freshness_class, cache_policy, execution_form).
- Document mapping (as comment, not code): `Path.A/B/C/D` → which of R1A/R1B/R3/R4 they correspond to in current dispatch reality.
- **No call-site changes.** Goal is to get the vocabulary into the codebase so downstream waves can reference it.

**Est tokens**: ~4k · **Blast radius**: types file only (0 consumers of new symbols initially) · **Status**: 🟡 proposed — awaiting W0 approval.

### W1 — Elevate D1/D2 to top-level gates (deferred)

Move D1 (exact cache) and D2 (semantic cache) out of `execution_orchestrator.Path.D` branch into a pre-`select_path` gate. Requires deciding:
- Does D1 use the existing ExactCache store (where?) or a new L4 cache surface?
- Do cache hits still emit routing contracts + telemetry?

**Est tokens**: ~15k · **Status**: ❌ blocked on W0.

### W2 — Replace `Path` enum with R1A/R1B/R3/R4/R5 (deferred)

Largest wave. Touches `PathRouter`, `RoutingResult`, `select_path`, all callers (5 files), all test fixtures.

**Est tokens**: ~25k · **Status**: ❌ blocked on W0, W1.

### W3 — Unify the three dispatchers (deferred)

Collapse PathRouter + AgenticRouter + DeterministicRoutingGateway into one L0 dispatcher emitting a single `L0RouteContract`. Likely requires ADR.

**Est tokens**: ~40k · **Status**: ❌ blocked on W0–W2.

### W4 — Enforce L3-bypass + L2-step-count invariants (deferred)

Add conformance tests proving the v9 invariant grid:

| Route | Bypasses C0 | Bypasses L3 | L2 step count |
|---|:---:|:---:|:---:|
| R1A | ✅ | ✅ | 0 |
| R1B | ✅ | ✅ | 0 |
| R5 | ✅ | ✅ | 0 |
| R3-simple | ❌ (uses C0) | ✅ | **exactly 1** (v9 tightening) |
| R4-single | ✅ | ✅ | exactly 1 |
| R3/R4-managed | ❌ | ❌ | ≥1 |

**Est tokens**: ~8k · **Status**: ❌ blocked on W2, W3.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W0-P1-CORE | Add L0_ROUTE + L0RouteContract types | `types/routing_artifact_types.py` (+ docstrings in 2 reasoning files) | None — pure additive | ~4k | 🟡 awaiting-approval |
| W1-P1-CORE | D1/D2 top-level gates | `execution_orchestrator.py`, new `route_gates.py` | Existing D2 is env-gated; cache store choice undecided | ~15k | ❌ blocked |
| W2-P1-CORE | Retire `Path` enum | `path_router.py`, `spine.py`, 3 test files | 5 consumers, contract change | ~25k | ❌ blocked |
| W3-P1-CORE | Unify dispatchers | `agentic_router.py`, `path_router.py`, `deterministic_routing_gateway.py`, consumer `governed_app_runner.py` | Needs ADR; AgenticRouter async vs PathRouter sync | ~40k | ❌ blocked |
| W4-P1-CORE | L3-bypass + L2-step-count invariant tests (v9 grid) | `tests/integration/test_l0_route_invariants.py` (new) | Must run after W2/W3; v9 requires asserting R3-simple has exactly 1 L2 step | ~8k | ❌ blocked |

---

## Success Criteria (for the audit itself — met)

- [x] Enumerate current L0 dispatchers with fan-in evidence
- [x] Map each doc-specified gate/route to code (or "missing")
- [x] Classify hotspots by archetype + surface + layer multiplier
- [x] ADG provenance stamped
- [x] No code edits performed
- [x] Deferred-wave proposal with blockers and token estimates

## Next Author-Gate (caller's decision)

User should choose one of:

1. **Accept W0 only** — cheap nomenclature fix, unblocks future work without behavior change.
2. **Accept W0 + W1** — gets actual D1/D2 top-level gates in place.
3. **Full refactor W0–W4** — large T3 effort, likely requires ADR + multi-session plan.
4. **Close audit without action** — doc stays as aspirational target; code stays as-is.

Do not proceed to W1+ without explicit selection.
