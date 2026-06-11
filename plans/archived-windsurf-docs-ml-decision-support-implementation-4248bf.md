---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ml-decision-support-implementation-4248bf.md'
original_relative_path: 'ml-decision-support-implementation-4248bf.md'
source_sha256: 8142c6c7fa057e0d2d2ac6d196c48d8f93276f5db034d3e3ff18c1132f76fec8
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ML Decision Support Layer Implementation Plan
**Phase Scope Standardized by Token Estimator**

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## HARDENING OBJECTIVE

Implement a deterministic, governed ML decision-support layer across L0-L6 that augments routing, retrieval, orchestration, safety, healing, observability, and meta-learning WITHOUT violating the architecture SSOT.

## TOKEN ESTIMATE & PHASE SCOPING

**Estimated Total Tokens:** 450K tokens across all phases
- Phase 1: 120K tokens (infrastructure + 3 models)
- Phase 2: 100K tokens (4 models + integration)
- Phase 3: 120K tokens (3 models + meta-learning)
- Phase 4: 110K tokens (validation + rollout)

**Phase Scope Rationale:** Each phase limited to ~120K tokens to ensure:
- Complete implementation within single conversation
- Adequate testing and validation
- Proper documentation and evidence capture
- Rollback capability

## NON-NEGOTIABLE ARCHITECTURAL RULES

1. ML models are advisory unless explicitly promoted through existing governance paths
2. L0 remains the only routing authority
3. L5 remains the only policy certification authority
4. L2 remains the only execution authority
5. L4 remains canonical state
6. L6 remains observation-only
7. Meta-learning proposals must never mutate live execution directly
8. All model outputs must be replayable and tied to trace_id, replay_key, policy_hash, model_version, feature_digest, and threshold_version
9. Fail closed on missing features, stale models, schema mismatch, or confidence below threshold
10. No hidden online learning inside live execution

## IMPLEMENTATION SCOPE

Build simple non-LLM ML components for:
- L0 route recommendation
- L0 confidence-gated escalation
- C0 retrieval reranking and completeness scoring
- semantic cache reuse safety
- L3 DAG branch ranking
- L5 risk calibration support
- L2 healer selection
- L6 anomaly detection
- meta-learning proposal ranking

## TARGET FILES TO CREATE OR MODIFY

### New Package Structure
```
agentic_core/
├── L1_cognition/
│   └── ml_decision_support/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── model_registry.py
│       │   ├── feature_schemas.py
│       │   └── threshold_config.py
│       ├── features/
│       │   ├── __init__.py
│       │   ├── base_extractor.py
│       │   ├── l0_features.py
│       │   ├── c0_features.py
│       │   ├── l3_features.py
│       │   ├── l5_features.py
│       │   ├── l6_features.py
│       │   └── meta_features.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base_model.py
│       │   ├── l0_route_recommender.py
│       │   ├── l0_escalation_classifier.py
│       │   ├── c0_reranker.py
│       │   ├── semantic_cache_classifier.py
│       │   ├── l3_branch_ranker.py
│       │   ├── l5_risk_calibrator.py
│       │   ├── l2_healer_selector.py
│       │   ├── l6_anomaly_detector.py
│       │   └── meta_proposal_ranker.py
│       ├── inference/
│       │   ├── __init__.py
│       │   ├── shadow_logger.py
│       │   ├── replay_harness.py
│       │   └── deterministic_engine.py
│       └── evaluation/
│           ├── __init__.py
│           ├── metrics.py
│           ├── replay_validator.py
│           └── drift_detector.py
```

### Modified Files
1. `agentic_core/L0_routing/artifacts/deterministic_routing_gateway.py` - Add ML augmentation
2. `agentic_core/L1_cognition/context/reference_worktable.py` - Add reranking
3. `agentic_core/L3_orchestration/arbitration/floor_supervisor.py` - Add branch ranking
4. `agentic_core/L5_safety/enforcement/policy_certifier.py` - Add risk scoring
5. `agentic_core/L2_execution/adaptation/healing_engine.py` - Add healer selection
6. `agentic_core/L6_sovereignty/observation/compliance_office.py` - Add anomaly detection
7. `agentic_core/L4_canonical/state/snapshot_manager.py` - Add ML state tracking
8. `agentic_core/runtime/lifecycle_trace_contract.py` - Add ML trace events

## MODEL PRIORITY ORDER

### Phase 1: Foundation Models
1. **Logistic Regression** - L0 route recommendation
2. **LightGBM** - C0 retrieval reranking
3. **Isolation Forest** - L6 anomaly detection

### Phase 2: Ranking Models
4. **Learning-to-Rank (LambdaMART)** - L3 DAG branch ranking
5. **XGBoost** - L5 risk calibration
6. **Logistic Regression** - L2 healer selection
7. **EWMA** - Semantic cache safety

### Phase 3: Meta-Learning
8. **Contextual Bandits (Shadow Only)** - Meta proposal ranking
9. **Change-Point Detection** - L6 drift detection
10. **Logistic Regression** - L0 escalation classifier

## FEATURE SCHEMAS PER MODEL

### L0 Route Recommender
```python
features = {
    "token_count": int,
    "tool_complexity_score": float,
    "latency_budget_ms": int,
    "user_confidence_score": float,
    "path_success_history": float,
    "current_load_ratio": float,
    "semantic_similarity_score": float,
    "policy_hash_version": str,
    "trace_id_hash": str
}
```

### C0 Retrieval Reranker
```python
features = {
    "query_doc_similarity": float,
    "doc_authority_score": float,
    "recency_score": float,
    "usage_frequency": float,
    "semantic_density": float,
    "source_reliability": float,
    "completeness_score": float,
    "query_complexity": float,
    "cache_hit_probability": float
}
```

### L6 Anomaly Detector
```python
features = {
    "latency_z_score": float,
    "error_rate_spike": float,
    "token_deviation": float,
    "path_divergence": float,
    "policy_hash_changes": int,
    "replay_mismatch_count": int,
    "escalation_frequency": float,
    "healing_success_rate": float,
    "semantic_drift_score": float
}
```

## TRAINING DATA SOURCES

### Primary Sources
1. **L0 Routing Logs** - `artifacts/routing/history/`
2. **C0 Retrieval Logs** - `artifacts/retrieval/interactions/`
3. **L3 Execution Traces** - `artifacts/orchestration/dag_executions/`
4. **L5 Policy Decisions** - `artifacts/safety/policy_reviews/`
5. **L2 Healing Events** - `artifacts/execution/healing_traces/`
6. **L6 Anomaly Reports** - `artifacts/observability/anomalies/`
7. **Meta-Learning Proposals** - `artifacts/meta_learning/proposals/`

### Data Processing Pipeline
```python
# ops_scripts/ml_pipeline/data_processor.py
- Extract from ADG SQLite
- Validate feature completeness
- Compute deterministic hashes
- Version datasets with content digests
- Store in artifacts/ml/training_data/
```

## ROLLOUT PLAN BY PHASE

### Phase 1: Infrastructure + First Models (Week 1-2)
1. **Week 1**: Setup infrastructure
   - Model registry implementation
   - Feature pipeline framework
   - Shadow logging system
   - Replay harness

2. **Week 2**: Deploy first 3 models
   - L0 route recommender (logistic regression)
   - C0 reranker (LightGBM)
   - L6 anomaly detector (Isolation Forest)
   - All in shadow mode only

### Phase 2: Ranking Integration (Week 3-4)
1. **Week 3**: Ranking models
   - L3 branch ranker (LambdaMART)
   - L5 risk calibrator (XGBoost)
   - L2 healer selector (logistic regression)

2. **Week 4**: Cache and monitoring
   - Semantic cache classifier (EWMA)
   - Enhanced monitoring dashboards
   - Threshold tuning framework

### Phase 3: Meta-Learning (Week 5-6)
1. **Week 5**: Meta-learning infrastructure
   - Proposal ranking model
   - Counterfactual estimation
   - Shadow contextual bandits

2. **Week 6**: Advanced detection
   - Drift detection (change-point)
   - L0 escalation classifier
   - Full integration testing

### Phase 4: Validation & Production (Week 7-8)
1. **Week 7**: Comprehensive validation
   - Replay parity checks
   - Determinism verification
   - Performance benchmarking

2. **Week 8**: Production rollout
   - Gradual promotion from shadow
   - A/B testing against baselines
   - Monitoring and rollback procedures

## FAILURE MODES

### Model Failures
1. **Missing Features** → Fail closed to heuristic
2. **Stale Model** → Automatic fallback
3. **Low Confidence** → Escalate to human
4. **Schema Mismatch** → Reject and log
5. **Timeout** → Use cached decision

### System Failures
1. **Feature Pipeline Down** → Use last known features
2. **Model Store Unavailable** → Local cache fallback
3. **High Latency** → Skip ML for that request
4. **Memory Pressure** → Disable non-critical models

### Data Failures
1. **Training Data Corruption** → Use previous version
2. **Feature Drift** → Trigger retraining
3. **Label Noise** → Flag for review
4. **Concept Drift** → Model retraining

## TEST PLAN

### Unit Tests
```python
tests/unit/ml_decision_support/
├── test_feature_extractors.py
├── test_model_inference.py
├── test_shadow_logging.py
├── test_replay_harness.py
└── test_determinism.py
```

### Integration Tests
```python
tests/integration/ml_decision_support/
├── test_l0_ml_augmentation.py
├── test_c0_reranking_pipeline.py
├── test_l3_ranking_integration.py
├── test_l5_risk_scoring.py
├── test_end_to_end_replay.py
└── test_fail_closed_behavior.py
```

### Performance Tests
```python
tests/performance/ml_decision_support/
├── test_inference_latency.py
├── test_batch_throughput.py
├── test_memory_usage.py
└── test_cache_efficiency.py
```

### Determinism Tests
```python
tests/determinism/ml_decision_support/
├── test_replay_parity.py
├── test_feature_determinism.py
├── test_model_output_stability.py
└── test_hash_consistency.py
```

## MIGRATION PLAN FROM HEURISTICS TO ML

### Step 1: Parallel Shadow Mode
- Run heuristics as primary
- Run ML in shadow
- Log differences
- Build confidence

### Step 2: Gradual Promotion
- Start with low-risk decisions
- 10% ML, 90% heuristic
- Monitor metrics
- Adjust thresholds

### Step 3: Controlled Rollout
- 50% ML, 50% heuristic
- Automatic rollback triggers
- Human oversight required

### Step 4: ML-First with Fallback
- ML as primary
- Heuristics as fallback
- Continuous monitoring
- Periodic validation

## EXPLICIT NON-ML HARD RULES

The following decisions MUST remain non-ML hard rules:

1. **L0 Path Assignment** - Final path decision remains with L0
2. **L5 Policy Certification** - Policy approval cannot be overridden
3. **L2 Execution Authority** - Execution permission cannot be granted by ML
4. **Security Boundaries** - Access control decisions remain hard rules
5. **UWG Bypass** - Universal Write Guard cannot be bypassed by ML
6. **Policy Hash Mutation** - Only L5 can modify policy hashes
7. **Trace ID Generation** - Must remain deterministic and non-ML
8. **Replay Key Creation** - Cryptographic keys cannot be ML-generated
9. **Emergency Stops** - System halt triggers remain manual
10. **Audit Requirements** - Compliance rules cannot be ML-modified

## REQUIRED EVALUATION METRICS

### Per-Model Metrics
- **Precision/Recall**: Classification models
- **Calibration**: Probability reliability
- **False Positive/Negative Cost**: Business impact
- **Business Utility**: Overall value
- **Determinism Check**: Same input → same output
- **Replay Parity**: Historical consistency
- **Drift Sensitivity**: Performance over time
- **Feature Availability**: % requests with all features

### Ranking Model Metrics
- **NDCG@10**: Normalized discounted cumulative gain
- **MRR**: Mean reciprocal rank
- **Hit@3/5/10**: Success at various positions

### Anomaly Detection Metrics
- **Alert Precision**: % alerts that are real
- **Mean Time to Detection**: Speed of detection
- **Operator Usefulness**: Human validation rate

## ENGINEERING TASKS DETAIL

### 1. Model Registry Implementation
```python
# agentic_core/L1_cognition/ml_decision_support/config/model_registry.py
class ModelRegistry:
    - Version tracking with content digests
    - Metadata storage (training date, metrics, thresholds)
    - Promotion workflow (shadow → candidate → production)
    - Rollback capability
    - Access control and audit logging
```

### 2. Deterministic Feature Pipeline
```python
# agentic_core/L1_cognition/ml_decision_support/features/base_extractor.py
class DeterministicFeatureExtractor:
    - Fixed random seeds
    - Reproducible preprocessing
    - Versioned feature schemas
    - Null handling policies
    - Feature provenance tracking
```

### 3. Shadow Inference Logging
```python
# agentic_core/L1_cognition/ml_decision_support/inference/shadow_logger.py
class ShadowLogger:
    - Log all ML decisions in shadow mode
    - Compare with actual decisions
    - Track improvement opportunities
    - Store for training data
```

### 4. Replay Harness
```python
# agentic_core/L1_cognition/ml_decision_support/inference/replay_harness.py
class ReplayHarness:
    - Replay historical requests
    - Verify deterministic outputs
    - Detect model drift
    - Validate feature consistency
```

### 5. Threshold Configuration
```python
# agentic_core/L4_canonical/state/threshold_store.py
class ThresholdStore:
    - Versioned threshold configs
    - A/B testing support
    - Gradual rollout control
    - Automated rollback triggers
```

## DASHBOARD REQUIREMENTS

### Monitoring Dashboards
1. **Model Performance**: Real-time metrics
2. **Decision Disagreement**: ML vs heuristic
3. **Feature Drift**: Distribution changes
4. **Score Calibration**: Confidence accuracy
5. **System Health**: Latency, errors, availability

### Alerting Rules
- Model performance degradation >10%
- Feature availability <95%
- High disagreement rate >20%
- Replay parity failures
- Threshold breach alerts

## SECURITY & COMPLIANCE

### Data Privacy
- No PII in features
- GDPR compliance for training data
- Right to explanation for ML decisions
- Data retention policies

### Model Security
- Model signature verification
- Tamper detection
- Secure model storage
- Access control

### Audit Requirements
- Complete decision logging
- Model version tracking
- Feature provenance
- Regulatory compliance

## INFRASTRUCTURE NEEDS

### Compute Requirements
- CPU: 16 cores for feature extraction
- Memory: 64GB for model loading
- Storage: 500GB for models + data
- Network: Low latency for real-time inference

### Storage Architecture
- Models: `artifacts/ml/models/`
- Features: `artifacts/ml/features/`
- Logs: `artifacts/ml/logs/`
- Metrics: `artifacts/ml/metrics/`

### Deployment Strategy
- Blue-green deployment
- Canary releases
- Feature flags
- Circuit breakers

## RISK MITIGATION

### Technical Risks
1. **Model Degradation**: Continuous monitoring
2. **Feature Drift**: Automated retraining
3. **System Complexity**: Modular design
4. **Performance Impact**: Lazy loading, caching

### Business Risks
1. **Wrong Decisions**: Human oversight
2. **Regulatory Issues**: Compliance review
3. **User Trust**: Transparency, explainability
4. **Vendor Lock**: Open source models

## SUCCESS CRITERIA

### Phase 1 Success
- Infrastructure deployed
- 3 models in shadow mode
- 99.9% system uptime
- <5ms inference latency

### Phase 2 Success
- All ranking models deployed
- 10% improvement in relevance
- Determinism verified
- No regression in core metrics

### Phase 3 Success
- Meta-learning operational
- Drift detection working
- 20% reduction in anomalies
- Positive user feedback

### Phase 4 Success
- Full production deployment
- 95% automation rate
- Measurable ROI
- Compliance satisfied

## CONCLUSION

This plan implements a conservative, governed approach to ML integration that:
- Respects all architectural boundaries
- Maintains system determinism
- Provides clear rollback paths
- Ensures regulatory compliance
- Delivers measurable business value

The phased approach allows for gradual learning and adjustment while maintaining system stability and reliability.

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

