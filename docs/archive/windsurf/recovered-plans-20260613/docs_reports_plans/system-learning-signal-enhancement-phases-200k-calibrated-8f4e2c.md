# System Learning Signal Enhancement — 200K Context-Calibrated Phases

**Date:** 2026-03-26  
**Based on:** `system-learning-signal-enhancement-top20-b7e2d4.md`  
**Calibration:** Each phase designed for 200K SWE 1.5 context window  
**Assumptions:** 80 chars/line avg, 30K base context, 170K available for code

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


## Context Budget Analysis

| Phase | Files | Total Lines | Est. Chars | Fits in 200K? |
|-------|-------|-------------|------------|----------------|
| **Phase 1** | 8 files | 3,083 | 246K | ❌ NO |
| **Phase 2** | 4 files | 2,003 | 160K | ✅ YES |
| **Phase 3** | 6 files | 2,487 | 199K | ✅ YES |
| **Phase 4** | 5 files | 1,892 | 151K | ✅ YES |
| **Phase 5** | 3 files | 1,677 | 134K | ✅ YES |

**Solution:** Split Phase 1 into two sub-phases (1A and 1B)

---

## Phase 1A: ADG Foundation (Days 1-2)

**Context:** 1,541 lines (~123K) - ✅ Fits

**Files:**
- `system_learning/engines/rca_engine.py` (319 lines)
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` (428 lines)
- `system_learning/engines/default_healing_pattern_advisor.py` (269 lines)
- `system_learning/engines/shadow_drift_analyzer.py` (375 lines)
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (~150 lines relevant)

### Waves in Phase 1A

#### Wave A-1: RCA Engine ↔ ADG Violation Correlation (#1)
**Changes:** ~25 lines total
- `ADGMemoryAdapter.py`: +15 lines (get_violation_file_set method)
- `rca_engine.py`: +10 lines (violation correlation logic)

#### Wave A-3: Hotspot-Aware Healing Priority (#3)
**Changes:** ~30 lines total
- `ADGMemoryAdapter.py`: +12 lines (get_hotspot_modules method)
- `default_healing_pattern_advisor.py`: +18 lines (hotspot query + boost)

#### Wave A-5: Violation Trend as Drift Dimension (#5)
**Changes:** ~35 lines total
- `system_learning_memory_bridge.py`: +20 lines (get_latest_violation_counts)
- `shadow_drift_analyzer.py`: +15 lines (violation trend analysis)

---

## Phase 1B: Safety & Governance Foundation (Days 3-4)

**Context:** 1,542 lines (~123K) - ✅ Fits

**Files:**
- `system_learning/engines/l0_routing_confidence_monitor.py` (418 lines)
- `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` (463 lines)
- `agentic_core/prompt_governance/scripts/detect_template_drift.py` (301 lines)
- `system_learning/engines/prompt_drift_detector.py` (510 lines)
- `tools/generate_full_adg.py` (~50 lines relevant)
- `system_learning/adapters/system_learning_memory_bridge.py` (~100 lines relevant)

### Waves in Phase 1B

#### Wave A-4: ADG Behavioral Score → Routing Confidence (#6)
**Changes:** ~25 lines total
- `_ssot_meta_learning.py`: +10 lines (emit behavioral score)
- `l0_routing_confidence_monitor.py`: +15 lines (factor ADG score)

#### Wave A-6: Circuit Breaker State → SL Signal (#11)
**Changes:** ~40 lines total
- `circuit_breaker_gate.py`: +15 lines (emit state transitions)
- `system_learning_memory_bridge.py`: +25 lines (persist_circuit_breaker_event)

#### Wave A-7: Template Drift → Prompt Drift Detector (#12)
**Changes:** ~45 lines total
- `detect_template_drift.py`: +20 lines (detect_and_return_drift)
- `prompt_drift_detector.py`: +25 lines (structural drift dimension)

#### Wave A-10: ADG Confidence Tiers → L0 Monitor (#10)
**Changes:** ~28 lines total
- `generate_full_adg.py`: +8 lines (persist conf_summary)
- `l0_routing_confidence_monitor.py`: +20 lines (read tier distribution)

---

## Phase 2: Execution & Orchestration (Week 2)

**Context:** 2,003 lines (~160K) - ✅ Fits

**Files:**
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (711 lines)
- `agentic_core/L3_orchestration/learning/workflow_learning_bridge.py` (306 lines)
- `apps_eval/engines/regression_detector.py` (296 lines)
- `system_learning/engines/pattern_analysis_engine.py` (~200 lines relevant)
- `system_learning/engines/signal_grouping_engine.py` (~150 lines relevant)
- `system_learning/engines/rca_cluster_engine.py` (~240 lines relevant)

### Waves in Phase 2

#### Wave A-8: Injection Detection Counts → Pattern Analysis (#18)
**Changes:** ~35 lines total
- `injection_detector.py`: +20 lines (track detection events)
- `signal_grouping_engine.py`: +15 lines (SecuritySignalGroup)

#### Wave A-9: Healing Tier Dispatch → Meta-Learning (#14)
**Changes:** ~30 lines total
- `healing_tier_dispatcher.py`: +15 lines (emit tier outcomes)
- `pattern_analysis_engine.py`: +15 lines (tier effectiveness)

#### Wave A-10: WorkflowLearningBridge → Pipeline (#16)
**Changes:** ~90 lines total
- `workflow_learning_bridge.py`: +10 lines (registration point)
- `workflow_outcome_sl_adapter.py` (new file, +80 lines)

#### Wave A-11: Eval Regression → Drift Detection (#17)
**Changes:** ~25 lines total
- `regression_detector.py`: +10 lines (emit results)
- `shadow_drift_analyzer.py`: +15 lines (eval regression dimension)

#### Wave B-1: Cognitive Disposition → RCA Enrichment (#8)
**Changes:** ~28 lines total
- `_ssot_meta_learning.py`: +8 lines (serialize cognitive dispositions)
- `rca_engine.py`: +20 lines (parse cognitive context)

#### Wave B-2: Safety Audit Records → RCA Clusters (#13)
**Changes:** ~35 lines total
- `safety_audit_emitter.py`: +10 lines (query API)
- `trace_feature_types.py`: +5 lines (optional field)
- `rca_cluster_engine.py`: +20 lines (factor safety audit)

---

## Phase 3: Resource & Memory Integration (Week 3)

**Context:** 2,487 lines (~199K) - ✅ Fits

**Files:**
- `agentic_core/L2_execution/engines/resource_predictor.py` (~300 lines)
- `agentic_core/L2_execution/engines/rollback_refiner.py` (~200 lines)
- `agentic_core/L1_cognition/memory/healing_memory_retriever.py` (~400 lines)
- `system_learning/engines/policy_recommendation_engine.py` (~250 lines)
- `system_learning/pipelines/meta_learning_pipeline.py` (~600 lines)
- `system_learning/engines/optimization_proposal_engine.py` (~400 lines)
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` (~137 lines remaining)

### Waves in Phase 3

#### Wave B-3: Resource Prediction Feedback (#15)
**Changes:** ~35 lines total
- `resource_predictor.py`: +20 lines (accuracy tracking)
- `rollback_refiner.py`: +15 lines (strategy outcomes)

#### Wave B-4: Healing Memory Retrieval Quality (#19)
**Changes:** ~40 lines total
- `healing_memory_retriever.py`: +25 lines (quality metrics)
- `policy_recommendation_engine.py`: +15 lines (quality input)

#### Wave B-5: Execute_SSOT Phase Outcome Feedback (#2)
**Changes:** ~23 lines total
- `_ssot_meta_learning.py`: +15 lines (collect phase outcomes)
- `meta_learning_pipeline.py`: +8 lines (unpack outcomes)

#### Wave B-6: Repair Route → Optimization Proposals (#4)
**Changes:** ~38 lines total
- `_ssot_meta_learning.py`: +8 lines (serialize repair routes)
- `optimization_proposal_engine.py`: +30 lines (RepairRouteCluster)

---

## Phase 4: Cross-Domain & Infrastructure (Week 4)

**Context:** 1,892 lines (~151K) - ✅ Fits

**Files:**
- `infrastructure/hardening/cross_layer_coherence.py` (690 lines)
- `apps_shared/reasoning/BaseHealingOrchestrator.py` (~400 lines)
- `system_learning/pipelines/pipeline_factory.py` (~200 lines)
- `system_learning/engines/pattern_analysis_engine.py` (~200 lines remaining)
- `system_learning/engines/shadow_drift_analyzer.py` (~100 lines remaining)
- `system_learning/adapters/system_learning_memory_bridge.py` (~100 lines remaining)

### Waves in Phase 4

#### Wave B-7: Cache Coherence → Drift Detection (#20)
**Changes:** ~30 lines total
- `cross_layer_coherence.py`: +15 lines (emit violations)
- `shadow_drift_analyzer.py`: +15 lines (infrastructure drift)

#### Wave C-1: Cross-Domain Pattern Sharing (#7)
**Changes:** ~70 lines total
- `BaseHealingOrchestrator.py`: +30 lines (cross-domain events)
- `pipeline_factory.py`: +10 lines (wire cross_repo context)
- `pattern_analysis_engine.py`: +30 lines (cross-domain patterns)

---

## Phase 5: Advanced Integration (Weeks 5-6)

**Context:** 1,677 lines (~134K) - ✅ Fits

**Files:**
- `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (~300 lines)
- `system_learning/pipelines/pipeline_factory.py` (~100 lines remaining)
- `system_learning/types/telemetry_store_protocol.py` (~200 lines)
- `system_learning/adapters/` (new files)
- `agentic_core/prompt_governance/security/detectors/injection_detector.py` (~400 lines)
- `system_learning/engines/signal_grouping_engine.py` (~100 lines remaining)

### Waves in Phase 5

#### Wave C-2: OTel Spans → Telemetry Store (#9)
**Changes:** ~150 lines total
- `otel_telemetry_store_adapter.py` (new file, +120 lines)
- `pipeline_factory.py`: +8 lines (register adapter)
- `open_telemetry_tracing_adapter_util.py`: +10 lines (expose spans)
- `telemetry_store_protocol.py` (new file, +12 lines)

#### Wave A-8 (Completion): Injection Detection Full Integration
**Changes:** ~50 lines total
- `injection_detector.py`: +30 lines (per-agent/route counting)
- `signal_grouping_engine.py`: +20 lines (spike detection)

---

## Implementation Strategy

### Sharp Assumptions for Context Optimization

1. **Minimal Diffs:** Each wave averages 30-40 lines of changes
2. **Focused Edits:** Only modify relevant functions, not entire files
3. **Reuse Imports:** Leverage existing import statements where possible
4. **Compact Code:** Use concise implementations without verbose comments
5. **Batch Operations:** Combine related changes in single edits

### Context Management Tactics

1. **Phase Isolation:** Each phase loads only its required files
2. **Incremental Loading:** Load files as needed, not all at once
3. **Selective Reading:** Read only relevant sections of large files
4. **Edit Efficiency:** Use multi_edit for multiple small changes
5. **Validation Deferred:** Run tests after phase completion, not during

### Risk Mitigation

1. **Feature Flags:** Add flags for each wave to enable/disable independently
2. **Rollback Points:** Each phase ends with a stable checkpoint
3. **Validation Gates:** Test each phase before proceeding
4. **Documentation:** Update docs after each phase completion
5. **Monitoring:** Add logging for new signal paths

---

## Timeline Summary

| Week | Phase | Context | Waves | Focus |
|------|-------|---------|-------|-------|
| 1 | 1A | 123K | 3 waves | ADG Foundation (RCA, Hotspots, Drift) |
| 1 | 1B | 123K | 4 waves | Safety & Governance (Circuit Breaker, Template Drift) |
| 2 | 2 | 160K | 6 waves | Execution & Orchestration (Tier Dispatch, Workflow) |
| 3 | 3 | 199K | 4 waves | Resource & Memory Integration |
| 4 | 4 | 151K | 2 waves | Cross-Domain & Infrastructure |
| 5-6 | 5 | 134K | 2 waves | Advanced Integration (OTel, Full Injection) |

**Total:** 6 phases, 21 waves, all within 200K context windows

---

## Success Metrics per Phase

### Phase 1A (ADG Foundation)
- RCA findings correlated with violations
- Hotspot modules receive priority boost
- Violation trends detected as drift

### Phase 1B (Safety & Governance)
- Circuit breaker patterns tracked
- Template drift detected structurally
- ADG confidence tiers influence routing

### Phase 2 (Execution & Orchestration)
- Injection attempts monitored
- Healing tier effectiveness tracked
- Workflow outcomes consumed by SL

### Phase 3 (Resource & Memory)
- Resource prediction accuracy tracked
- Healing memory quality monitored
- Phase outcomes inform proposers

### Phase 4 (Cross-Domain)
- Cache coherence issues detected
- Patterns shared across domains

### Phase 5 (Advanced)
- OTel spans converted to telemetry
- Full injection detection integration

Each phase is designed to complete within a single SWE 1.5 turn while maximizing the 200K context window usage.

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

