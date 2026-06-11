---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\system-learning-signal-enhancement-implementation-phases-4f8c2e.md'
original_relative_path: 'system-learning-signal-enhancement-implementation-phases-4f8c2e.md'
source_sha256: aa5aa24912d9247b660aaa8e2729f1efcd1be1009907d91a917c0009efa45883
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# System Learning Signal Enhancement — Detailed Implementation Phases & Waves

**Date:** 2026-03-25
**Based on:** `system-learning-signal-enhancement-top20-b7e2d4.md`
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


## Phase Structure Overview

### Phase 1: Foundation & Quick Wins (Week 1)
- **Wave A-1:** ADG Violation Correlation (#1)
- **Wave A-2:** Hotspot-Aware Healing Priority (#3)
- **Wave A-3:** Violation Trend as Drift Dimension (#5)
- **Wave A-4:** ADG Behavioral Score → Routing Confidence (#6)
- **Wave A-5:** ADG Confidence Tiers → L0 Monitor (#10)

### Phase 2: Safety & Governance Integration (Week 2)
- **Wave A-6:** Circuit Breaker State → SL Signal (#11)
- **Wave A-7:** Template Drift → Prompt Drift Detector (#12)
- **Wave A-8:** Injection Counts → Pattern Analysis (#18)
- **Wave B-1:** Cognitive Disposition → RCA Enrichment (#8)
- **Wave B-2:** Safety Audit Records → RCA Clusters (#13)

### Phase 3: Execution & Orchestration Feedback (Week 3)
- **Wave A-9:** Healing Tier Dispatch → Meta-Learning (#14)
- **Wave A-10:** WorkflowLearningBridge → Pipeline (#16)
- **Wave A-11:** Eval Regression → Drift Detection (#17)
- **Wave B-3:** Resource Prediction Feedback (#15)
- **Wave B-4:** Healing Memory Retrieval Quality (#19)

### Phase 4: Cross-Cutting Integration (Week 4)
- **Wave B-5:** Execute_SSOT Phase Outcome Feedback (#2)
- **Wave B-6:** Repair Route → Optimization Proposals (#4)
- **Wave B-7:** Cache Coherence → Drift Detection (#20)

### Phase 5: Advanced Cross-Domain (Week 5-6)
- **Wave C-1:** Cross-Domain Pattern Sharing (#7)
- **Wave C-2:** OTel Spans → Telemetry Store (#9)

---

## Phase 1: Foundation & Quick Wins (Week 1)

### Wave A-1: RCA Engine ↔ ADG Violation Correlation (#1)

**Objective:** Enable RCA findings to reference architectural violations for causal attribution

**Tasks:**
1. **ADGMemoryAdapter Enhancement** (Day 1)
   - Add `get_violation_file_set() -> frozenset[str]` method
   - Query `ADGViolation` entities from Memory MCP
   - Extract `source=` observation values
   - Return frozenset of file paths with violations

2. **RCA Engine Enhancement** (Day 1-2)
   - Add optional `violation_file_set: frozenset[str] | None = None` parameter to `analyze_failures()`
   - For each `FailureLine`, check if file path in violation set
   - If matched: tag `RCAFinding` with `adg_correlated=True` and `violation_type="layer_boundary"`
   - Maintain backward compatibility (parameter optional)

3. **Pipeline Integration** (Day 2)
   - In `meta_learning_pipeline.py`, call `ADGMemoryAdapter.get_violation_file_set()`
   - Pass to `rca_engine.analyze_failures()` call
   - Handle ADG unavailability gracefully (skip correlation)

**Validation Criteria:**
- RCA findings for files with violations show `adg_correlated=True`
- Pipeline runs successfully when ADG unavailable
- No regression in existing RCA functionality
- Unit tests for new correlation logic

**Files Modified:**
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` (+15 lines)
- `system_learning/engines/rca_engine.py` (+25 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (+8 lines)

---

### Wave A-2: Hotspot-Aware Healing Priority (#3)

**Objective:** Boost healing pattern priority for high-fan-out architectural hotspots

**Tasks:**
1. **ADGMemoryAdapter Helper** (Day 1)
   - Add `get_hotspot_modules(limit: int = 20) -> frozenset[str]` method
   - Query `ADGHotspot` entities sorted by fan-out
   - Return top N module names

2. **Pattern Advisor Enhancement** (Day 2)
   - Import hotspot helper in `default_healing_pattern_advisor.py`
   - In `advise()` method, query hotspots for failing module
   - If module in hotspot set: add `reason_code="adg_hotspot"` + boost multiplier
   - Cap boost by existing `_MAX_PATTERN_BOOST`

3. **Testing** (Day 2)
   - Verify hotspot modules receive higher boost
   - Test with empty hotspot set gracefully

**Validation Criteria:**
- Hotspot modules receive additional boost in `PatternAdvice`
- Non-hotspot modules unchanged
- Graceful handling when ADG unavailable
- No impact on existing healing patterns

**Files Modified:**
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` (+12 lines)
- `system_learning/engines/default_healing_pattern_advisor.py` (+18 lines)

---

### Wave A-3: Violation Trend as Drift Dimension (#5)

**Objective:** Detect structural regression through ADG violation count changes

**Tasks:**
1. **Memory Bridge Enhancement** (Day 1)
   - Add `get_latest_violation_counts() -> tuple[int, int]` method
   - Query two most recent `ADGSnapshot` entities
   - Return (current_count, previous_count)

2. **Shadow Drift Analyzer Enhancement** (Day 2)
   - Add violation trend analysis to `analyze_drift()`
   - Compute `violation_delta = current - previous`
   - If `violation_delta > 0`: set `drift_flag=True`, add `drift_source="adg_structural"`
   - Integrate into existing `DriftSummary` output

3. **Pipeline Integration** (Day 2)
   - Call violation trend analysis in meta-learning pipeline
   - Handle insufficient snapshots gracefully

**Validation Criteria:**
- Violation increase triggers structural drift flag
- Drift summary includes ADG structural dimension
- No drift when violation count stable/decreased
- Graceful with <2 snapshots

**Files Modified:**
- `system_learning/adapters/system_learning_memory_bridge.py` (+20 lines)
- `system_learning/engines/shadow_drift_analyzer.py` (+15 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (+6 lines)

---

### Wave A-4: ADG Behavioral Score → Routing Confidence (#6)

**Objective:** Factor ADG's risk assessment into routing confidence monitoring

**Tasks:**
1. **Execute_SSOT Signal Forwarding** (Day 1)
   - In `_ssot_meta_learning.py`, extract `adg_territory_score` from `state_mgr.state`
   - Emit as `(territory, score)` tuple to `HealingSuccessRateStore`

2. **Confidence Monitor Enhancement** (Day 2)
   - Add ADG score as optional input to confidence calculation
   - If ADG score < threshold (0.7), reduce routing confidence
   - Weight ADG score alongside existing signals

3. **Integration Testing** (Day 2)
   - Verify confidence adjustment with high ADG risk scores
   - Test with missing ADG scores

**Validation Criteria:**
- High ADG risk scores lower routing confidence
- Missing scores don't crash confidence monitor
- Existing confidence logic preserved

**Files Modified:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (+10 lines)
- `system_learning/engines/l0_routing_confidence_monitor.py` (+15 lines)

---

### Wave A-5: ADG Confidence Tiers → L0 Monitor (#10)

**Objective:** Provide confidence tier distribution to routing confidence monitor

**Tasks:**
1. **ADG Build Signal Emission** (Day 1)
   - In `generate_full_adg.py`, after ADG build, persist `conf_summary`
   - Create `SLDriftSummary` entity with confidence tier counts
   - Store via `SystemLearningMemoryBridge`

2. **Confidence Monitor Integration** (Day 2)
   - Add method to read latest confidence tier distribution
   - Factor tier imbalance into confidence score
   - Alert if low-confidence edges exceed high-confidence

3. **Validation** (Day 2)
   - Verify tier distribution affects confidence
   - Test with missing confidence data

**Validation Criteria:**
- Tier imbalance detected and reported
- Confidence score reflects tier distribution
- No failure when confidence data unavailable

**Files Modified:**
- `tools/generate_full_adg.py` (+8 lines)
- `system_learning/engines/l0_routing_confidence_monitor.py` (+20 lines)

---

## Phase 2: Safety & Governance Integration (Week 2)

### Wave A-6: Circuit Breaker State → System Learning Signal (#11)

**Objective:** Track circuit breaker patterns for infrastructure health insights

**Tasks:**
1. **Circuit Breaker Event Emission** (Day 1)
   - In `circuit_breaker_gate.py`, add event emission on state transitions
   - Emit `CircuitBreakerEvent` with: breaker_id, old_state, new_state, timestamp, metrics
   - Call new `SystemLearningMemoryBridge.persist_circuit_breaker_event()`

2. **Memory Bridge Enhancement** (Day 1)
   - Add `persist_circuit_breaker_event()` method
   - Store as `CircuitBreakerEvent` entity with observations
   - Create relations to breaker instance

3. **Pattern Analysis Integration** (Day 2)
   - Add circuit breaker events to `SignalGroupingEngine`
   - Detect patterns: frequent trips, slow recovery, stuck states

**Validation Criteria:**
- State transitions persisted to Memory MCP
- Pattern analysis detects breaker anomalies
- No impact on breaker performance

**Files Modified:**
- `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` (+15 lines)
- `system_learning/adapters/system_learning_memory_bridge.py` (+25 lines)
- `system_learning/engines/signal_grouping_engine.py` (+10 lines)

---

### Wave A-7: Template Drift → Prompt Drift Detector (#12)

**Objective:** Incorporate structural drift into prompt quality monitoring

**Tasks:**
1. **Template Drift API Exposure** (Day 1)
   - Modify `detect_template_drift.py` to return results instead of just exiting
   - Add `detect_and_return_drift() -> tuple[list[dict], list[dict]]` function
   - Keep CLI behavior unchanged for existing usage

2. **Prompt Drift Detector Enhancement** (Day 2)
   - Add structural drift dimension to `detect_prompt_drift()`
   - Call template drift detection as part of analysis
   - Emit `PromptDriftSignal` with `drift_type="structural"` when drift detected

3. **Integration** (Day 2)
   - Wire structural drift into existing drift pipeline
   - Ensure structural and quality drift both reported

**Validation Criteria:**
- Template modifications trigger structural drift signals
- Both structural and quality drift dimensions reported
- No impact on existing prompt drift detection

**Files Modified:**
- `agentic_core/prompt_governance/scripts/detect_template_drift.py` (+20 lines)
- `system_learning/engines/prompt_drift_detector.py` (+25 lines)

---

### Wave A-8: Injection Detection Counts → Pattern Analysis (#18)

**Objective:** Monitor prompt injection attempts for security insights

**Tasks:**
1. **Injection Detection Metrics** (Day 1)
   - In `injection_detector.py`, add per-agent/route counting
   - Track detection events with: agent, route, timestamp, injection_type
   - Emit aggregated counts to system learning bus

2. **Signal Grouping Enhancement** (Day 2)
   - Add `SecuritySignalGroup` type to `SignalGroupingEngine`
   - Process injection detection events
   - Generate patterns for spike detection

3. **Pattern Analysis** (Day 2)
   - Detect injection attempt spikes against specific agents
   - Alert on recurring injection patterns

**Validation Criteria:**
- Injection attempts tracked per agent/route
- Spike detection triggers alerts
- No performance impact on injection detection

**Files Modified:**
- `agentic_core/prompt_governance/security/detectors/injection_detector.py` (+20 lines)
- `system_learning/engines/signal_grouping_engine.py` (+15 lines)

---

### Wave B-1: Cognitive Disposition → RCA Enrichment (#8)

**Objective:** Enrich RCA findings with cognitive context from Execute_SSOT

**Tasks:**
1. **Cognitive Disposition Serialization** (Day 1)
   - In `_ssot_meta_learning.py`, serialize `cognitive_dispositions` from `state_mgr.state`
   - Add to `PipelineDependencies` as `cognitive_dispositions_bytes`

2. **RCA Engine Enhancement** (Day 2)
   - Parse cognitive dispositions in `analyze_failures()`
   - Match cognitive markers to failure patterns
   - Add `cognitive_category` to enriched `RCAFinding`

3. **Testing** (Day 2)
   - Verify cognitive categories appear in findings
   - Test with missing cognitive data

**Validation Criteria:**
- RCA findings include cognitive context when available
- Cognitive categories help explain failure patterns
- Graceful handling of missing data

**Files Modified:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (+8 lines)
- `system_learning/engines/rca_engine.py` (+20 lines)

---

### Wave B-2: Safety Audit Records → RCA Clusters (#13)

**Objective:** Enrich failure clusters with safety audit context

**Tasks:**
1. **Safety Audit Query API** (Day 1)
   - Add `get_audit_records_for_trace(trace_id: str) -> list[SafetyAuditRecord]` to `safety_audit_emitter.py`
   - Enable lookup of audit records by trace ID

2. **Trace Feature Enhancement** (Day 2)
   - Add optional `safety_audit_outcome` field to `TraceFeatureRecord`
   - Populate when audit record exists for trace

3. **RCA Cluster Engine Enhancement** (Day 2)
   - Factor safety audit outcomes into clustering
   - Create clusters like "GUARDRAIL_BLOCK + safety_deny"

**Validation Criteria:**
- Clusters include safety audit context
- Safety rejection patterns identified
- No impact on existing clustering

**Files Modified:**
- `system_learning/types/trace_feature_types.py` (+5 lines)
- `system_learning/engines/rca_cluster_engine.py` (+25 lines)
- `agentic_core/L5_safety/audit/safety_audit_emitter.py` (+10 lines)

---

## Phase 3: Execution & Orchestration Feedback (Week 3)

### Wave A-9: Healing Tier Dispatch → Meta-Learning (#14)

**Objective:** Track healing tier effectiveness for routing optimization

**Tasks:**
1. **Dispatch Outcome Tracking** (Day 1)
   - In `healing_tier_dispatcher.py`, emit `(failure_type, tier_chosen, outcome, elapsed_ms)` after each dispatch
   - Send to `HealingOutcomeAggregator` via existing channel

2. **Pattern Analysis Integration** (Day 2)
   - Add tier effectiveness analysis to `PatternAnalysisEngine`
   - Detect patterns: "QWEN_VLLM consistently fails for SYNTAX errors"
   - Generate tier adjustment recommendations

3. **Validation** (Day 2)
   - Verify tier outcomes tracked
   - Test pattern detection for tier effectiveness

**Validation Criteria:**
- Tier choices and outcomes recorded
- Pattern analysis identifies tier-specific failures
- Recommendations for tier adjustments generated

**Files Modified:**
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (+15 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (+6 lines)
- `system_learning/engines/pattern_analysis_engine.py` (+20 lines)

---

### Wave A-10: WorkflowLearningBridge → Pipeline (#16)

**Objective:** Connect workflow outcomes to system learning for orchestration insights

**Tasks:**
1. **Workflow Outcome Adapter** (Day 1)
   - Create `WorkflowOutcomeSLAdapter` implementing workflow outcome consumer interface
   - Convert `WorkflowOutcome` to system learning signals
   - Register with global `WorkflowLearningBridge`

2. **Pipeline Registration** (Day 2)
   - In `pipeline_factory.py`, register adapter during pipeline initialization
   - Wire workflow outcomes into `PatternAnalysisEngine`

3. **Testing** (Day 2)
   - Verify workflow outcomes reach system learning
   - Test pattern detection for workflow issues

**Validation Criteria:**
- Workflow outcomes consumed by system learning
- Pattern analysis detects workflow issues
- No impact on existing workflow execution

**Files Modified:**
- `system_learning/adapters/workflow_outcome_sl_adapter.py` (new, +80 lines)
- `system_learning/pipelines/pipeline_factory.py` (+8 lines)

---

### Wave A-11: Eval Regression → Drift Detection (#17)

**Objective:** Detect quality regression through evaluation score changes

**Tasks:**
1. **Regression Result Emission** (Day 1)
   - In `regression_detector.py`, emit `RegressionResult` after detection
   - Send to `ShadowDriftAnalyzer` as quality drift signal

2. **Drift Analyzer Enhancement** (Day 2)
   - Add eval regression dimension to drift analysis
   - Set `drift_source="eval_regression"` when regressions detected
   - Integrate into `DriftSummary`

3. **Validation** (Day 2)
   - Verify quality regressions trigger drift signals
   - Test drift summary includes eval dimension

**Validation Criteria:**
- Evaluation regressions detected as drift
- Drift summary includes eval regression source
- No impact on existing regression detection

**Files Modified:**
- `apps_eval/engines/regression_detector.py` (+10 lines)
- `system_learning/engines/shadow_drift_analyzer.py` (+15 lines)

---

### Wave B-3: Resource Prediction Feedback (#15)

**Objective:** Compare resource predictions against actual usage for accuracy

**Tasks:**
1. **Prediction Accuracy Tracking** (Day 1)
   - In `resource_predictor.py`, add post-execution accuracy check
   - Compare predicted envelope vs actual resource usage
   - Emit `(prediction_accuracy, strategy_id, outcome)` to meta-learning

2. **Rollback Strategy Tracking** (Day 1)
   - In `rollback_refiner.py`, track strategy effectiveness
   - Emit strategy outcomes to meta-learning

3. **Pattern Analysis Integration** (Day 2)
   - Add prediction accuracy patterns to `PatternAnalysisEngine`
   - Detect systematic prediction errors

**Validation Criteria:**
- Prediction accuracy tracked and reported
- Rollback strategy effectiveness monitored
- Pattern analysis identifies prediction issues

**Files Modified:**
- `agentic_core/L2_execution/engines/resource_predictor.py` (+20 lines)
- `agentic_core/L2_execution/engines/rollback_refiner.py` (+15 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (+6 lines)

---

### Wave B-4: Healing Memory Retrieval Quality (#19)

**Objective:** Monitor FAISS retrieval quality for healing context

**Tasks:**
1. **Retrieval Quality Metrics** (Day 1)
   - In `healing_memory_retriever.py`, track quality metrics
   - Monitor: hit_count, avg_similarity, empty_retrieval_rate
   - Emit metrics per query window

2. **Policy Recommendation Enhancement** (Day 2)
   - Add retrieval quality as input to `PolicyRecommendationEngine`
   - Generate recommendations for index rebuild when quality drops

3. **Validation** (Day 2)
   - Verify retrieval quality tracked
   - Test index rebuild recommendations

**Validation Criteria:**
- Retrieval quality metrics collected
- Quality degradation triggers recommendations
- No impact on retrieval performance

**Files Modified:**
- `agentic_core/L1_cognition/memory/healing_memory_retriever.py` (+25 lines)
- `system_learning/engines/policy_recommendation_engine.py` (+15 lines)

---

## Phase 4: Cross-Cutting Integration (Week 4)

### Wave B-5: Execute_SSOT Phase Outcome Feedback (#2)

**Objective:** Close the loop between healing phases and learning

**Tasks:**
1. **Phase Outcome Collection** (Day 1-2)
   - In `_ssot_meta_learning.py`, collect phase outcomes from `state_mgr.state`
   - Serialize: `location_violations`, `hierarchy_fixed`, `gravity_fixed`, `classification_violations`, `compliance_scores`
   - Add to `PipelineDependencies` as `phase_outcomes_bytes`

2. **Pipeline Integration** (Day 2)
   - Unpack phase outcomes in meta-learning pipeline
   - Make available to proposers for pattern analysis

3. **Testing** (Day 3)
   - Verify phase outcomes reach proposers
   - Test with missing phase data

**Validation Criteria:**
- Phase outcomes available to proposers
- Pattern analysis uses phase context
- No impact on existing phase execution

**Files Modified:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (+15 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (+8 lines)

---

### Wave B-6: Repair Route → Optimization Proposals (#4)

**Objective:** Connect static ADG repair routes to dynamic optimization

**Tasks:**
1. **Repair Route Serialization** (Day 1)
   - In `_ssot_meta_learning.py`, serialize `repair_routing_summary()` output
   - Add to `PipelineDependencies` as `repair_routes_bytes`

2. **Optimization Engine Enhancement** (Day 2)
   - Add `RepairRouteCluster` handling to `optimization_proposal_engine.py`
   - Map repair routes to optimization proposals
   - Generate proposals for violation remediation

3. **Testing** (Day 2-3)
   - Verify repair routes generate proposals
   - Test proposal quality and relevance

**Validation Criteria:**
- Repair routes converted to proposals
- Proposals target correct agents and CI lanes
- No impact on existing proposal generation

**Files Modified:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (+8 lines)
- `system_learning/engines/optimization_proposal_engine.py` (+30 lines)

---

### Wave B-7: Cache Coherence → Drift Detection (#20)

**Objective:** Detect infrastructure drift through cache consistency monitoring

**Tasks:**
1. **Coherence Event Emission** (Day 1)
   - In `cross_layer_coherence.py`, emit `ConsistencyViolationEvent` on detection
   - Include: layer_type, key, inconsistency_type, resolution
   - Send to `SystemLearningMemoryBridge`

2. **Drift Analyzer Enhancement** (Day 2)
   - Add infrastructure drift dimension to `ShadowDriftAnalyzer`
   - Process coherence events as drift signals
   - Set `drift_source="infrastructure_coherence"`

3. **Validation** (Day 2)
   - Verify coherence violations trigger drift
   - Test drift summary includes infrastructure source

**Validation Criteria:**
- Cache inconsistencies detected as drift
- Infrastructure drift dimension reported
- No impact on cache performance

**Files Modified:**
- `infrastructure/hardening/cross_layer_coherence.py` (+15 lines)
- `system_learning/engines/shadow_drift_analyzer.py` (+15 lines)

---

## Phase 5: Advanced Cross-Domain (Week 5-6)

### Wave C-1: Cross-Domain Pattern Sharing (#7)

**Objective:** Share healing patterns across app domains for collective learning

**Tasks:**
1. **Cross-Domain Event Bus** (Week 5, Days 1-3)
   - Design cross-domain healing event format
   - Implement event bus in `apps_shared/reasoning/BaseHealingOrchestrator.py`
   - Add domain namespace to healing cycle events

2. **Pipeline Integration** (Week 5, Days 3-4)
   - Wire cross-domain events into `PipelineDependencies.cross_repo_learning_context`
   - Update `PatternAnalysisEngine` to process cross-domain patterns

3. **Domain Adapter** (Week 5, Day 5)
   - Create adapter to normalize healing events across domains
   - Handle domain-specific event formats

4. **Testing** (Week 6, Days 1-2)
   - Verify patterns shared between LIC and RG
   - Test cross-domain pattern detection

**Validation Criteria:**
- Healing patterns shared across domains
- Cross-domain patterns detected and analyzed
- No impact on domain-specific healing

**Files Modified:**
- `apps_shared/reasoning/BaseHealingOrchestrator.py` (+30 lines)
- `system_learning/pipelines/pipeline_factory.py` (+10 lines)
- `system_learning/engines/pattern_analysis_engine.py` (+20 lines)

---

### Wave C-2: OTel Spans → Telemetry Store (#9)

**Objective:** Bridge OpenTelemetry spans to system learning telemetry

**Tasks:**
1. **OTel Adapter Design** (Week 5, Days 1-2)
   - Create `OTelTelemetryStoreAdapter` implementing `TelemetryStore` protocol
   - Design span-to-telemetry conversion logic
   - Handle span batching and filtering

2. **Adapter Implementation** (Week 5, Days 3-4)
   - Implement span reading from OTel exporter
   - Convert to `(timestamp, event_type, payload_bytes)` tuples
   - Add error handling and retry logic

3. **Pipeline Integration** (Week 5, Day 5)
   - Register OTel adapter in `pipeline_factory.py`
   - Configure span filtering for relevant events

4. **Testing** (Week 6, Days 1-2)
   - Verify spans converted to telemetry
   - Test telemetry pipeline with OTel data

**Validation Criteria:**
- OTel spans successfully converted to telemetry
- Telemetry pipeline processes span data
- No impact on OTel performance

**Files Modified:**
- `system_learning/adapters/otel_telemetry_store_adapter.py` (new, +120 lines)
- `system_learning/pipelines/pipeline_factory.py` (+8 lines)
- `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (+10 lines)

---

## Implementation Guidelines

### Development Standards
1. **Backward Compatibility:** All new parameters optional with sensible defaults
2. **Graceful Degradation:** Upstream unavailability = skip, never crash
3. **Deterministic Outputs:** Same inputs → same outputs
4. **Lifecycle Trace Compliance:** All new paths emit appropriate `_emit_*` calls
5. **Layer Boundary Safety:** No new gravity violations
6. **Unit Test Coverage:** Minimum 80% for new code
7. **Integration Tests:** End-to-end validation for each wave

### Risk Mitigation
1. **Feature Flags:** Use flags for potentially disruptive changes
2. **Rollback Plan:** Each wave includes rollback procedures
3. **Monitoring:** Add observability for new signal paths
4. **Performance:** Profile impact on critical paths
5. **Data Validation:** Validate all new data formats

### Success Metrics
1. **Signal Coverage:** Increase from 11 to 31 signal types
2. **Domain Coverage:** All 9 domains contributing signals
3. **Pattern Detection:** 50% increase in pattern recognition
4. **Drift Detection:** 40% improvement in drift detection accuracy
5. **Healing Effectiveness:** 15% improvement in healing success rates

---

## Timeline Summary

| Week | Waves | Focus Areas |
|------|-------|-------------|
| 1 | A-1 to A-5 | ADG foundation, routing confidence |
| 2 | A-6 to A-8, B-1 to B-2 | Safety, governance, RCA enrichment |
| 3 | A-9 to A-11, B-3 to B-4 | Execution feedback, orchestration |
| 4 | B-5 to B-7 | Cross-cutting integration |
| 5-6 | C-1 to C-2 | Advanced cross-domain patterns |

**Total Duration:** 
**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
**Parallel Opportunities:** Some waves can be overlapped within phases

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

