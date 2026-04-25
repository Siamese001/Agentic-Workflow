# V6 Shadow Evaluation — Repo Gap Assessment

**Reference**: `06_Shadow_Evaluation_System_Learning_v6.md`
**Plan**: `.windsurf/plans/shadow-eval-v6-gap-d4a9c2.md`
**Date**: 2026-04-25

## Summary

The repo already implements most v6 step engines. The principal gaps are at the **aggregation /
contract layer**, not at the per-stage engine layer. This document maps every v6 surface to a repo
artifact and flags the four real gaps closed by plan `shadow-eval-v6-gap-d4a9c2`.

## Coverage Matrix — v6 Step → Repo Artifact

| v6 Step | v6 Authoritative Contract | Repo Artifact | Status |
|---|---|---|---|
| S1A Gather Exhaust | telemetry consumer, historical ingestion, OTel store adapter, prompt tracer | `system_learning/engines/telemetry_consumer.py`, `historical_ingestion_orchestrator.py`, `historical_backfill_engine.py`, `prompt_execution_tracer.py`, `agentic_core/L6_observability/otel_runtime_ingest.py` | ✅ Covered |
| S1B Normalize Evidence | trace feature extractor, meta-learning inbox, lineage binder | `trace_feature_extractor.py`, `meta_learning_bus.py`, `prompt_provenance_builder.py`, `meta_learning_replay_binding.py` | ✅ Covered |
| S1C Observer Law | surface isolation validator, stage barrier enforcer, invariant checks | `surface_isolation_validator.py`, `stage_barrier_enforcer.py` | ✅ Covered |
| S2A Outcome Evals | outcome evaluator, groundedness evaluator, citation/support scorer | `outcome_evaluation_engine.py`, `agentic_core/L6_observability/utils/evaluation/rag_evaluators.py` | ✅ Covered |
| S2B Trajectory Evals | trajectory evaluator, trace rubric scorer, retry/thrash detector | `trajectory_evaluation_engine.py`, `trajectory_divergence_scorer.py` | ✅ Covered |
| S2C Governance Regression | gate regression checker, prompt drift detector, shadow drift analyzer | `g_gate_regression_checker.py`, `prompt_drift_detector.py`, `shadow_drift_analyzer.py` | ✅ Covered |
| S2D Human Calibration | human calibration engine, HITL decision logger, golden-set review | `human_calibration_engine.py`, `hitl_decision_logger.py` | ✅ Covered |
| S3A Signal Fusion | signal aggregator, signal grouping, BUS P / BUS T fusion | `signal_aggregator_engine.py`, `signal_grouping_engine.py` | ✅ Covered |
| S3B Incident RCA | RCA engine, cluster analyzer, pattern analysis | `rca_engine.py`, `rca_cluster_engine.py`, `pattern_analysis_engine.py` | ✅ Covered |
| S3C Rule Drafting | prompt proposer, policy proposer, rubric/config/retrieval-profile proposer | `rule_drafting_engine.py`, `l1_model_proposer.py`, `l5_policy_proposer.py`, `rag_proposer.py`, `retrieval_profile_proposal.py` | ✅ Covered |
| S4A Gauntlet | approval gauntlet, deterministic replay, regression runner, retrieval replay check | `approval_gauntlet_engine.py`, `deterministic_replay_engine.py`, `gauntlet_gate.py`, `retrieval_profile_replay_check.py` | ✅ Covered |
| S4B Approve / Reject | approval gate, system-learning admission gate, eval freshness gate | `system_learning_admission_gate.py`, `eval_freshness_gate.py`, `eval_gated_l4_writer.py` | ✅ Covered |
| S4C UWG Master Clerk | L4 state writer, L4 audit reader, L4 version store | `l4_state_writer.py`, `l4_audit_reader.py`, `l4_version_store.py` | ✅ Covered |
| S4D Ledger Proof | replay binding, state digest, startup integrity, rollout receipt generator | `meta_learning_replay_binding.py`, `meta_learning_state_digest.py`, `faiss_startup_integrity.py` | ✅ Covered |

## Real Gaps Identified

### G1 — No Unified V6 KPI Board

**v6 ref**: lines 231-245 (KPI BOARD section).

**Symptom**: Each KPI exists conceptually as English prose; no typed surface aggregates them. The
generic `LearningMetricsDashboard` is a free-form metric recorder, not v6-spec-aligned.

**Closed by**: `system_learning/engines/v6_kpi_board.py` (W1.1) — typed `V6KPIBoard` with 11 enum
KPI names, frozen `V6_KPI_SPECS` registry, and `evaluate_sample` semantics.

### G2 — No Compound HEALTH Evaluator

**v6 ref**: lines 34-36 (HEALTH DEFINITION).

**Symptom**: v6 declares the pipeline healthy only when ingest freshness, eval coverage,
calibration freshness, replay localization, false-promote rate, and UWG uniqueness are all green
together. Nothing in the repo computes this conjunction.

**Closed by**: `V6KPIBoard.health_snapshot()` + `HEALTH_REQUIRED_KPIS` constant.

### G3 — No Invariant-Level Test Coverage

**v6 ref**: lines 248-284 (V6 NORMATIVE INVARIANTS, 7 items).

**Symptom**: Each invariant has at least one engine that participates in enforcing it, but no
single test file asserts the **combined** invariant behavior end-to-end as a v6 contract.

**Closed by**: `tests/unit/system_learning/test_v6_invariants.py` (W2.1).

### G4 — No Contract Ownership Map Registry

**v6 ref**: lines 291-308 (V6 CONTRACT OWNERSHIP MAP).

**Symptom**: The 14-row table assigning each step to authoritative engines is documentation only;
nothing programmatically asserts the engines named in the map exist in the repo.

**Closed by**: `system_learning/v6_contract_map.py` (W3.1) + drift test (W3.2).

## Out-of-Scope Observations

- **KPI sample population** is intentionally not wired in this plan. Producers (telemetry
  consumer, gauntlet engine, replay binder, etc.) will adopt `V6KPIBoard.record()` in a follow-up
  scope. This plan establishes the typed surface; population is a separate concern.
- **No new ingest paths** are added; `telemetry_consumer.py` is sufficient.
- **No refactoring** of existing engines. The KPI Board is purely additive.

## V6 KPI Reference Card

| KPI | Phase | Threshold | Direction | Unit |
|---|---|---|---|---|
| Trace-ingest freshness | 6A | 600 | <= | seconds |
| Eval coverage of runs | 6B | 0.98 | >= | ratio |
| Judge unknown-budget compliance | 6B | 0.95 | >= | ratio |
| Judge-human κ freshness | 6B/S2D | 604800 | <= | seconds (7d) |
| RCA-to-proposal lead time | 6C | 86400 | <= | seconds (24h) |
| Gauntlet false-promote rate | 6D | 0.01 | <= | ratio |
| UWG ink-path uniqueness | 6D | 0 | == | count |
| Replay divergence localization | 6D | 0.90 | >= | ratio |
| Eval-freshness on write | 6D | 1.00 | >= | ratio |
| Exemplar-hit rate | cross | 0.20 | >= | ratio |
| Saturation watch | 6B | 0.10 | <= | ratio |

These thresholds are encoded verbatim in `V6_KPI_SPECS` and locked by `TestV6KPISpecValues`.
