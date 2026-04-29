# Plan: ADG Three-Graph Test Harness — Manifest-Driven CI

**Slug**: `adg-three-graph-harness-e57cc7`
**Status**: In progress
**Tier**: T3 (cross-layer harness; multi-file scaffold)
**Origin**: User request 2026-04-29 — harden and streamline the ADG three-graph testing framework

## Goal

Convert the existing static + registry + runtime + cross-bucket ADG checks into a
manifest-driven CI harness with a canonical gate registry, normalized result
schema, dedicated test lanes per graph, and negative controls.

## Constraints (from request)

- Do NOT create a new report file.
- Do NOT rename anything.
- Do NOT make certification claims.
- Existing CI gates remain backward compatible.
- No deletion of existing scripts until parity tests pass.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | W1.P1, W1.P2, W1.P3 | Spine: GateResult schema, manifest, runner | ~9k | YAML available; existing `check_*` scripts callable | done | Runner loads manifest, executes one gate, emits normalized JSON |
| **W2** | W2.P1, W2.P2, W2.P3 | Three new gates: registry integrity, runtime topology, impossible states | ~12k | Snapshot at `artifacts/adg/adg_indexed_*.sqlite`; `v_runtime_proof` has `static_edge_id`/`latest_trace_id` columns | done | Each gate runs against current snapshot, produces normalized JSON |
| **W3** | W3.P1 | Manifest view-rule executor (`check_adg_view_rules.py`) | ~3k | Simple SQL count rules suffice for the W4/W5/W6 family | done | View-rule gate runs at least 3 manifest-defined rules |
| **W4** | W4.P1 | Negative-control fixtures + tests | ~7k | Fixtures are minimal SQLite snapshots seeded by Python | done | All 10 negative cases produce expected `actual_fail_reason` |
| **W5** | W5.P1 | Tests: schema, manifest, integration, parity | ~6k | pytest available; 60s timeout per gate via subprocess | done | Parity test confirms legacy + manifest agree on PASS/FAIL for shared gates |
| **W6** | W6.P1 | Verification + commit | ~2k | All tests green | done | `python ops_scripts/ci/run_adg_three_graph_tests.py --suite quick` exits 0 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | GateResult schema | `agentic_core/adg/ci/__init__.py`, `gate_result.py` | Match exact field list from spec | 1.5k | done |
| W1.P2 | Manifest YAML | `ops_scripts/ci/adg_gate_manifest.yaml` | Cover every existing gate + 3 new + view-rules | 3k | done |
| W1.P3 | Manifest runner | `run_adg_three_graph_tests.py` | Subprocess + JSON normalization + bypass-env detection | 4k | done |
| W2.P1 | Registry integrity | `check_registry_graph_integrity.py` | Some required fields aspirational — emit WARN truthfully | 4k | done |
| W2.P2 | Runtime topology | `check_runtime_trace_topology.py` | Walk runtime store JSON OR rely on `v_runtime_proof` cols | 4k | done |
| W2.P3 | Impossible states | `check_three_bucket_impossible_states.py` | 7 invariants from spec | 4k | done |
| W3.P1 | View rules | `check_adg_view_rules.py` | Manifest-defined SQL rule executor | 3k | done |
| W4.P1 | Negative fixtures | `tests/adg/fixtures/negative/` + builder | Minimal seeded SQLite per case | 7k | done |
| W5.P1 | Tests | `tests/unit/...` + `tests/integration/adg/...` | Schema + manifest + integration + parity + negative | 6k | done |
| W6.P1 | Verify + commit | run + commit | All gates execute | 2k | done |

## Out of Scope

- Killing existing `check_w4_*`/`check_w5_*`/`check_w6_*` scripts (parity-protected).
- Adding new materialized views.
- Changing snapshot generation (`tools/generate_full_adg.py`).
- Rewriting MCP server.

## ADG_GRAPH_LAYER_EVIDENCE

Greenfield harness scaffold. The harness QUERIES graph-layer primitives — it
doesn't refactor source code that depends on them. Therefore there is no
hotspot/blast-radius to rank. The relevant graph-layer surface this work
consumes:

| Primitive | Used by |
|---|---|
| `nodes` (entity_type, layer, identity_kind, confidence) | `check_registry_graph_integrity.py` (registry node well-formedness) |
| `edges` (bucket, resolution_status, authority_status, evidence_refs, source_file) | `check_registry_graph_integrity.py`, `check_three_bucket_impossible_states.py` |
| `v_runtime_proof` (static_edge_id, latest_trace_id, latest_span_id, evidence_refs, attesting_trace_count) | `check_runtime_trace_topology.py`, `check_three_bucket_impossible_states.py` |
| `mv_*` count + `v_p*` count | `check_adg_view_rules.py` (manifest-driven counts) |
| `meta` (artifact_digest) | runner (snapshot_id) + `check_three_bucket_impossible_states.py` (stale snapshot vs gap report) |

## ADG_HOTSPOT_REPORT

Not applicable — this plan adds new files; no existing hotspots are being
refactored. Constitutional §22 requires this section in T2/T3 plans for
*refactoring*; harness-build plans satisfy the spirit by listing the graph-layer
surface they consume (above).

## Definition of Done

- One command: `python ops_scripts/ci/run_adg_three_graph_tests.py --suite quick`
- Five lanes: preflight → static → registry → runtime → cross_bucket → negative
- Normalized JSON per gate + rollup
- Bypass env vars cannot produce green strict run
- All 10 negative-control cases tested with exact `actual_fail_reason` matching
- Parity test green
- Existing `check_adg_certified.py` continues to work unchanged
