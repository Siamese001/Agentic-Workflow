# Assurance P1 Gates — Runtime Trace, Negative Controls, Replay, Crosswalk

Status: Done
Tier: T3 (cross-layer; L1/L2/L4/L6 + CI)
Created: 2026-04-28
Plan slug: `assurance-p1-gates-ab4758`

## Goal

Close the four highest-leverage gaps in the 16-axis agentic assurance model, on top of the existing tests/Merkle/ADG/requirement-gate baseline:

1. **Runtime trace proof gate** — assert canary run emitted required span graph (U0→L0→C0→PA→L2→Exit→UWG)
2. **Negative-control library** — one known-bad input per gate, proving fail-closed behavior
3. **Deterministic replay proof gate** — invariant digest stable across two runs (route, gates, evidence_hash, disposition)
4. **ADG ↔ requirements crosswalk** — every tier obligation resolves to an ADG node + test ID

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1, W1.2, W1.3 | Runtime trace proof gate | ~14000 | otel_mcp healthy; runtime ADG store reachable; canary route contract definable | Done | CI gate fails when canary span graph missing required spans/attributes |
| W2 | W2.1, W2.2 | Negative-control library | ~10000 | Existing gates have identifiable fail-closed paths; pytest collects `tests/negative_controls/` | Done | One negative test per gate in `.cursor/scripts/pre_*_gate.py` and `ops_scripts/ci/check_*.py`; all assert exit≠0 |
| W3 | W3.1, W3.2 | Deterministic replay proof gate | ~12000 | Canary input deterministic; evidence digest schema stable | Done | Two replays produce identical `(route, gate_decisions, evidence_hash, disposition)` tuple |
| W4 | W4.1, W4.2 | ADG ↔ requirements crosswalk | ~9000 | Tier metadata enumerable; ADG node IDs stable across snapshots | Done | Every obligation row has `adg_node_id` + `test_id`; CI fails on unmapped obligation |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Define route contract schema | `config/runtime_trace/contracts/canary_lic_v1.yaml`, `agentic_core/L6_observability/runtime_trace/contract.py` | Span attribute drift; canary route stability | ~4000 | Done |
| W1.2 | Build canary runner + ingest hook | `scripts/proof/run_runtime_trace_proof.py`; reuses runtime-ADG materializer (in-process, hermetic) | Canary input determinism; fixture isolation | ~5000 | Done |
| W1.3 | CI gate + test coverage | `ops_scripts/ci/check_runtime_trace_contract.py`; `tests/unit/ops_scripts/ci/test_check_runtime_trace_contract.py`; wired into `run_contract_gates.py` | Flaky OTEL ingestion timing | ~5000 | Done |
| W2.1 | Negative-control directory + harness | `tests/negative_controls/__init__.py`, `tests/negative_controls/conftest.py`, `tests/negative_controls/README.md` | Directory layout; subprocess invocation pattern | ~3000 | Done |
| W2.2 | Per-gate negative tests | `tests/negative_controls/test_constitutional_negatives.py` (15+ parametrized cases — pre_run_gate fail modes + runtime trace gate); also added missing `_check_python_dash_c_quote_hazard` to pre_run_gate.py per constitutional rule | Coverage discipline; not duplicating existing unit tests | ~7000 | Done |
| W3.1 | Replay invariant digest spec | `tools/proof/replay_digest.py` — SHA-256 over canonical JSON of `(route_id, gate_decisions, evidence_packet_ids, final_disposition)` | Digest stability across PA randomness; seed control | ~5000 | Done |
| W3.2 | Replay proof gate + CI | `scripts/proof/run_replay_proof.py`, `ops_scripts/ci/check_replay_proof.py`, `tests/unit/tools/proof/test_replay_digest.py` | Two-run orchestration; isolation | ~7000 | Done |
| W4.1 | Crosswalk schema + extractor | `config/crosswalk/obligations.yaml`, `tools/crosswalk/build_requirements_crosswalk.py`, `artifacts/crosswalk/requirements_crosswalk.json` | Tier metadata heterogeneity; ADG node ID resolution | ~4000 | Done |
| W4.2 | Crosswalk CI gate | `ops_scripts/ci/check_requirements_adg_crosswalk.py`, `tests/unit/ops_scripts/ci/test_check_requirements_adg_crosswalk.py`; also added missing `test_check_windsurf_config_schema.py` for §27 coverage | Surfacing unmapped obligations without false positives | ~5000 | Done |

## ADG_HOTSPOT_REPORT

To be populated at W1.1 entry — query `mv_hotspot_centrality` filtered to L6_observability runtime_trace surface; W3 queries L1_cognition prompt_assembly for digest stability hotspots; W4 queries the requirement-metadata loaders.

| Hotspot | Layer | Fan-in | Archetype | Surface | Impact |
|---|---|---|---|---|---|
| `agentic_core/L6_observability/runtime_trace/contract.py` | L6 | TBD | CENTRAL_DEPENDENCY | Observability Surface | TBD |
| `agentic_core/L1_cognition/prompt_assembly/*.py` | L1 | TBD | ORCHESTRATOR | Execution Surface | TBD |
| `agentic_core/L4_state/utils/uwg/*.py` | L4 | TBD | STATE_NODE | Write Surface | TBD |

(Will be filled in by W1.1 from `mv_hotspot_centrality` queries.)

## ADG_GRAPH_LAYER_EVIDENCE

To be populated at W1.1 entry. Required materialized views and P-views:

- `mv_hotspot_centrality` — pick runtime-trace touch points
- `mv_dependency_cone_risk` — replay digest blast radius
- `mv_path_criticality_rollup` — canary route contract authoritative path
- Semantic edges: `flows_to`, `emits_side_effect`, `writes_to` (UWG sovereignty during canary)
- P-views: `v_p0_write_bypass_uwg` (must be empty during canary), `v_p1_mis_layered_infra`

## Dependencies

- otel_mcp healthy (`otel_server_info` source_is_stale=false)
- ADG snapshot fresh (`artifacts/adg/adg_indexed_<ts>.sqlite` < 24h old at wave entry)
- `mcp1_adg_health` green for W1.1, W4.1 entries

## Out of Scope

- Prompt-assembly boundary tests (deferred to Wave D / P2.7)
- Tool-authorization negative suite expansion beyond gate coverage (P2.6)
- Drift monitor expansion (P2.5)
- Judge calibration cadence (P3.9)
- Multi-agent handoff contract (P3.10)

## Success Exit Criteria

1. `python ops_scripts/ci/run_contract_gates.py` invokes 4 new gates, all green
2. `tests/negative_controls/` collects ≥15 tests, all pass
3. `python scripts/proof/run_replay_proof.py` produces identical digest across two runs
4. `artifacts/crosswalk/requirements_crosswalk.json` shows zero unmapped obligations
5. New CI workflow row in `.github/workflows/adg-ci-gates.yml` (or sibling) runs all four

## Notes

- Each wave commits independently; W1 must land before W3 (replay reuses canary infra)
- W2 and W4 can run in parallel after W1
- Author-Gate triggers expected at: W1.1 (route contract design), W3.1 (digest formula), W4.1 (crosswalk schema)
