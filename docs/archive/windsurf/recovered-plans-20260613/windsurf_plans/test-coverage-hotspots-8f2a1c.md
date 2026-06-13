# Plan: Top-15 Test Coverage Gaps (ADG-Hotspot Driven)

**Status:** Complete + Hardened — 5 waves + hardening pass landed 2026-04-24 (455 tests pass in 7.8s).
**Created:** 2026-04-24
**ADG Snapshot:** `adg_indexed_04242026_0721.sqlite`
**Plan ID:** `test-coverage-hotspots-8f2a1c`

## Final Outcome (2026-04-24)

| Wave | Phases | Tests | Status |
|------|--------|-------|--------|
| W1 | P1–P3 | 89 | Complete |
| W2 | P4–P6 | 63 | Complete |
| W3 | P7–P9 | 64 | Complete (3→1 bug pin + 2 happy-path flips) |
| W4 | P10–P12 | 142 | Hardened (+35 hypothesis/property tests) |
| W5 | P13–P15 | 97→97 (stable) | Hardened (+44 PII + property tests in P14) |
| **HARDENING** | latent-bug fixes | — | 3 bugs fixed upstream |
| **TOTAL** | **15 phases** | **455 tests** | **100% green** |

### Latent source bugs FIXED upstream (2026-04-24 hardening pass)

| # | File | Fix |
|---|------|------|
| 1 | `@c:/Git/Agentic-Workflow/agentic_core/L5_safety/types/cst_transformers_types.py:700` | Added `cst.ParserSyntaxError` to except clause; malformed type annotations now silently skip as intended |
| 2 | `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py:187-194` | `SealedL2Artifact(...)` now passes required `artifact_id` and omits `run_scope` (ClassVar sentinel) |
| 3 | `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py:197-206` | `_publish_metrics` rewritten to call `TelemetryBus.publish(**kwargs)` instead of manual malformed `BusMessage(...)` |

All 3 regression pins converted to **happy-path tests** asserting the post-fix contract.

### Property-based hardening (new 2026-04-24)

- `test_abstain_contract.py`: 9 hypothesis tests — decision-vs-comparison, determinism, multi-signal priority, clarify iff contract
- `test_compiled_artifact.py`: 5 hypothesis tests — HMAC roundtrip, wrong-secret rejection, manifest_hash nonce-independence, slot-order invariance (EQ-9), tampering detection
- `test_semantic_cache_manager.py`: 6 hypothesis tests — L1 normalization idempotence, PII sanitize stability, `is_safe` ↔ `detect_pii` inverse relation, threshold env-override roundtrip, PLUS 18 `PII_Sanitizer` unit tests

## Intent

Identify and close the top 15 test-coverage gaps in the repository using ADG hotspot analysis (fan-in × layer-criticality multiplier), filtered to modules that have **ZERO test file on disk**. Execute as 5 waves of 3 files each to keep per-wave token budgets bounded.

## ADG_GRAPH_LAYER_EVIDENCE

Evidence pulled from graph-layer primitives on snapshot `c2a881b3644f172a07cbaaf520a0c18f02540d0f` (ADG Provenance: backend=sqlite):

- **`mv_hotspot_centrality`** — fan-in + fan-out + degree centrality; drove the primary ranking (324 modules with `fan_in >= 10`).
- **`mv_graph_reverse_dependency_hotspots`** — reverse dependency score + layer criticality weight; confirmed layer multiplier (L0/L5 = 2.0, L3/L4/L_RUNTIME = 1.75, L_SHARED = 1.5, L1/L2/L_SL = 1.0, L_TOOLS/L_OPS/L6 = 0.75).
- **`mv_eval_coverage_by_path`** — observed action_node_count vs eval_covered_count = 0 across all layers (note: this measures *eval pipeline* coverage, not pytest; we use the `covers` edge count + on-disk test discovery as the actual test-coverage signal).
- **`edges WHERE relation_type='covers'`** — 7,134 covers edges spanning 904 distinct covered nodes, emitted by `tools/adg/integration/coverage_bridge.py` (W10 coverage-to-code-path linkage, shipped 2026-04-11).
- **P-views**: No P0/P1 hotspots intersected with the top 15; all are architectural/utility hotspots, not SC/AP violation concentrations.

**Cross-reference with 5 ADG Surfaces** (Execution/Write/Security/State/Observability):
- Rank 1, 6, 11, 13, 15: **Security** surface (L5_safety)
- Rank 7, 9: **Execution** surface (L3_orchestration)
- Rank 9: **State** surface (runtime_hitl_ledger, L3)
- Rank 4, 8: **Execution** (ADG pipeline tooling)
- Rank 2, 3, 5: **Execution/Write** (contracts, validators, static scanner)

## Methodology

1. Query `mv_hotspot_centrality` for all modules with `fan_in >= 10`, latest snapshot.
2. Compute `impact = fan_in × layer_multiplier` (layer multipliers per ADG canonical invariants §6).
3. Filter: exclude `__init__.py`, `/tests/`, `_smoke`, `path_constants.py`, and the outlier `lifecycle_trace_contract.py` (trace-emission scaffold, not business logic).
4. Cross-check with `tests/**/test_<stem>.py` on-disk — remove any with existing tests.
5. Take top 15 by `impact`.

## Top 15 Coverage Gaps (DIRECTLY OBSERVED from ADG + filesystem)

| Rank | Impact | Fan-In | Layer | Mul  | Path                                                                    |
|------|--------|--------|-------|------|-------------------------------------------------------------------------|
| 1    | 190.0  | 95     | L5    | 2.00 | `agentic_core/L5_safety/types/cst_transformers_types.py`                |
| 2    | 170.2  | 227    | L_TOOLS | 0.75 | `agentic_core/adg/contracts/schema_util.py`                           |
| 3    | 138.0  | 92     | L_SHARED | 1.50 | `agentic_core/utils/runners/ssot_discovery_validator.py`             |
| 4    | 129.0  | 172    | L_OPS | 0.75 | `ops_scripts/ci/_adg_wiring_gate_base.py`                                |
| 5    | 112.5  | 150    | L_TOOLS | 0.75 | `agentic_core/adg/extraction/static_scanner.py`                        |
| 6    | 88.0   | 44     | L5    | 2.00 | `agentic_core/L5_safety/adapters/human_approval_adapter.py`             |
| 7    | 87.5   | 50     | L3    | 1.75 | `agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py` |
| 8    | 84.8   | 113    | L_TOOLS | 0.75 | `tools/generate/adg_graph_watchlist_builder.py`                        |
| 9    | 84.0   | 48     | L3    | 1.75 | `agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py`     |
| 10   | 78.8   | 45     | L_RUNTIME | 1.75 | `agentic_core/runtime/contracts/abstain_contract.py`                  |
| 11   | 71.8   | 41     | L4    | 1.75 | `agentic_core/L4_state/utils/lifecycle/state_lifecycle.py`              |
| 12   | 58.0   | 58     | L2    | 1.00 | `agentic_core/L2_execution/reasoning/compiled_artifact.py`              |
| 13   | 58.0   | 29     | L5    | 2.00 | `agentic_core/L5_safety/enforcement/escalation/human_escalation.py`     |
| 14   | 52.5   | 30     | L4    | 1.75 | `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`          |
| 15   | 52.0   | 26     | L5    | 2.00 | `agentic_core/L5_safety/exit_control/hitl_classes.py`                   |

## Wave Structure

| Wave | Phase IDs | Focus                                          | Est. Tokens | Assumptions                                      | Status | Success Criteria                                                   |
|------|-----------|------------------------------------------------|-------------|--------------------------------------------------|--------|--------------------------------------------------------------------|
| W1   | W1.P1–P3  | Ranks 1–3 (L5 transformers, ADG contracts, SSOT validator) | 🟢 6,000  | Small-to-medium files, pure-logic testable      | in_progress | 3 test files green; pytest shows ≥ 15 tests pass for each         |
| W2   | W2.P4–P6  | Ranks 4–6 (ADG wiring gate, static scanner, human approval adapter) | 🟢 8,000  | Some mocking of Path/subprocess needed          | todo   | 3 test files green; ≥ 12 tests/file                                |
| W3   | W3.P7–P9  | Ranks 7–9 (L3 engines, runtime HITL ledger)    | 🟡 10,000  | L3 orchestration may need async fixtures        | todo   | 3 test files green; ≥ 10 tests/file                                |
| W4   | W4.P10–P12 | Ranks 10–12 (abstain contract, state lifecycle, compiled artifact) | 🟡 10,000  | State tests may need tmp_path + registry fixtures | todo   | 3 test files green; ≥ 10 tests/file                                |
| W5   | W5.P13–P15 | Ranks 13–15 (L5 escalation, semantic cache, HITL classes) | 🟡 10,000  | Semantic-cache test may need redis/chromadb stub | todo   | 3 test files green; ≥ 10 tests/file; 2026-Q2 Coverage audit target  |

**Total budget:** ~44,000 tokens across 5 waves.

## Phase-Level Summary

| Phase ID | Title                                                   | Scope (files) | Pain Points                                        | Est. Tokens | Status |
|----------|---------------------------------------------------------|---------------|----------------------------------------------------|-------------|--------|
| W1.P1    | Test: L5 CST transformers types                         | 1 test file   | Trace-emit boilerplate noise in source module      | 2500        | in_progress |
| W1.P2    | Test: ADG schema_util (canonical_name, module_path_to_layer, layer consistency) | 1 test file | 3030-line source, must focus on pure functions    | 2500        | in_progress |
| W1.P3    | Test: SSOT discovery validator                          | 1 test file   | Tiny file, but high fan-in — register/validate roundtrip | 1000   | in_progress |
| W2.P4    | Test: ADG wiring gate base                              | 1 test file   | Abstract base — need minimal concrete subclass     | 3000        | todo    |
| W2.P5    | Test: ADG static scanner                                | 1 test file   | File I/O + AST walking                             | 3000        | todo    |
| W2.P6    | Test: L5 human approval adapter                         | 1 test file   | Integration with escalation orchestrator           | 2000        | todo    |
| W3.P7    | Test: L3 evidence_eval_bridge                           | 1 test file   | Orchestration logic, bridge contracts              | 3500        | todo    |
| W3.P8    | Test: L_TOOLS adg_graph_watchlist_builder               | 1 test file   | Watchlist YAML + ADG node query                    | 3500        | todo    |
| W3.P9    | Test: L3 runtime_hitl_ledger                            | 1 test file   | Async ledger writes, state invariants              | 3000        | todo    |
| W4.P10   | Test: L_RUNTIME abstain contract                        | 1 test file   | Dataclass + contract invariants                    | 3000        | todo    |
| W4.P11   | Test: L4 state_lifecycle                                | 1 test file   | State transitions, registry interaction            | 3500        | todo    |
| W4.P12   | Test: L2 compiled_artifact                              | 1 test file   | Compilation + serialization roundtrip              | 3500        | todo    |
| W5.P13   | Test: L5 human_escalation                               | 1 test file   | Escalation pipeline, policy check                  | 3000        | todo    |
| W5.P14   | Test: L4 semantic_cache_manager                         | 1 test file   | Cache-miss/hit, similarity threshold, TTL          | 4000        | todo    |
| W5.P15   | Test: L5 hitl_classes                                   | 1 test file   | HITL dataclass invariants, serialization           | 3000        | todo    |

## Verification

Each wave ends with:
1. `python -m pytest tests/unit/path/to/new_test.py -v` → 100% pass
2. `python -m pytest --collect-only tests/unit/path/to/new_test.py` → no collection errors
3. `python -m py_compile <source_module_under_test>` → clean (sanity)
4. On Wave 5 exit: full `python tools/generate_full_adg.py` to refresh the `covers` edges for the new tests.

## Gap Register

- **Coverage-bridge refresh**: Several lower-ranked hotspots (rank 16–30) have tests but stale `covers` edges. Out of scope for this plan; a separate task should run `tools/adg/integration/coverage_bridge.py` on a fresh pytest-cov run to refresh all `covers` edges before the next full-ADG regeneration.
- **Layer multiplier for L_SL**: Added 1.25 heuristically (between shared utilities and orchestration); not yet codified in ADG canonical invariants §6. TODO: ratify or adjust.

## References

- ADG canonical invariants: `.windsurf/rules/adg-canonical-invariants.md` (layer multipliers §6, 5 surfaces §3)
- Coverage bridge: `tools/adg/integration/coverage_bridge.py` (W10 ship, 2026-04-11)
- Notion backlog: Wave/Phase Convergence DB `aa8d2507-101e-4384-81d9-60ea3fe33876`
