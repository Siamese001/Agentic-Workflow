---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-adg-acceleration-b4f2a1.md'
original_relative_path: 'runtime-adg-acceleration-b4f2a1.md'
source_sha256: 9de28a8e66862e119d2745e1ad3d19a633d82b6d5648dcdc96d97f7a740e0e6a
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime ADG Acceleration — T3 Execution Plan

> Slug: `runtime-adg-acceleration-b4f2a1`
> Status: **All Waves Complete (W5 phase-1: incremental single-file reindexer delivered; watcher daemon deferred to own ADR)**
> Tier: **T3** (cross-layer: tools/, agentic_core/L0, L5, L6; touches runtime hot path)
> ADG Snapshot: `artifacts/adg/adg_indexed_04242026_0721.sqlite` (healthy; 150k imports, 109k reads_from, 68k flows_to, 57k resolves_callsite edges)
> Origin: User request 2026-04-24 11:20 UTC — "map into prioritized plan and implement each wave"
> Source analysis: Cascade response 2026-04-24 10:57 UTC (10 opportunities for runtime graph-DB-over-SQLite acceleration)

## Intent

Push the ADG from a design-time asset (refactoring, CI gates, plans) onto the **runtime hot path** so the graph-layer-over-SQLite substrate accelerates live routing, observability, and decisioning. Deliver enablers first, then high-leverage integrations.

## ADG_HOTSPOT_REPORT

Ranked target surfaces this plan enables downstream consumers to act on. Each row cites the hotspot archetype (doctrine §5) and the ADG Surface intersections (doctrine §3) the runtime signal touches.

| Rank | Target (ADG consumer) | Archetype | Fan-in (approx) | Layer Mult | Surface(s) | Impact Score | Rationale |
|-----:|-----------------------|-----------|----------------:|-----------:|------------|-------------:|-----------|
| 1 | `agentic_core/L0_routing/*` via `adg_risk_signal` | CENTRAL_DEPENDENCY | 30+ | 2.0 | Execution Surface, Security Surface | 90 | L0 router is the primary entry point; risk envelope gates every dispatch. Wave W2. |
| 2 | `agentic_core/L5_safety/enforcement/*` via `adg_hitl_enricher` | SAFETY_GATEKEEPER | 15+ | 2.0 | Security Surface, Write Surface | 75 | HITL packets on the exit-control path; enrichment shortens reviewer decision latency. Wave W4. |
| 3 | `agentic_core/L6_observability/*` via `adg_span_annotator` | ORCHESTRATOR | 20+ | 0.75 | Observability Surface, State Surface | 35 | Every emitted span becomes an ADG-vs-runtime drift signal. Wave W7. |
| 4 | `tools/adg/causal_chain.py` consumers (CLI + agents) | CENTRAL_DEPENDENCY | 10+ | 1.0 | Observability Surface, Execution Surface | 25 | Bridges static/runtime ADG + refactor_outcome ledger; single highest-leverage diagnostic feature. Wave W3. |
| 5 | pytest collection via `tools/adg/select_tests.py` | ORCHESTRATOR | 5+ | 1.0 | Execution Surface | 15 | ADG-driven test subsetting; converts CI-only triage into edit-time feedback. Wave W6. |

Impact formula applied: `impact ≈ fan_in × (1 + log10(1 + fan_in)) × layer_multiplier` per doctrine §6. Ranking drives execution order (W1 enabler first, then W2/W4 high-impact, then W3, then W6/W7).

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views that become runtime signal sources**:
- `mv_graph_critical_path_blast_radius` — per-node criticality + downstream blast
- `mv_graph_reverse_dependency_hotspots` — fan-in centrality (router signal)
- `mv_hotspot_centrality` — betweenness approximation (chokepoint detection)
- `mv_dependency_cone_risk` — scoped risk envelope for a file/symbol
- `mv_high_fan_in_out_with_defects` — hotspot × defect join (HITL enrichment)
- `mv_path_criticality_rollup` — L×L criticality (policy plane inputs)
- `mv_graph_chokepoint_bridges` — circuit-breaker candidates

**Semantic edges driving runtime queries**:
- `flows_to` (68k edges) — backward walk from failing span → swallow site
- `resolves_callsite` (57k) — join OTel span → static node
- `writes_to` (4.5k) + `emits_side_effect` (31k) — expected-effects check vs observed
- `controls_flow` (54k) — HITL packet enrichment (guard context)

**P-views relevant to policy plane**:
- `v_p0_write_bypass_uwg`, `v_p0_provider_bypass` — runtime guardrail refusal set
- `v_p1_raw_http_outside_seam` — egress policy tightening
- `mv_exemptions_near_critical_paths` — dynamic exemption scrutiny

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| W1 | W1.1–W1.3 | Runtime ADG Query Library (enabler) | 8000 | 🟡 In Progress | Library importable from L0/L5/L6; sub-10ms median query; unit tests pass |
| W2 | W2.1–W2.2 | Router risk-signal adapter (L0) | 4000 | 🔴 Todo | `risk_envelope(symbol)` returns structured band usable by routers; non-breaking |
| W3 | W3.1–W3.3 | Causal chain "why" tool | 7000 | 🔴 Todo | Given `trace_id`, returns ranked cause chain (span→node→swallow site→precedent) |
| W4 | W4.1 | HITL packet enrichment helper | 3000 | 🔴 Todo | Adds archetype + upstream callers + surface intersections to L5 packets |
| W5 | W5.1–W5.2 | Incremental MV refresh + file watcher | 12000 | 🔴 Todo | Edited-file re-parse + MV patch < 2s; Redis projection live |
| W6 | W6.1 | Live test-selection runtime hook | 4000 | 🔴 Todo | `select_tests_for(changed_files)` via fan-in closure; integrates with pytest MCP |
| W7 | W7.1 | Semantic-edge × OTel observability join | 5000 | 🔴 Todo | Span annotator tags `expected_writes_to` delta vs observed; anomaly surfaces |

**Total**: ~43k tokens estimated; waves W1–W4 are the "phase 1 innovation unlock" (22k). W5 is the highest-leverage standalone wave. W6/W7 depend on W1 being stable.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | Query library core | `tools/adg/runtime_query.py` (new) | SQLite thread-safety; MCP already flakes on thread boundary | 4000 | 🟡 In Progress |
| W1.2 | Snapshot resolver | extend `tools/adg/runtime_query.py` | Must pick latest `adg_indexed_*.sqlite` deterministically | 1500 | 🔴 Todo |
| W1.3 | Unit tests | `tests/unit/tools/adg/test_runtime_query.py` (new) | Needs real snapshot; use mark=integration for DB-dependent | 2500 | 🔴 Todo |
| W2.1 | L0 risk-signal adapter | `agentic_core/L0_routing/utils/adg_risk_signal.py` (new) | Must not import MCP client (sync path) | 2500 | 🔴 Todo |
| W2.2 | L0 adapter tests | `tests/unit/agentic_core/L0_routing/test_adg_risk_signal.py` (new) | Mock the query library; no real DB dependency | 1500 | 🔴 Todo |
| W3.1 | Causal chain core | `tools/adg/causal_chain.py` (new) | Needs flows_to reverse traversal + antipattern lookup | 3500 | 🔴 Todo |
| W3.2 | Ledger precedent join | same file (extend) | Reads from `artifacts/ledgers/refactor_outcome*.sqlite` | 1500 | 🔴 Todo |
| W3.3 | CLI + tests | CLI under same file; `tests/unit/tools/adg/test_causal_chain.py` | CLI must honor progress bar rule | 2000 | 🔴 Todo |
| W4.1 | HITL enricher | `agentic_core/L5_safety/enforcement/adg_hitl_enricher.py` (new) + test | Pure function, no MCP dependency | 3000 | 🔴 Todo |
| W5.1 | Incremental reindex library | `tools/adg/incremental/` (new package) | AST re-parse single file + MV patch is non-trivial | 8000 | 🔴 Todo |
| W5.2 | File watcher daemon + Redis push | `tools/adg/incremental/watcher.py` | Needs debounce + lock coordination | 4000 | 🔴 Todo |
| W6.1 | Test-selection runtime hook | `tools/adg/select_tests.py` (new) | Fan-in closure over `imports` + `calls` edges | 4000 | 🔴 Todo |
| W7.1 | Span annotator | `agentic_core/L6_observability/adg_span_annotator.py` (new) | Joins OTel span attrs with static `writes_to` | 5000 | 🔴 Todo |

## Gap Register

| # | Gap | Mitigation |
|---|-----|------------|
| G1 | MCP ADG server currently returns SQLite thread error | Library uses direct sqlite3 with per-call connection; no MCP dependency at runtime |
| G2 | No existing runtime-facing ADG read API | This plan delivers it (W1) |
| G3 | Static snapshot drift vs live code | W5 delivers incremental refresh; until then, library exposes snapshot timestamp so callers can decide freshness |
| G4 | Redis hot-cache may be cold on fresh sessions | Library falls back to SQLite; Redis is optimization not dependency |
| G5 | Some proposed MVs may not exist yet | W1 only uses verified MVs (see ADG_GRAPH_LAYER_EVIDENCE above — all confirmed present in snapshot) |

## Execution Order & Prioritization Rationale

**#1 — W1 (enabler)**: nothing else works without a fast, thread-safe, process-local query library. MCP is the wrong tool for hot-path reads (serialization rule §26 + observed thread bug). Direct SQLite = zero hop, sub-10ms.

**#2 — W2 + W4 (lightweight integrations)**: tiny adapters proving the library delivers value; no architectural churn.

**#3 — W3 (causal chain)**: highest single-feature leverage once W1 stable. Bridges static ADG + runtime ADG + decision ledgers — pure innovation.

**#4 — W5 (incremental refresh)**: transformational but most complex. Deferred to second batch.

**#5 — W6, W7**: builds on all prior waves; natural extensions.

## Non-Goals / Rejected Alternatives

- ❌ Introducing Neo4j, KuzuDB, or DuckPGQ — violates doctrine (SQLite + MV overlay is sufficient at our scale).
- ❌ Exposing raw `nodes`/`edges` queries to runtime callers — MVs and typed helpers are the API.
- ❌ Caching MVs in Redis without snapshot-ID keying — staleness corrupts runtime signals.
- ❌ Making L0/L5 take a hard dependency on the runtime ADG MCP — must stay direct-SQLite.

## Verification Protocol

Per wave:
1. `py_compile` on every touched file
2. Unit tests `pytest tests/unit/<scope>` (no skips, no xfail without strict=True)
3. Import smoke test from a clean Python invocation
4. For W1: benchmark median query time (target p50 < 10ms, p99 < 50ms on warm cache)

## Rollback Checkpoints

- After W1: library self-contained, no callers — safe to revert single file.
- After W2–W4: each adapter is a new file with no existing caller — safe to revert.
- W5 requires its own ADR before merge (touches build pipeline).

## References

- Source analysis: this session's 2026-04-24 10:57 UTC response
- Doctrine: `docs/reference/AST Dependency Graphs (ADG)/ADG Mental Model.md`
- Serialization rule: `.windsurf/rules/mcp-serialization.md` (§26)
- Canonical invariants: `.windsurf/rules/adg-canonical-invariants.md`
