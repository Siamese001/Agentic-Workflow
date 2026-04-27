# Plan — OTel Runtime-ADG Ingestion Pipeline

**Slug**: `otel-runtime-adg-ingest-7a3f12`
**Status**: Draft (awaiting /plan kick-off)
**Tier**: T3 (cross-layer L6→L4, >5 files, new ingestion pipeline)
**Parent marker**: `DEFERRED_SCOPE: plan=adg-pipeline-e2e-5287a1 wave=W7 phase=W7.1 layer=L6 surface=Observability coverage_gap_pct=100.0 est_tokens=8000`
**Priority band**: **P1** (auto-scored)
**ADG baseline**: regenerate at kick-off; use latest `adg_indexed_<ts>.sqlite`
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_<ts>.sqlite`

---

## Intent

Close the §8 (static vs runtime ADG) half-blind gap. Today `otel_mcp::otel_ingest_to_runtime_adg` exists as a tool surface but has **zero producer coverage** — no code path anywhere in `agentic_core/L6_observability/` or `system_learning/` emits spans that land in the runtime ADG store. W7.1 wires real producers: heal router + consensus + bus consumer OTel spans → runtime ADG ingest → queryable via `otel_mcp::otel_trace`.

---

## ADG_GRAPH_LAYER_EVIDENCE

Primary drivers (constitutional §22):

- **Materialized views (≥3)**: `mv_replay_surface_gaps` (identifies span surfaces with no ingest edge), `mv_runtime_spine_gaps` (identifies core runtime path emitters lacking OTel exit), `mv_observability_interference_breaches` (catches cross-layer interference during ingest), `mv_trace_replay_eval_gaps` (runtime→eval round-trip coverage)
- **Semantic edges**: `emits_side_effect` (span-emit surfaces), `flows_to` (ingest pipeline), `writes_to` (runtime-ADG store)
- **P-views**: `v_p0_l6_mutation` (guard against inadvertent L6 mutations during ingest), `v_p1_not_on_spine` (runtime spine coverage)

## ADG_HOTSPOT_REPORT

Hotspots must be recomputed at kick-off from latest snapshot. Target archetypes:

- **OBSERVABILITY** (L6 emitters missing ingest edges) — from `mv_replay_surface_gaps`
- **STATE_NODE** (runtime ADG store — its UWG writer-path surface) — from `mv_write_sovereignty_paths`
- **ORCHESTRATOR** (ingest pipeline itself — fan-out poisoner if it swallows)

Impact score = `violation_count × (1 + log10(1 + fan_in)) × 2.0` (L6 multiplier per constitutional §23).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:---:|---|:---:|---|
| W1 | P1.1 | Ingest contract + producer helper (`otel_runtime_ingest.py` in L6) | 1500 | `otel_mcp` tool surface stable | Todo | Helper exposes `emit_span_to_runtime_adg(span)`; 3 shape tests pass |
| W2 | P2.1–P2.3 | Wire 3 existing OTel emitters to helper: heal_router, consensus, sl_span | 2500 | W-D2 sl_span wiring in place (done 2026-04-22) | Todo | `otel_ingest_to_runtime_adg` receives ≥3 distinct service_name values |
| W3 | P3.1 | Integration test: emit→ingest→query round-trip | 1500 | Runtime-ADG schema stable | Todo | Test asserts span lands and is queryable via `otel_trace` within 1s |
| W4 | P4.1 | Coverage gate: `check_runtime_adg_coverage.py` (audit mode first) | 1500 | W3 passes | Todo | Gate reports coverage %; fails below 20% in audit |
| W5 | P5.1 | ADR-030 runtime-ingest contract + Notion writeback | 1000 | — | Todo | ADR posted; Notion ADR + MCP registry rows present |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1.1 | Ingest helper | `agentic_core/L6_observability/otel_runtime_ingest.py` (new) | Runtime-ADG schema drift | 1500 | Todo |
| P2.1 | Wire heal_router | `agentic_core/L6_observability/heal_router_otel.py` | ADR-025 ordering | 900 | Todo |
| P2.2 | Wire consensus | `agentic_core/L6_observability/consensus_otel.py` | C3 wave coupling | 900 | Todo |
| P2.3 | Wire sl_span | `system_learning/_tracing.py` | Cross-layer (done already; just add ingest call) | 700 | Todo |
| P3.1 | Round-trip test | `tests/integration/otel/test_runtime_adg_ingest_roundtrip.py` | Async ingest timing | 1500 | Todo |
| P4.1 | Coverage gate | `ops_scripts/ci/check_runtime_adg_coverage.py` (new) | Threshold calibration | 1500 | Todo |
| P5.1 | ADR + writeback | `docs/architecture/adr/ADR-030-*.md` + Notion | — | 1000 | Todo |

**Total est**: 8000 tokens (matches marker)

## Gap Register

| Gap | Impact | Resolution Wave |
|---|---|---|
| G-1 | Zero producers feeding runtime ADG | W2 |
| G-2 | No round-trip test | W3 |
| G-3 | No coverage visibility | W4 |
| G-4 | Contract undocumented | W5 |

## Success Criteria (rollup)

1. `otel_ingest_to_runtime_adg` receives spans from ≥3 service_names in a normal eval run
2. Round-trip test `emit→ingest→otel_trace` completes < 1 second
3. `check_runtime_adg_coverage.py` reports ≥20% coverage and is wired into adg-ci-gates.yml (audit mode)
4. ADR-030 posted to Notion ADR Registry
5. No regressions in L6 OTel unit tests (43/43 baseline)

## Dependencies

- W-D2 tracer wiring (commit `a3cca1afea`) — DONE
- ADR-025 heal_router OTel schema — DONE
- `otel_mcp` MCP server healthy at kick-off

## Out of Scope

- Runtime-ADG query-side optimization (separate concern)
- `otel_mcp` tool-surface changes (runtime-ADG ingest API is contract-stable)
- Span-to-ADG node resolution (uses existing adg_name resolver)
