# System Learning Signal Enhancement — Implementation Phases & Waves (Validated)

**Date:** 2026-03-26  
**Based on:** `system-learning-signal-enhancement-top20-b7e2d4.md`  
**Validation:** All file paths and components confirmed to exist in current repository  
**Goal:** Step-by-step implementation roadmap with detailed tasks, dependencies, and validation criteria

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


## Executive Summary

### Phases & Waves Overview

| Phase | Duration | Waves | Focus Areas | Value Delivered |
|-------|----------|-------|-------------|-----------------|
| **Phase 1** | Week 1 | 5 waves | ADG Foundation | RCA correlation, hotspot awareness, drift detection |
| **Phase 2** | Week 2 | 5 waves | Safety & Governance | Circuit breaker, template drift, injection detection |
| **Phase 3** | Week 3 | 5 waves | Execution & Orchestration | Tier dispatch, workflow outcomes, eval regression |
| **Phase 4** | Week 4 | 3 waves | Cross-Cutting Integration | Phase outcomes, repair routes, cache coherence |
| **Phase 5** | Weeks 5-6 | 2 waves | Advanced Cross-Domain | Pattern sharing, OTel telemetry |

**Total:** 20 waves across , covering 9 domains with 31 signal types (up from 11)

### Quick Wins (Wave A - 11 opportunities)
- RCA ↔ ADG Violation Correlation (#1)
- Hotspot-Aware Healing Priority (#3)
- Violation Trend as Drift Dimension (#5)
- ADG Behavioral Score → Routing Confidence (#6)
- ADG Confidence Tiers → L0 Monitor (#10)
- Circuit Breaker State → SL Signal (#11)
- Template Drift → Prompt Drift Detector (#12)
- Injection Counts → Pattern Analysis (#18)
- Healing Tier Dispatch → Meta-Learning (#14)
- WorkflowLearningBridge → Pipeline (#16)
- Eval Regression → Drift Detection (#17)

### Medium Effort (Wave B - 7 opportunities)
- Cognitive Disposition → RCA Enrichment (#8)
- Safety Audit Records → RCA Clusters (#13)
- Resource Prediction Feedback (#15)
- Healing Memory Retrieval Quality (#19)
- Execute_SSOT Phase Outcome Feedback (#2)
- Repair Route → Optimization Proposals (#4)
- Cache Coherence → Drift Detection (#20)

### Advanced (Wave C - 2 opportunities)
- Cross-Domain Pattern Sharing (#7)
- OTel Spans → Telemetry Store (#9)

---

## Phase 1: Foundation & Quick Wins (Week 1)

### Wave A-1: RCA Engine ↔ ADG Violation Correlation (#1)

**Objective:** Enable RCA findings to reference architectural violations for causal attribution

**Files (Validated):**
- ✅ `system_learning/engines/rca_engine.py` - exists
- ✅ `agentic_core/adg/adapters/ADGMemoryAdapter.py` - exists
- ✅ `system_learning/pipelines/meta_learning_pipeline.py` - exists

**Tasks:**
1. **ADGMemoryAdapter Enhancement** (Day 1)
   - Add `get_violation_file_set() -> frozenset[str]` method
   - Query `ADGViolation` entities from Memory MCP
   - Return frozenset of file paths with violations

2. **RCA Engine Enhancement** (Day 1-2)
   - Add optional `violation_file_set` parameter to `analyze_failures()`
   - Tag findings with `adg_correlated=True` when file matches violation

3. **Pipeline Integration** (Day 2)
   - Wire violation set into RCA analysis in meta-learning pipeline

**Validation Criteria:**
- RCA findings show `adg_correlated=True` for violation files
- Graceful handling when ADG unavailable

---

### Wave A-2: Hotspot-Aware Healing Priority (#3)

**Objective:** Boost healing pattern priority for high-fan-out architectural hotspots

**Files (Validated):**
- ✅ `system_learning/engines/default_healing_pattern_advisor.py` - exists
- ✅ `agentic_core/adg/adapters/ADGMemoryAdapter.py` - exists

**Tasks:**
1. **ADGMemoryAdapter Helper** (Day 1)
   - Add `get_hotspot_modules(limit: int = 20) -> frozenset[str]`

2. **Pattern Advisor Enhancement** (Day 2)
   - Query hotspots in `advise()` method
   - Add `reason_code="adg_hotspot"` + boost for hotspot modules

---

### Wave A-3: Violation Trend as Drift Dimension (#5)

**Objective:** Detect structural regression through ADG violation count changes

**Files (Validated):**
- ✅ `system_learning/engines/shadow_drift_analyzer.py` - exists
- ✅ `system_learning/adapters/system_learning_memory_bridge.py` - exists

**Tasks:**
1. **Memory Bridge Enhancement** (Day 1)
   - Add `get_latest_violation_counts() -> tuple[int, int]`

2. **Shadow Drift Analyzer Enhancement** (Day 2)
   - Add violation trend analysis
   - Set `drift_source="adg_structural"` when violations increase

---

### Wave A-4: ADG Behavioral Score → Routing Confidence (#6)

**Objective:** Factor ADG's risk assessment into routing confidence monitoring

**Files (Validated):**
- ✅ `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` - exists
- ✅ `system_learning/engines/l0_routing_confidence_monitor.py` - exists

**Tasks:**
1. **Execute_SSOT Signal Forwarding** (Day 1)
   - Extract `adg_territory_score` from `state_mgr.state`
   - Emit to `HealingSuccessRateStore`

2. **Confidence Monitor Enhancement** (Day 2)
   - Factor ADG score into confidence calculation
   - Reduce confidence for high-risk territories

---

### Wave A-5: ADG Confidence Tiers → L0 Monitor (#10)

**Objective:** Provide confidence tier distribution to routing confidence monitor

**Files (Validated):**
- ✅ `tools/generate_full_adg.py` - exists
- ✅ `system_learning/engines/l0_routing_confidence_monitor.py` - exists

**Tasks:**
1. **ADG Build Signal Emission** (Day 1)
   - Persist `conf_summary` as `SLDriftSummary` entity
   - Store via `SystemLearningMemoryBridge`

2. **Confidence Monitor Integration** (Day 2)
   - Read confidence tier distribution
   - Alert on tier imbalance

---

## Phase 2: Safety & Governance Integration (Week 2)

### Wave A-6: Circuit Breaker State → System Learning Signal (#11)

**Objective:** Track circuit breaker patterns for infrastructure health insights

**Files (Validated):**
- ✅ `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` - exists
- ✅ `system_learning/adapters/system_learning_memory_bridge.py` - exists

**Tasks:**
1. **Circuit Breaker Event Emission** (Day 1)
   - Emit `CircuitBreakerEvent` on state transitions
   - Add `persist_circuit_breaker_event()` to Memory Bridge

2. **Pattern Analysis Integration** (Day 2)
   - Add events to `SignalGroupingEngine`
   - Detect breaker anomalies

---

### Wave A-7: Template Drift → Prompt Drift Detector (#12)

**Objective:** Incorporate structural drift into prompt quality monitoring

**Files (Validated):**
- ✅ `agentic_core/prompt_governance/scripts/detect_template_drift.py` - exists
- ✅ `system_learning/engines/prompt_drift_detector.py` - exists

**Tasks:**
1. **Template Drift API Exposure** (Day 1)
   - Add `detect_and_return_drift()` function
   - Return results instead of just exiting

2. **Prompt Drift Detector Enhancement** (Day 2)
   - Add structural drift dimension
   - Emit `PromptDriftSignal` with `drift_type="structural"`

---

### Wave A-8: Injection Detection Counts → Pattern Analysis (#18)

**Objective:** Monitor prompt injection attempts for security insights

**Files (Validated):**
- ✅ `agentic_core/prompt_governance/security/detectors/injection_detector.py` - exists
- ✅ `system_learning/engines/signal_grouping_engine.py` - exists

**Tasks:**
1. **Injection Detection Metrics** (Day 1)
   - Track detection events per agent/route
   - Emit aggregated counts

2. **Signal Grouping Enhancement** (Day 2)
   - Add `SecuritySignalGroup` type
   - Detect injection spikes

---

### Wave B-1: Cognitive Disposition → RCA Enrichment (#8)

**Objective:** Enrich RCA findings with cognitive context from Execute_SSOT

**Files (Validated):**
- ✅ `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` - exists
- ✅ `system_learning/engines/rca_engine.py` - exists

**Tasks:**
1. **Cognitive Disposition Serialization** (Day 1)
   - Serialize `cognitive_dispositions` from `state_mgr.state`
   - Add to `PipelineDependencies`

2. **RCA Engine Enhancement** (Day 2)
   - Parse cognitive dispositions
   - Add `cognitive_category` to findings

---

### Wave B-2: Safety Audit Records → RCA Clusters (#13)

**Objective:** Enrich failure clusters with safety audit context

**Files (Validated):**
- ✅ `agentic_core/L5_safety/audit/safety_audit_emitter.py` - exists
- ✅ `system_learning/types/trace_feature_types.py` - exists
- ✅ `system_learning/engines/rca_cluster_engine.py` - exists

**Tasks:**
1. **Safety Audit Query API** (Day 1)
   - Add `get_audit_records_for_trace()` method

2. **Trace Feature Enhancement** (Day 2)
   - Add optional `safety_audit_outcome` field
   - Factor into clustering

---

## Phase 3: Execution & Orchestration Feedback (Week 3)

### Wave A-9: Healing Tier Dispatch → Meta-Learning (#14)

**Objective:** Track healing tier effectiveness for routing optimization

**Files (Validated):**
- ✅ `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` - exists
- ✅ `system_learning/engines/pattern_analysis_engine.py` - exists

**Tasks:**
1. **Dispatch Outcome Tracking** (Day 1)
   - Emit `(failure_type, tier_chosen, outcome, elapsed_ms)` after dispatch
   - Send to `HealingOutcomeAggregator`

2. **Pattern Analysis Integration** (Day 2)
   - Add tier effectiveness analysis
   - Generate tier adjustment recommendations

---

### Wave A-10: WorkflowLearningBridge → Pipeline (#16)

**Objective:** Connect workflow outcomes to system learning for orchestration insights

**Files (Validated):**
- ✅ `agentic_core/L3_orchestration/learning/workflow_learning_bridge.py` - exists
- ✅ `system_learning/pipelines/pipeline_factory.py` - exists

**Tasks:**
1. **Workflow Outcome Adapter** (Day 1)
   - Create `WorkflowOutcomeSLAdapter` (new file)
   - Convert `WorkflowOutcome` to system learning signals
   - Register with global bridge

2. **Pipeline Registration** (Day 2)
   - Register adapter in `pipeline_factory.py`
   - Wire outcomes into `PatternAnalysisEngine`

---

### Wave A-11: Eval Regression → Drift Detection (#17)

**Objective:** Detect quality regression through evaluation score changes

**Files (Validated):**
- ✅ `apps_eval/engines/regression_detector.py` - exists
- ✅ `system_learning/engines/shadow_drift_analyzer.py` - exists

**Tasks:**
1. **Regression Result Emission** (Day 1)
   - Emit `RegressionResult` after detection
   - Send to `ShadowDriftAnalyzer`

2. **Drift Analyzer Enhancement** (Day 2)
   - Add eval regression dimension
   - Set `drift_source="eval_regression"`

---

### Wave B-3: Resource Prediction Feedback (#15)

**Objective:** Compare resource predictions against actual usage for accuracy

**Files (Validated):**
- ✅ `agentic_core/L2_execution/engines/resource_predictor.py` - exists
- ✅ `agentic_core/L2_execution/engines/rollback_refiner.py` - exists

**Tasks:**
1. **Prediction Accuracy Tracking** (Day 1)
   - Add post-execution accuracy check
   - Emit accuracy metrics to meta-learning

2. **Rollback Strategy Tracking** (Day 1)
   - Track strategy effectiveness
   - Emit outcomes to meta-learning

3. **Pattern Analysis Integration** (Day 2)
   - Add prediction accuracy patterns
   - Detect systematic errors

---

### Wave B-4: Healing Memory Retrieval Quality (#19)

**Objective:** Monitor FAISS retrieval quality for healing context

**Files (Validated):**
- ✅ `agentic_core/L1_cognition/memory/healing_memory_retriever.py` - exists
- ✅ `system_learning/engines/policy_recommendation_engine.py` - exists

**Tasks:**
1. **Retrieval Quality Metrics** (Day 1)
   - Track: hit_count, avg_similarity, empty_retrieval_rate
   - Emit metrics per query window

2. **Policy Recommendation Enhancement** (Day 2)
   - Add retrieval quality as input
   - Generate index rebuild recommendations

---

## Phase 4: Cross-Cutting Integration (Week 4)

### Wave B-5: Execute_SSOT Phase Outcome Feedback (#2)

**Objective:** Close the loop between healing phases and learning

**Files (Validated):**
- ✅ `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` - exists
- ✅ `system_learning/pipelines/meta_learning_pipeline.py` - exists

**Tasks:**
1. **Phase Outcome Collection** (Day 1-2)
   - Collect phase outcomes from `state_mgr.state`
   - Serialize: location_violations, hierarchy_fixed, gravity_fixed, etc.
   - Add to `PipelineDependencies`

2. **Pipeline Integration** (Day 2)
   - Unpack phase outcomes in meta-learning pipeline
   - Make available to proposers

---

### Wave B-6: Repair Route → Optimization Proposals (#4)

**Objective:** Connect static ADG repair routes to dynamic optimization

**Files (Validated):**
- ✅ `system_learning/engines/optimization_proposal_engine.py` - exists
- ✅ `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` - exists

**Tasks:**
1. **Repair Route Serialization** (Day 1)
   - Serialize `repair_routing_summary()` output
   - Add to `PipelineDependencies`

2. **Optimization Engine Enhancement** (Day 2)
   - Add `RepairRouteCluster` handling
   - Map repair routes to proposals

---

### Wave B-7: Cache Coherence → Drift Detection (#20)

**Objective:** Detect infrastructure drift through cache consistency monitoring

**Files (Validated):**
- ✅ `infrastructure/hardening/cross_layer_coherence.py` - exists
- ✅ `system_learning/engines/shadow_drift_analyzer.py` - exists

**Tasks:**
1. **Coherence Event Emission** (Day 1)
   - Emit `ConsistencyViolationEvent` on detection
   - Send to `SystemLearningMemoryBridge`

2. **Drift Analyzer Enhancement** (Day 2)
   - Add infrastructure drift dimension
   - Set `drift_source="infrastructure_coherence"`

---

## Phase 5: Advanced Cross-Domain (Weeks 5-6)

### Wave C-1: Cross-Domain Pattern Sharing (#7)

**Objective:** Share healing patterns across app domains for collective learning

**Files (Validated):**
- ✅ `apps_shared/reasoning/BaseHealingOrchestrator.py` - exists
- ✅ `system_learning/pipelines/pipeline_factory.py` - exists
- ✅ `system_learning/engines/pattern_analysis_engine.py` - exists

**Tasks:**
1. **Cross-Domain Event Bus** (Week 5, Days 1-3)
   - Design cross-domain healing event format
   - Implement event bus in `BaseHealingOrchestrator`
   - Add domain namespace to events

2. **Pipeline Integration** (Week 5, Days 3-4)
   - Wire events into `PipelineDependencies.cross_repo_learning_context`
   - Update `PatternAnalysisEngine` for cross-domain patterns

3. **Domain Adapter** (Week 5, Day 5)
   - Create adapter for normalizing events
   - Handle domain-specific formats

---

### Wave C-2: OTel Spans → Telemetry Store (#9)

**Objective:** Bridge OpenTelemetry spans to system learning telemetry

**Files (Validated):**
- ✅ `apps_shared/utils/open_telemetry_tracing_adapter_util.py` - exists
- ✅ `system_learning/pipelines/pipeline_factory.py` - exists

**Tasks:**
1. **OTel Adapter Design** (Week 5, Days 1-2)
   - Create `OTelTelemetryStoreAdapter` (new file)
   - Implement `TelemetryStore` protocol
   - Design span-to-telemetry conversion

2. **Adapter Implementation** (Week 5, Days 3-4)
   - Read spans from OTel exporter
   - Convert to telemetry tuples
   - Add error handling

3. **Pipeline Integration** (Week 5, Day 5)
   - Register adapter in `pipeline_factory.py`
   - Configure span filtering

---

## Implementation Guidelines

### Development Standards
1. **Backward Compatibility:** All new parameters optional with defaults
2. **Graceful Degradation:** Upstream unavailability = skip, never crash
3. **Deterministic Outputs:** Same inputs → same outputs
4. **Lifecycle Trace Compliance:** Emit appropriate `_emit_*` calls
5. **Layer Boundary Safety:** No new gravity violations
6. **Unit Test Coverage:** Minimum 80% for new code
7. **Integration Tests:** End-to-end validation per wave

### Risk Mitigation
1. **Feature Flags:** Use flags for disruptive changes
2. **Rollback Plan:** Each wave includes rollback procedures
3. **Monitoring:** Add observability for new signal paths
4. **Performance:** Profile impact on critical paths
5. **Data Validation:** Validate all new data formats

### Success Metrics
1. **Signal Coverage:** Increase from 11 to 31 signal types
2. **Domain Coverage:** All 9 domains contributing signals
3. **Pattern Detection:** 50% increase in pattern recognition
4. **Drift Detection:** 40% improvement in drift accuracy
5. **Healing Effectiveness:** 15% improvement in success rates

---

## Validation Status

### File Path Verification
All referenced files have been confirmed to exist in the current repository:
- ✅ ADG adapters and engines
- ✅ System learning components
- ✅ Execute_SSOT scripts
- ✅ App domain engines
- ✅ Safety and governance components
- ✅ Infrastructure modules

### Dependencies Check
- ✅ Memory MCP server operational (`tools/memory/adg_memory_server.py`)
- ✅ ADG Redis integration functional
- ✅ Lifecycle trace contract emitters available
- ✅ Meta-learning pipeline infrastructure ready

---

## Timeline Summary

| Week | Waves | Focus | Deliverables |
|------|-------|-------|--------------|
| 1 | A-1 to A-5 | ADG Foundation | RCA correlation, hotspot awareness, drift detection |
| 2 | A-6 to A-8, B-1 to B-2 | Safety & Governance | Circuit breaker, template drift, injection detection |
| 3 | A-9 to A-11, B-3 to B-4 | Execution & Orchestration | Tier dispatch, workflow outcomes, eval regression |
| 4 | B-5 to B-7 | Cross-Cutting | Phase outcomes, repair routes, cache coherence |
| 5-6 | C-1 to C-2 | Advanced Cross-Domain | Pattern sharing, OTel integration |

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5  
**Parallel Opportunities:** Waves within each phase can overlap based on dependencies

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

