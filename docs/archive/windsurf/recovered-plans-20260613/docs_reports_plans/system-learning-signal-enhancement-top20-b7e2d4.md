# System Learning Signal Enhancement — Top 20 Opportunities

**Date:** 2026-03-25
**Scope:** ADG, Execute_SSOT, apps_*, and OTHER subsystems (L1–L5, prompt_governance, infrastructure)
**Supersedes:** `system-learning-signal-enhancement-top10-a3f8c1.md`
**Goal:** Comprehensive, high-fidelity input signals across ALL subsystems for healing, routing, drift detection, policy decisions, and architectural governance.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 1. Signal Landscape — Current State

### 1.1 What system learning consumes TODAY

| Signal | Producer | Consumer |
|--------|----------|----------|
| Healing EMA rates | `HealingSuccessRateStore` | `DefaultHealingPatternAdvisor` |
| RCA findings (regex) | `rca_engine.analyze_failures` | `SystemLearningMemoryBridge` |
| Drift summaries (embedding cosine) | `ShadowDriftAnalyzer` | `PolicyRecommendationEngine` |
| Policy recommendations | `PolicyRecommendationEngine` | `RetrievalProfileProposalManager` |
| Healing outcome events | `HealingOutcomeIntakeAdapter` | `HealingOutcomeAggregator` |
| Pattern analysis | `PatternAnalysisEngine` | `HealingConfigOptimizer` |
| BGE-m3 failure embeddings | `bmg_embed_text` | FAISS store |
| Historical backfill | `.healing_backups` dir | `HealingOutcomeAggregator` |
| BaseHealingOrchestrator cycles | `LicHealingOrchestrator` / `RgHealingOrchestrator` | `GraphMemoryBridge` |
| Oscillation detection | `OscillationDetector` | `meta_learning_pipeline` validation |
| Healing confidence scores | `HealingConfidenceScorer` | Escalation decisions |

### 1.2 Subsystems producing signals NOT consumed by system learning

| Subsystem | Unconsumed Signals | Count |
|-----------|-------------------|-------|
| **ADG** | Violations, hotspots, repair routes, confidence tiers, violation trends, module topology | 6 |
| **Execute_SSOT** | Phase outcomes, ADG behavioral scores, cognitive dispositions, compliance scores | 4 |
| **apps_*** | Cross-domain healing, eval regressions, scenario outcomes, OTel spans | 4 |
| **L5_safety** | Circuit breaker transitions, safety audit records, guardrail hit patterns | 3 |
| **prompt_governance** | Template drift detections, injection attempt counts, slot contract violations | 3 |
| **L2_execution** | Resource prediction envelopes, rollback outcomes, healing tier dispatch decisions | 3 |
| **L3_orchestration** | WorkflowLearningBridge (no SL consumers wired), recursion monitor alerts | 2 |
| **L1_cognition** | HealingMemoryRetriever quality, reasoning evaluation scores | 2 |
| **infrastructure** | Cross-layer coherence inconsistencies, adaptive optimizer metrics | 2 |

---

## 2. Top 20 Enhancement Opportunities

---

### #1 — RCA Engine: ADG Violation Correlation
**Domain:** ADG → system_learning | **Value:** Highest | **Effort:** Low
**Gap:** `rca_engine.analyze_failures()` classifies failures by regex only. Zero awareness of whether the failing file has a known architectural violation.
**Enhancement:** Add optional `violation_file_set: frozenset[str]` from `ADGMemoryAdapter`. When failure file matches violation source → tag `RCAFinding` with `adg_correlated=True`.
**Files:** `system_learning/engines/rca_engine.py`, `agentic_core/adg/adapters/ADGMemoryAdapter.py`, `system_learning/pipelines/meta_learning_pipeline.py`

---

### #2 — Execute_SSOT: Phase Outcome Feedback Loop
**Domain:** Execute_SSOT → system_learning | **Value:** Very High | **Effort:** Medium
**Gap:** `_fire_meta_learning_intake` ingests `healing_actions` but NOT per-phase outcomes (`location_violations`, `hierarchy_fixed`, `gravity_fixed`, `classification_violations`, `compliance_scores`).
**Enhancement:** Collect phase outcome summary from `state_mgr.state`, feed as `phase_outcomes_bytes` into `PipelineDependencies`.
**Files:** `agentic_core/L0_routing/scripts/_ssot_meta_learning.py`, `system_learning/pipelines/meta_learning_pipeline.py`

---

### #3 — Healing Pattern Advisor: ADG Hotspot-Aware Priority Boost
**Domain:** ADG → system_learning | **Value:** High | **Effort:** Low
**Gap:** `DefaultHealingPatternAdvisor.advise()` bases `pattern_boost` only on historical rates. No architectural risk awareness.
**Enhancement:** Query `ADGHotspot` entities; if module is top-20 fan-out hotspot → add `reason_code="adg_hotspot"` + boost multiplier.
**Files:** `system_learning/engines/default_healing_pattern_advisor.py`, `agentic_core/adg/adapters/ADGMemoryAdapter.py`

---

### #4 — Optimization Proposal Engine: ADG Repair Route Feed
**Domain:** ADG → system_learning | **Value:** High | **Effort:** Medium
**Gap:** `optimization_proposal_engine.py` has `POLICY_VIOLATION` templates but triggers only from runtime signals. 10 critical ADG violations with `recommended_agent` and `ci_lane` from `RepairRoute` never reach the proposal engine.
**Enhancement:** Feed `repair_routing_summary()` as new `RepairRouteCluster` into the optimizer. Maps violation→agent→proposal.
**Files:** `system_learning/engines/optimization_proposal_engine.py`, `agentic_core/L0_routing/scripts/_ssot_meta_learning.py`

---

### #5 — Shadow Drift Analyzer: ADG Violation Trend as Drift Dimension
**Domain:** ADG → system_learning | **Value:** High | **Effort:** Low
**Gap:** `ShadowDriftAnalyzer` computes drift from embedding cosine only. Violation growth (10→15) between ADG builds triggers no drift signal.
**Enhancement:** Compare `ADGSnapshot` violation counts across Memory MCP snapshots. New dimension: `violation_delta`. Folds into existing `DriftSummary`.
**Files:** `system_learning/engines/shadow_drift_analyzer.py`, `system_learning/adapters/system_learning_memory_bridge.py`

---

### #6 — Execute_SSOT: ADG Behavioral Score → Routing Confidence
**Domain:** Execute_SSOT → system_learning | **Value:** Medium-High | **Effort:** Low
**Gap:** `execute_ssot.py` Phase 1 stores `adg_territory_score` in `state_mgr.state` — never forwarded to `l0_routing_confidence_monitor.py`.
**Enhancement:** Emit `adg_territory_score` as signal to `HealingSuccessRateStore`; confidence monitor factors it in.
**Files:** `agentic_core/L0_routing/scripts/_ssot_meta_learning.py`, `system_learning/engines/l0_routing_confidence_monitor.py`

---

### #7 — apps_* Domain Healing: Cross-Domain Pattern Sharing
**Domain:** apps_* → system_learning | **Value:** Medium-High | **Effort:** Medium
**Gap:** `BaseHealingOrchestrator._persist_healing_cycle()` writes to `GraphMemoryBridge` but each domain (LIC, RG, eval, exec, research, rfp) uses siloed entity namespaces. `meta_learning_pipeline` only sees outcomes from execute_ssot, not app-domain healing cycles.
**Enhancement:** `BaseHealingOrchestrator` additionally emits `HealingOutcomeEvent` to cross-domain bus. Wire into `PipelineDependencies.cross_repo_learning_context` (field exists but always `None`).
**Files:** `apps_shared/reasoning/BaseHealingOrchestrator.py`, `system_learning/pipelines/pipeline_factory.py`

---

### #8 — Execute_SSOT: Cognitive Disposition → RCA Enrichment
**Domain:** Execute_SSOT → system_learning | **Value:** Medium | **Effort:** Medium
**Gap:** Phase 1 stores `cognitive_dispositions` on `state_mgr.state` (from `CognitiveDispositionAgent`). `rca_engine` never sees them — only gets raw audit bytes.
**Enhancement:** Serialize `cognitive_dispositions` as supplementary evidence. RCA engine recognizes cognitive markers → richer `RCAFinding` with `cognitive_category`.
**Files:** `agentic_core/L0_routing/scripts/_ssot_meta_learning.py`, `system_learning/engines/rca_engine.py`

---

### #9 — apps_* Telemetry: OpenTelemetry Span → System Learning Telemetry Store
**Domain:** apps_* → system_learning | **Value:** Medium | **Effort:** High
**Gap:** `apps_shared/utils/open_telemetry_tracing_adapter_util.py` produces structured spans (timing, errors, retries) consumed only by OTel exporter. `TelemetryStore` protocol in `meta_learning_pipeline.py` reads from separate store. No bridge exists.
**Enhancement:** New `OTelTelemetryStoreAdapter` implementing `TelemetryStore` protocol. Reads OTel spans, converts to `(timestamp, event_type, payload_bytes)` tuples.
**Files:** `system_learning/adapters/` (new adapter), `system_learning/pipelines/pipeline_factory.py`, `apps_shared/utils/open_telemetry_tracing_adapter_util.py`

---

### #10 — ADG Confidence Tiers → L0 Routing Confidence Monitor
**Domain:** ADG → system_learning | **Value:** Medium | **Effort:** Low
**Gap:** `l0_routing_confidence_monitor.py` has zero visibility into ADG's E9 confidence tiers. When low-confidence edges (443K) exceed high-confidence edges (314K), the monitor doesn't know.
**Enhancement:** Persist `conf_summary` as `SLDriftSummary` entity after ADG build. Confidence monitor reads as baseline signal.
**Files:** `tools/generate_full_adg.py`, `system_learning/engines/l0_routing_confidence_monitor.py`

---

### #11 — L5_safety: Circuit Breaker State → System Learning Signal
**Domain:** L5_safety → system_learning | **Value:** Medium-High | **Effort:** Low
**Gap:** `CircuitBreaker` in `circuit_breaker_gate.py` tracks `CircuitBreakerMetrics` (total_calls, failed_calls, state_transitions, current_backoff) but these metrics are local to each breaker instance. System learning never sees breaker trip patterns.
**Enhancement:** On each state transition (CLOSED→OPEN, OPEN→HALF_OPEN, HALF_OPEN→CLOSED), emit a `CircuitBreakerEvent` to `SystemLearningMemoryBridge`. Pattern analysis can then detect: "breaker X trips every  → underlying issue needs deeper healing".
**Files:** `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` — emit event on `_transition_*`, `system_learning/adapters/system_learning_memory_bridge.py` — new `persist_circuit_breaker_event()`

---

### #12 — prompt_governance: Template Drift → Prompt Drift Detector
**Domain:** prompt_governance → system_learning | **Value:** Medium-High | **Effort:** Low
**Gap:** `detect_template_drift.py` detects instruction drift (hash mismatch between disk and registry) and exits with status code. Results are not forwarded to system learning. Meanwhile, `PromptDriftDetector` in system_learning detects *quality* drift from `PromptOutcomeRecord` windows — but has no awareness of *structural* drift (template modified without version bump).
**Enhancement:** Feed `detect_template_drift()` output (synchronized/drifted lists) into `PromptDriftDetector` as a supplementary structural drift dimension. When structural drift is detected → emit `PromptDriftSignal` with `drift_type="structural"`.
**Files:** `agentic_core/prompt_governance/scripts/detect_template_drift.py` — expose results as data, `system_learning/engines/prompt_drift_detector.py` — add structural drift dimension

---

### #13 — L5_safety: Safety Audit Records → RCA Cluster Engine
**Domain:** L5_safety → system_learning | **Value:** Medium | **Effort:** Medium
**Gap:** `safety_audit_emitter.py` creates `SafetyAuditRecord` objects (policy hash, decision outcome, reason hash, actor, action class) via `SafetyAuditRegistry`. These are persisted locally but never reach system learning. The `RCAClusterEngine` clusters `TraceFeatureRecord` objects — which lack safety audit context.
**Enhancement:** Enrich `TraceFeatureRecord` with optional `safety_audit_outcome` field. When a trace has an associated safety audit record → attach it. Enables clusters like "GUARDRAIL_BLOCK + safety_deny = recurring policy rejection pattern".
**Files:** `system_learning/types/trace_feature_types.py` — add optional field, `system_learning/engines/rca_cluster_engine.py` — factor safety audit into clustering, `agentic_core/L5_safety/audit/safety_audit_emitter.py` — expose query API

---

### #14 — L2_execution: Healing Tier Dispatch Decisions → Meta-Learning
**Domain:** L2_execution → system_learning | **Value:** Medium | **Effort:** Low
**Gap:** `healing_tier_dispatcher.py` routes each `HealingDecision` to LOCAL_AGENT, QWEN_VLLM, or GEMINI_2_5_PRO based on `healing_tier_router.route_healing_tier()`. The tier chosen and its outcome are not fed back to system learning. If QWEN_VLLM consistently fails for a particular failure type, system learning cannot discover this.
**Enhancement:** After dispatch, emit `(failure_type, tier_chosen, outcome, elapsed_ms)` tuple to `HealingOutcomeAggregator`. Pattern analysis can then recommend tier adjustments.
**Files:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — emit outcome, `system_learning/pipelines/meta_learning_pipeline.py` — consume via `PipelineDependencies`

---

### #15 — L2_execution: Resource Prediction → Optimization Proposals
**Domain:** L2_execution → system_learning | **Value:** Medium | **Effort:** Medium
**Gap:** `resource_predictor.py` produces `ResourcePrediction` (deterministic resource envelope from failure signatures) and `rollback_refiner.py` produces `RollbackRefinementDecision` (rollback strategy selection). Neither feeds outcomes to system learning. If predictions are consistently wrong or rollback strategies consistently fail, no feedback loop exists.
**Enhancement:** After execution, compare predicted envelope vs. actual resource usage. Emit `(prediction_accuracy, strategy_id, outcome)` to meta-learning pipeline. `PatternAnalysisEngine` can then detect systematic prediction errors.
**Files:** `agentic_core/L2_execution/engines/resource_predictor.py`, `agentic_core/L2_execution/engines/rollback_refiner.py`, `system_learning/pipelines/meta_learning_pipeline.py`

---

### #16 — L3_orchestration: WorkflowLearningBridge → Meta-Learning Pipeline
**Domain:** L3_orchestration → system_learning | **Value:** Medium-High | **Effort:** Low
**Gap:** `WorkflowLearningBridge` has `register_learner()` + `contribute()` API and records `WorkflowOutcome` (bundle_id, workflow_type, success, elapsed_ms, agent_sequence, quality_score). A global bridge instance exists. **BUT: zero system learning consumers are registered.** The ADG even documents this: "0/204 L3 modules have triggers_learning, feeds_back_signal, or contributes_to_sl edges".
**Enhancement:** Register a system learning consumer via `get_workflow_learning_bridge().register_learner("meta_pipeline", adapter.accept)` during pipeline initialization. `WorkflowOutcome` → `PatternAnalysisEngine` → detect slow or failing workflow patterns.
**Files:** `system_learning/pipelines/pipeline_factory.py` — register learner, `system_learning/adapters/` — new `WorkflowOutcomeSLAdapter`

---

### #17 — apps_eval: Regression Detector → System Learning Drift
**Domain:** apps_eval → system_learning | **Value:** Medium | **Effort:** Low
**Gap:** `RegressionDetector.detect()` compares scorecard results against baseline, flagging REGRESSION/WARN/PASS verdicts. Results are returned to the caller and optionally written to a baseline JSON file — but never forwarded to system learning. Quality regression is a powerful signal for drift detection.
**Enhancement:** After detection, emit `RegressionResult` to `ShadowDriftAnalyzer` as a new quality drift dimension. When `regression_count > 0` → flag `drift_source="eval_regression"` in `DriftSummary`.
**Files:** `apps_eval/engines/regression_detector.py` — emit results, `system_learning/engines/shadow_drift_analyzer.py` — add eval regression dimension

---

### #18 — prompt_governance: Injection Detection Counts → Pattern Analysis
**Domain:** prompt_governance → system_learning | **Value:** Medium | **Effort:** Low
**Gap:** `injection_detector.py` identifies and blocks prompt injection attempts. Detection counts and patterns are logged but not forwarded to system learning. If injection attempts spike against a particular agent or route, system learning has no visibility.
**Enhancement:** Aggregate injection detection events per agent/route per window. Feed as `SecuritySignalGroup` to `SignalGroupingEngine`. Pattern analysis detects: "injection attempts against CampaignPlannerAgent increased 3x → review guardrail configuration".
**Files:** `agentic_core/prompt_governance/security/detectors/injection_detector.py` — emit counts, `system_learning/engines/signal_grouping_engine.py` — add security signal type

---

### #19 — L1_cognition: HealingMemoryRetriever Quality → Retrieval Profile
**Domain:** L1_cognition → system_learning | **Value:** Medium | **Effort:** Medium
**Gap:** `HealingMemoryRetriever` retrieves advisory healing context from FAISS index. Retrieval quality (relevance, hit rate, empty retrieval rate) is not tracked. If the healing memory index degrades or returns irrelevant results, `RetrievalProfileProposalManager` has no signal to adjust retrieval parameters.
**Enhancement:** Track retrieval quality metrics (hit_count, avg_similarity, empty_retrieval_rate) per query window. Feed to `PolicyRecommendationEngine` as retrieval quality signal. Enables: "healing memory retrieval quality dropped 15% → propose index rebuild".
**Files:** `agentic_core/L1_cognition/memory/healing_memory_retriever.py` — emit quality metrics, `system_learning/engines/policy_recommendation_engine.py` — consume retrieval quality

---

### #20 — infrastructure: Cross-Layer Cache Coherence → Drift Detection
**Domain:** infrastructure → system_learning | **Value:** Medium | **Effort:** Medium
**Gap:** `ConsistencyMonitor` in `cross_layer_coherence.py` detects cache inconsistencies across the 4-layer retrieval pattern (version mismatches, checksum failures, stale entries). Resolution history is tracked locally but never reaches system learning. If a layer consistently falls out of sync, it indicates infrastructure drift.
**Enhancement:** Emit `ConsistencyViolationEvent` (layer_type, key, inconsistency_type, resolution) to `SystemLearningMemoryBridge`. `ShadowDriftAnalyzer` adds infrastructure drift dimension.
**Files:** `infrastructure/hardening/cross_layer_coherence.py` — emit events, `system_learning/engines/shadow_drift_analyzer.py` — add infra drift dimension

---

## 3. Priority Matrix

| # | Enhancement | Domain | Value | Effort | Risk |
|---|-------------|--------|-------|--------|------|
| 1 | RCA ↔ ADG Violation Correlation | ADG | **Highest** | Low | Low |
| 2 | Execute_SSOT Phase Outcome Feedback | SSOT | **Very High** | Medium | Low |
| 3 | Hotspot-Aware Healing Priority | ADG | **High** | Low | Low |
| 4 | Repair Route → Optimization Proposals | ADG | **High** | Medium | Low |
| 5 | Violation Trend as Drift Dimension | ADG | **High** | Low | Low |
| 6 | ADG Behavioral Score → Routing Confidence | SSOT | **Med-High** | Low | Low |
| 7 | Cross-Domain Pattern Sharing | apps_* | **Med-High** | Medium | Medium |
| 8 | Cognitive Disposition → RCA Enrichment | SSOT | **Medium** | Medium | Low |
| 9 | OTel Spans → Telemetry Store | apps_* | **Medium** | High | Medium |
| 10 | ADG Confidence Tiers → L0 Monitor | ADG | **Medium** | Low | Low |
| 11 | Circuit Breaker State → SL Signal | L5_safety | **Med-High** | Low | Low |
| 12 | Template Drift → Prompt Drift Detector | prompt_gov | **Med-High** | Low | Low |
| 13 | Safety Audit Records → RCA Clusters | L5_safety | **Medium** | Medium | Low |
| 14 | Healing Tier Dispatch → Meta-Learning | L2_exec | **Medium** | Low | Low |
| 15 | Resource Prediction Feedback | L2_exec | **Medium** | Medium | Medium |
| 16 | WorkflowLearningBridge → Pipeline | L3_orch | **Med-High** | Low | Low |
| 17 | Eval Regression → Drift Detection | apps_eval | **Medium** | Low | Low |
| 18 | Injection Counts → Pattern Analysis | prompt_gov | **Medium** | Low | Low |
| 19 | Healing Memory Retrieval Quality | L1_cog | **Medium** | Medium | Low |
| 20 | Cache Coherence → Drift Detection | infra | **Medium** | Medium | Medium |

---

## 4. Implementation Waves

### Wave A — Quick wins (low effort, high value; ~1 session each)
- **#1** RCA ↔ ADG Violation Correlation
- **#3** Hotspot-Aware Healing Priority
- **#5** Violation Trend as Drift Dimension
- **#6** ADG Behavioral Score → Routing Confidence
- **#10** ADG Confidence Tiers → L0 Monitor
- **#11** Circuit Breaker State → SL Signal
- **#12** Template Drift → Prompt Drift Detector
- **#14** Healing Tier Dispatch → Meta-Learning
- **#16** WorkflowLearningBridge → Pipeline (just register a learner!)
- **#17** Eval Regression → Drift Detection
- **#18** Injection Counts → Pattern Analysis

### Wave B — Medium effort, pipeline wiring (~2-3 sessions each)
- **#2** Execute_SSOT Phase Outcome Feedback
- **#4** Repair Route → Optimization Proposals
- **#8** Cognitive Disposition → RCA Enrichment
- **#13** Safety Audit Records → RCA Clusters
- **#15** Resource Prediction Feedback
- **#19** Healing Memory Retrieval Quality
- **#20** Cache Coherence → Drift Detection

### Wave C — Larger effort, cross-cutting (~3-5 sessions each)
- **#7** Cross-Domain Pattern Sharing
- **#9** OTel Spans → Telemetry Store

---

## 5. Domain Coverage Summary

| Domain | Opportunities | IDs |
|--------|--------------|-----|
| **ADG** | 5 | #1, #3, #4, #5, #10 |
| **Execute_SSOT** | 3 | #2, #6, #8 |
| **apps_*** | 4 | #7, #9, #17 (apps_eval), #7 (cross-domain) |
| **L5_safety** | 2 | #11, #13 |
| **prompt_governance** | 2 | #12, #18 |
| **L2_execution** | 2 | #14, #15 |
| **L3_orchestration** | 1 | #16 |
| **L1_cognition** | 1 | #19 |
| **infrastructure** | 1 | #20 |

---

## 6. Common Design Contracts (All 20)

1. **Informational-only (C0)** — no automatic mutation of routing tiers or safety configs
2. **Proposal-only outputs** — human/gate approval required for any config change
3. **Resilient** — upstream unavailability (ADG, Memory MCP, OTel) = skip, never crash
4. **Deterministic** — same inputs → same outputs; no wall-clock reads
5. **Backward compatible** — all new parameters are optional with sensible defaults
6. **Lifecycle trace compliant** — all new signal paths emit appropriate `_emit_*` lifecycle trace calls
7. **Layer boundary safe** — no new gravity violations; all imports follow L(N) ← L(0..N) rule

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

