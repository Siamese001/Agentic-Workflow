# Shadow Evaluation v6 — Gap Assessment & Implementation Plan

**Plan ID**: `shadow-eval-v6-gap-d4a9c2`
**Created**: 2026-04-25
**Owner**: Cascade
**Reference**: `docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v6.md`
**Tier**: T3 (cross-layer, multi-module, new surfaces)
**Status**: Active

## Executive Summary

The repo has substantial infrastructure for v6 (80+ engines under `system_learning/`, dozens
under `agentic_core/L6_observability/`). The principal gaps are:

1. **No unified V6 KPI Board** — the 11 KPIs in v6 lines 231-245 lack a single typed aggregator.
2. **No compound HEALTH evaluator** — v6 lines 34-36 require all-green compound state; no module
   computes it.
3. **No invariant-level test coverage** — v6 lines 248-284 list 7 normative invariants; no test
   file enforces them as a unit.
4. **No contract ownership registry** — v6 lines 291-308 map each step to authoritative engines;
   nothing programmatically asserts the map stays in sync with the codebase.

Existing surfaces NOT to duplicate:

| v6 step | Existing engine |
|---|---|
| S1A Gather Exhaust | `system_learning/engines/telemetry_consumer.py`, `historical_ingestion_orchestrator.py`, `prompt_execution_tracer.py` |
| S1B Normalize Evidence | `trace_feature_extractor.py`, `meta_learning_bus.py` |
| S1C Observer Law | `surface_isolation_validator.py`, `stage_barrier_enforcer.py` |
| S2A Outcome Evals | `outcome_evaluation_engine.py` |
| S2B Trajectory Evals | `trajectory_evaluation_engine.py`, `trajectory_divergence_scorer.py` |
| S2C Governance Regression | `g_gate_regression_checker.py`, `prompt_drift_detector.py`, `shadow_drift_analyzer.py` |
| S2D Human Calibration | `human_calibration_engine.py`, `hitl_decision_logger.py` |
| S3A Signal Fusion | `signal_aggregator_engine.py`, `signal_grouping_engine.py` |
| S3B Incident RCA | `rca_engine.py`, `rca_cluster_engine.py`, `pattern_analysis_engine.py` |
| S3C Rule Drafting | `rule_drafting_engine.py`, `l1_model_proposer.py`, `l5_policy_proposer.py`, `rag_proposer.py`, `retrieval_profile_proposal.py` |
| S4A Gauntlet | `approval_gauntlet_engine.py`, `deterministic_replay_engine.py`, `gauntlet_gate.py` |
| S4B Approve / Reject | `system_learning_admission_gate.py`, `eval_freshness_gate.py`, `eval_gated_l4_writer.py` |
| S4C UWG Master Clerk | `l4_state_writer.py`, `l4_audit_reader.py`, `l4_version_store.py` |
| S4D Ledger Proof | `meta_learning_replay_binding.py`, `meta_learning_state_digest.py`, `faiss_startup_integrity.py` |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.1, W1.2, W1.3 | V6 KPI Board module + unit tests + gap assessment doc | ~6000 | Active | Module imports clean, 11 KPIs typed, unit tests pass |
| W2 | W2.1, W2.2 | V6 invariant test suite (7 invariants) | ~5000 | Pending | Each invariant has at least one passing test asserting the constraint |
| W3 | W3.1, W3.2 | Contract ownership map registry + integration test | ~4000 | Pending | Registry module + test asserting all 14 step engines exist |
| W4 | W4.1 | Wire KPI Board into existing dashboards (advisory only) | ~3000 | Pending | Optional integration; no behavior change |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | KPI Board module | `system_learning/engines/v6_kpi_board.py` (NEW) | Translating prose KPIs to typed records; threshold encoding | 2500 | Active |
| W1.2 | KPI Board unit tests | `tests/unit/system_learning/engines/test_v6_kpi_board.py` (NEW) | Cover threshold semantics, compound health, edge cases | 2000 | Pending |
| W1.3 | Gap assessment doc | `docs/reference/06_Shadow_Evaluation_System_Learning/v6_GAP_ASSESSMENT.md` (NEW) | Side-by-side v6 spec ↔ repo surfaces | 1500 | Pending |
| W2.1 | Invariant test suite | `tests/unit/system_learning/test_v6_invariants.py` (NEW) | One test per invariant — observer law, eval-before-learning, rubric integrity, no silent promote, no partial bypass, UWG sole ink, future-run only | 3500 | Pending |
| W2.2 | Invariant test wiring | `tests/unit/system_learning/conftest.py` if needed | Fixtures for stub gauntlet/eval records | 1500 | Pending |
| W3.1 | Contract ownership registry | `system_learning/v6_contract_map.py` (NEW) | Encode the 14-row table from v6 lines 291-308 | 2000 | Pending |
| W3.2 | Contract map test | `tests/unit/system_learning/test_v6_contract_map.py` (NEW) | importlib.find_spec for each engine name | 2000 | Pending |
| W4.1 | Dashboard wiring | `agentic_core/L6_observability/utils/evaluation/learning_metrics_dashboard.py` | Optional: expose `v6_kpi_board()` accessor | 3000 | Pending |

## Gap Register

| ID | Gap | v6 Reference | Implementation |
|---|---|---|---|
| G1 | No typed V6 KPI records | lines 231-245 | W1.1 — `V6KPI` dataclass + 11 instances |
| G2 | No compound HEALTH definition | lines 34-36 | W1.1 — `aggregate_health()` |
| G3 | No invariant test coverage | lines 248-284 | W2 |
| G4 | No contract ownership map | lines 291-308 | W3 |
| G5 | KPI threshold values not centralized | scattered | W1.1 — `_KPI_THRESHOLDS` constant |

## Out of Scope (Explicit)

- Refactoring any existing engine (low ROI, high blast radius)
- New ingest paths (existing `telemetry_consumer` is sufficient)
- New gauntlet phases (existing `approval_gauntlet_engine` covers S4A)
- Live KPI metric population (KPI Board is a typed surface; population wiring is W4 advisory)

## Rollback

All waves are additive. Rollback = `git revert` of each wave's commit.
