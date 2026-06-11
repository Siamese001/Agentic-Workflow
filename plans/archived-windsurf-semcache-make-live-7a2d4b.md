---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\semcache-make-live-7a2d4b.md'
original_relative_path: 'semcache-make-live-7a2d4b.md'
source_sha256: e5a7f113d3c11ee174d9389dcd1abfe3cffc105c92359cc1a2652ffb83946a18
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Make Semantic Cache Fully Operational During L0 Routing

- **Plan ID**: `semcache-make-live-7a2d4b`
- **Tier**: T3 (cross-layer L0→L4, state mutation, observability, multi-file)
- **Status**: EXECUTED 2026-04-22 — all 6 waves complete; probe reports `operational=True`; integration tests 2/2 PASS.
- **ADG Snapshot**: `adg_indexed_04222026_0441.sqlite` (71,790 nodes / 541,959 edges; Redis healthy)
- **Baseline Evidence** (from prior diagnosis response):
  - `data/cache/gptcache/gptcache.db`: 5 tables, **0 rows** (legacy, unused path)
  - Redis: **0** runtime keys matching `semcache:*`, `sovereign:*`, `l2:*`, `memory:*`
  - `SEMANTIC_CACHE_D2_ENABLED`: **unset** → flag closed, `_init_gptcache()` short-circuits
  - L0 `execution_orchestrator.py:217` gate never fires; no `learn()` call anywhere in L0

---

## Intent

Transition the semantic cache from "wired but dormant" to "fully operational" on the L0 Path-D flow:

1. **Write path live**: Every successful L0 Path-D execution populates L1 (Redis, 24h) and, on feedback-gated success, promotes to L2 (SQLite scalar + ChromaDB vector, 7d).
2. **Read path live**: L0 `execute()` queries L1 first (O(1) Redis), falls through to L2 (cosine ≥0.95 over BGE-M3 embeddings); on L2 hit, L1 is warmed so subsequent hits stay O(1).
3. **Persistent store → Redis projection**: On process start / singleton init, a bounded warmup loads hot L2 rows into Redis so cold-start recall is fast.
4. **Proven end-to-end**: Integration test shows miss→learn→hit cycle; Redis keys + SQLite rows + Chroma vectors all observable.

---

## ADG_HOTSPOT_REPORT

Hotspots ranked by `violations × (1 + log10(1 + fan_in)) × layer_multiplier`. Fan-in drawn from `adg_edge_fanin(imports)`; archetypes classified per canonical invariants §5.

| Rank | Module | Layer | Mult | Fan-in | Archetype | Surfaces Crossed | Why a hotspot for this wave |
|---|---|---|---|---|---|---|---|
| 1 | `agentic_core/L0_routing/reasoning/execution_orchestrator.py` | L0 | ×2.0 | lazy/dynamic (0 static) | ORCHESTRATOR | Execution Surface, State Surface, Observability Surface | Sole L0 hit-path into cache; miss-path must also call `learn()`. Edits here are highest-blast. |
| 2 | `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | L4 | ×1.75 | 0 (lazy imports only) | STATE_NODE | Write Surface, State Surface | Canonical L1+L2 facade. No new semantics — only plumbing (warmup + namespace ownership). |
| 3 | `agentic_core/L4_state/cache/gptcache_client.py` | L4 | ×1.75 | 0 (lazy) | STATE_NODE | Write Surface, State Surface | `NativePersistentCacheClient` is L2 SSOT; read path already sound, need stats exposure. |
| 4 | `apps_shared/enforcement/GlobalcacheStrategy.py` | L_APP | ×1.0 | 0 | STATE_NODE | State Surface | L1 LRU wrapper; not required for Path-D flow, out of scope. |
| 5 | `agentic_core/L0_routing/utils/elevator_shaft_seam.py` | L0 | ×2.0 | — | CENTRAL_DEPENDENCY | Execution Surface | JIT context loader already calls `get_semantic_cache().query()`; out of scope for write path (read-only, tolerant of miss). |

**Surfaces crossed** (per canonical invariants §3): the write path intersects **Execution** (L0 path dispatch), **State** (Redis+SQLite+Chroma), and **Observability** (Prometheus metrics, lifecycle_trace_contract emitters). Requires intersection-aware testing.

**ADG Provenance**: backend=sqlite, snapshot=`adg_indexed_04222026_0441.sqlite`.

---

## ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22: evidence from materialized views, semantic edges, and P-views — not raw `edges`.

### Materialized views consulted

| MV | Why used | Outcome for this plan |
|---|---|---|
| `mv_graph_reverse_dependency_hotspots` | Detect cache modules with high fan-in that would amplify a bad change | Cache modules have **low** static fan-in (all lazy imports). Blast radius for edits is bounded. |
| `mv_graph_chokepoint_bridges` | Identify L0↔L4 bridges that must remain unbroken | `execution_orchestrator.execute` and `semantic_cache_manager.recall/learn` are the chokepoints — edits preserve signatures. |
| `mv_dependency_cone_risk` | Downstream cone risk for L0 edits | L0 change scope limited to 1 new call inside `execute()`; cone risk LOW. |

### Semantic edges used

- `flows_to`: `execute()` → `SemanticCacheManager.recall()` (already present at `execution_orchestrator.py:225`) — new edge to add: `execute()` → `SemanticCacheManager.learn()` on post-success miss.
- `reads_from` / `writes_to`: `SemanticCacheManager` → Redis (namespace `memory:*`), `NativePersistentCacheClient` → SQLite `l2_cache.db` + Chroma `l2_semantic_cache`.
- `emits_side_effect`: `learn()` and `promote_to_long_term()` write persistent state; each is already instrumented via `_emit_writes_observability_log` and `_record_semantic_cache_prom_event`.
- `resolves_callsite`: the D2 gate at `execution_orchestrator.py:217-244` resolves to the L4 singleton via lazy import — same resolution pattern reused for the learn-path.

### P-view cross-references

- `v_p0_apps_direct_infra`: No new matches introduced — L0 continues to use lazy imports of L4, preserving boundary discipline.
- `v_p0_write_bypass_uwg`: New state writes flow through `SemanticCacheManager` (authorized state node), not direct Redis/SQLite. No UWG bypass.
- `v_p1_mis_layered_infra`: No cross-layer static imports added. Only runtime imports inside `try`.
- `v_p2_duplicated_adapters`: `NativePersistentCacheClient` already SSOT; no new adapter.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| **W0** | P0.1 | Baseline capture + flag enablement + disk layout verification | 🟢 ~4k | todo | `SEMANTIC_CACHE_D2_ENABLED=1` active in `.env`; `artifacts/gptcache/` provisioned; pre-change Redis/SQLite state snapshot recorded. |
| **W1** | P1.1, P1.2 | **Write path live**: L0 emits `learn()` on Path-D miss-then-success | 🟡 ~10k | todo | After one L0 Path-D execution, Redis key `memory:<hash>` exists with 24h TTL and enriched payload JSON. |
| **W2** | P2.1, P2.2 | **L2 persistence + Redis warmup on init**: promote-on-feedback + warmup loader | 🟡 ~10k | todo | After a feedback-scored execution, `l2_cache.db` gains a row, Chroma `l2_semantic_cache` gains a vector, and `SemanticCacheManager._initialize()` warms top-N L2 rows into Redis. |
| **W3** | P3.1 | **Observability exposure**: metrics surface for `l1_hit/l2_hit/miss/store/promote` via existing Prometheus rules | 🟢 ~4k | todo | Metrics counters increment visibly; `SemanticCacheManager.stats` readable from a diagnostic tool. |
| **W4** | P4.1 | **End-to-end integration test**: two-shot miss→learn→hit proof | 🟡 ~8k | todo | New test in `tests/integration/cache/test_l0_d2_semantic_cache_live.py` passes; asserts L1 key, L2 row, L2 vector, second-call hit. |
| **W5** | P5.1 | **Verification**: ADG regen, targeted pytest, runbook update | 🟢 ~5k | todo | ADG snapshot refreshed; no new P0/P1/P2 violations introduced; runbook `docs/runbooks/d2_semantic_cache_production_rollout.md` updated. |

**Token budget** (via `ContextWindowEstimator`): total ≈ 41k tokens across 6 waves. All waves 🟢 or 🟡 — no 🔴.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Baseline + flag | `.env`, `artifacts/gptcache/.gitkeep` | Flag wiring; confirm `.env` is honored by runtime. | 4k | todo |
| P1.1 | L0 learn wiring | `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/execution_orchestrator.py` | Must call `learn()` only on true miss + successful downstream path; avoid writing on routing errors or replay. | 6k | todo |
| P1.2 | Payload contract | `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/execution_orchestrator.py`, `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | Namespace derivation + result payload must survive `repr(payload)` hashing and `sanitizer.sanitize()`. | 4k | todo |
| P2.1 | Promote path | `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/execution_orchestrator.py`, `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | `promote_to_long_term` is `async` — need sync wrapper or `asyncio.run` guard; requires `evidence_ids` + `grounding_complete=True`. | 6k | todo |
| P2.2 | Redis warmup on singleton init | `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | Bounded warmup (top-N=256 by recency) to avoid init storm; must not block import. | 4k | todo |
| P3.1 | Metrics exposure | `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/semantic_cache_manager.py`, `@c:/Git/Agentic-Workflow/tools/diag/probe_semantic_cache.py` (new) | Use existing `_record_semantic_cache_prom_event` helper (already invoked); add a probe CLI that dumps `stats` + Redis keyspace. | 4k | todo |
| P4.1 | End-to-end test | `@c:/Git/Agentic-Workflow/tests/integration/cache/test_l0_d2_semantic_cache_live.py` (new) | Needs real Redis + Chroma; marked `@pytest.mark.integration`; skip only when infra absent with `strict=True` style guard. | 8k | todo |
| P5.1 | Verify + runbook | `@c:/Git/Agentic-Workflow/docs/runbooks/d2_semantic_cache_production_rollout.md`, `tools/generate_full_adg.py` | Re-run burndown; confirm no new violations; document `SEMANTIC_CACHE_D2_ENABLED=1` production rollout steps. | 5k | todo |

---

## Gap Register

| ID | Gap | Severity | Closes In |
|---|---|---|---|
| G1 | `SEMANTIC_CACHE_D2_ENABLED` unset → whole cache stack inert | **P0** | W0 |
| G2 | L0 never calls `learn()` → nothing ever written | **P0** | W1 |
| G3 | `promote_to_long_term` never invoked → L2 permanently empty | **P1** | W2 |
| G4 | L2-hit does not write back into L1 → repeated cold reads | **P1** | W2 |
| G5 | No Redis warmup on init → cold start paradox | **P2** | W2 |
| G6 | No integration test proving end-to-end | **P1** | W4 |
| G7 | No runbook for enabling in production | **P2** | W5 |

---

## Rollback Checkpoints

Each wave has a single explicit rollback:

- **W0**: Unset flag in `.env`. (No code change.)
- **W1**: Revert `execution_orchestrator.py` to pre-W1 commit; flag remains on but inert.
- **W2**: Skip promote block via a nested flag `SEMANTIC_CACHE_PROMOTE_ENABLED` (default off during ramp).
- **W3**: Metrics are additive; no rollback needed.
- **W4**: Test can be skipped via `@pytest.mark.skipif(not_integration_env, ...)`.
- **W5**: Docs-only; no runtime rollback.

---

## Verification

- **ADG regen after W4** — must show zero new P0/P1 violations; snapshot diffs recorded under `docs/reports/plans/semcache-make-live-7a2d4b/`.
- **Redis direct inspection** via `mcp9_redis_keys pattern=memory:*` — expect ≥1 key after test run.
- **SQLite direct inspection** of `artifacts/gptcache/l2_cache.db` — expect ≥1 row in promote path.
- **Chroma direct inspection** of `artifacts/gptcache/chroma/` — expect ≥1 vector in `l2_semantic_cache` collection.
- **Pytest scope**: `tests/integration/cache/test_l0_d2_semantic_cache_live.py` + `tests/unit/agentic_core/L0_routing/reasoning/test_execution_orchestrator_d2.py` (add if missing).

---

## Out of Scope (explicitly)

- `elevator_shaft_seam.py` context-JIT path — read-only, already tolerant of empty cache; no edit needed for "fully operational" on the Path-D flow.
- `SovereignSemanticCache` (mission-isolated file-AST cache) — different use case (repo file caching), not the L0 query cache.
- `apps_shared/enforcement/GlobalcacheStrategy.py` — delegates to the same `SemanticCacheManager` singleton; no extra wiring required.
