# ML Models for L0 Routing Confidence Calibration - Implementation Plan-2e2596

This plan analyzes the most common Machine Learning models used in routing agentic architectures and provides implementation recommendations for confidence calibration in L0 routing, following OpenAI agentic best practices.

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

Modern agentic architectures require sophisticated routing mechanisms that can reliably classify user intents and select appropriate agents while maintaining calibrated confidence scores for HITL (Human-in-the-Loop) integration. This document analyzes industry-standard ML approaches and provides concrete implementation recommendations for L0 routing.

## Core ML Models for Agentic Routing

### 1. **Intent Classification Models**

#### 1.1 Embedding-Based Semantic Classifiers
- **Model Type**: Transformer-based embeddings (e.g., text-embedding-3-small/large)
- **Architecture**: Cosine similarity matching against prototype vectors
- **Use Case**: Primary intent classification when clear semantic patterns exist
- **Confidence Calibration**: Raw cosine scores → temperature scaling

```python
# Current implementation uses this approach
class IntentEmbeddingClassifier:
    - Uses FAISS for efficient similarity search
    - Implements cosine similarity scoring
    - Needs calibration layer for reliable confidence
```

#### 1.2 Fine-Tuned Classification Models
- **Model Type**: BERT/RoBERTa fine-tuned on intent datasets
- **Architecture**: Multi-class classification with softmax output
- **Use Case**: Complex intent patterns requiring contextual understanding
- **Confidence Calibration**: Temperature scaling + label smoothing

#### 1.3 Zero-Shot/Few-Shot Classifiers
- **Model Type**: GPT-3.5/4 with prompt engineering
- **Architecture**: LLM-based classification with structured prompts
- **Use Case**: New intents without training data
- **Confidence Calibration**: Token probability aggregation + ensemble methods

### 2. **Multi-Armed Bandits for Routing Optimization**

#### 2.1 Contextual Bandits (LinUCB)
- **Purpose**: Balance exploration vs exploitation in routing decisions
- **Features**: User context, intent embedding, historical performance
- **Update Rule**: Online learning from routing outcomes
- **Confidence**: Upper confidence bounds for decision safety

#### 2.2 Thompson Sampling
- **Purpose**: Probabilistic routing with uncertainty quantification
- **Advantages**: Natural uncertainty estimates for HITL triggers
- **Implementation**: Bayesian posterior updates from feedback

### 3. **Ensemble Methods for Robust Routing**

#### 3.1 Stacked Ensemble
- **Base Models**: Embedding classifier, fine-tuned model, rule-based system
- **Meta-Learner**: Gradient boosting on base model predictions
- **Benefit**: Combines strengths of multiple approaches

#### 3.2 Mixture of Experts (MoE)
- **Architecture**: Gating network + specialized expert models
- **Routing**: Soft routing based on input characteristics
- **Confidence**: Gating probabilities provide natural uncertainty

## Confidence Calibration Methods

### 1. **Temperature Scaling**
```python
# Apply temperature to logits before softmax
calibrated_confidence = softmax(logits / temperature)
# Temperature learned on validation set to minimize NLL
```

### 2. **Platt Scaling**
- Logistic regression on model scores
- Effective for binary/multi-class problems
- Requires calibration dataset

### 3. **Isotonic Regression**
- Non-parametric calibration
- More flexible but requires more data
- Risk of overfitting on small datasets

### 4. **Dirichlet Calibration**
- Calibrates full probability distribution
- Better for uncertainty quantification
- Suitable for HITL scenarios

### 5. **Ensemble-Based Calibration**
- Deep Ensembles: Multiple models with different seeds
- MC Dropout: Bayesian approximation via dropout
- Provides uncertainty estimates alongside calibration

## Implementation Recommendations

### Phase 1: Enhance Current System
1. **Add Calibration Layer to IntentEmbeddingClassifier**
   - Implement temperature scaling
   - Create calibration dataset from routing logs
   - Monitor Expected Calibration Error (ECE)

2. **Implement Confidence Thresholds**
   ```python
   # Dynamic threshold based on ADG territory score
   adjusted_threshold = base_threshold - (adg_risk_score * 0.1)
   ```

3. **Add Uncertainty Quantification**
   - Monte Carlo dropout for embedding classifier
   - Confidence intervals for routing decisions

### Phase 2: Multi-Model Approach
1. **Implement Contextual Bandit**
   - LinUCB for online learning
   - Context features: intent embedding, user history, time
   - Exploration parameter tied to confidence

2. **Add Ensemble Router**
   - Combine embedding classifier with rule-based system
   - Meta-learner for final routing decision
   - Confidence from ensemble variance

### Phase 3: Advanced Features
1. **Implement Mixture of Experts**
   - Specialized experts for different domains
   - Gating network for expert selection
   - Load balancing considerations

2. **Add Meta-Learning**
   - Fast adaptation to new intents
   - Learning to learn from few examples
   - Continual learning capabilities

## HITL Integration Points

### 1. **Confidence-Based Escalation**
```python
if routing_confidence < threshold:
    escalate_to_human(
        reason="Low routing confidence",
        confidence=routing_confidence,
        top_k_alternatives=alternative_routes
    )
```

### 2. **Active Learning Loop**
- Collect human feedback on uncertain routings
- Use feedback for model improvement
- Prioritize high-impact corrections

### 3. **Explainable Routing**
- Provide routing rationale to humans
- Show confidence breakdown by factor
- Enable human override with learning

## Monitoring and Evaluation

### 1. **Calibration Metrics**
- Expected Calibration Error (ECE)
- Reliability diagrams
- Brier score
- Sharpness vs calibration trade-off

### 2. **Routing Performance**
- Accuracy@k
- Routing latency
- Success rate by confidence bucket
- Human intervention rate

### 3. **Business Metrics**
- Task completion rate
- User satisfaction
- Cost per successful routing
- Human reviewer efficiency

## Technical Architecture

### 1. **Model Serving**
```python
class CalibratedRouter:
    def __init__(self):
        self.embedding_classifier = IntentEmbeddingClassifier()
        self.calibrator = TemperatureCalibrator()
        self.bandit = LinUCB()
        self.ensemble = EnsembleRouter()
    
    def route(self, query: str) -> RoutingDecision:
        # Get predictions from multiple models
        embedding_score = self.embedding_classifier.classify(query)
        bandit_score = self.bandit.predict(query)
        ensemble_score = self.ensemble.predict(query)
        
        # Calibrate and combine
        calibrated_confidence = self.calibrator(embedding_score)
        final_confidence = self.combine_scores([
            calibrated_confidence,
            bandit_score,
            ensemble_score
        ])
        
        return RoutingDecision(
            agent=self.select_agent(final_confidence),
            confidence=final_confidence,
            uncertainty=self.calculate_uncertainty(),
            explanation=self.generate_explanation()
        )
```

### 2. **Feedback Pipeline**
```python
class RoutingFeedback:
    def collect_feedback(self, routing_id: str, outcome: RoutingOutcome):
        # Update bandit
        self.bandit.update(routing_id, outcome.reward)
        
        # Store for calibration updates
        self.calibration_buffer.add(routing_id, outcome)
        
        # Trigger active learning if uncertain
        if outcome.routing_uncertainty > threshold:
            self.request_human_review(routing_id)
```

### 3. **Continuous Learning**
- Daily calibration updates
- Weekly model retraining
- Monthly architecture evaluation
- Quarterly model refresh

## Risk Mitigation

### 1. **Confidence Drift**
- Monitor calibration metrics continuously
- Automatic recalibration triggers
- Fallback to simpler models if needed

### 2. **Catastrophic Forgetting**
- Maintain rehearsal buffer
- Elastic weight consolidation
- Regular performance validation

### 3. **Adversarial Robustness**
- Input validation and sanitization
- Adversarial training for classifiers
- Anomaly detection for out-of-distribution inputs

## Success Criteria

1. **Calibration**: ECE < 0.05 on held-out test set
2. **Accuracy**: >95% routing accuracy with confidence >0.8
3. **Latency**: <100ms routing decision time
4. **HITL Efficiency**: <5% human intervention rate
5. **Adaptability**: < to onboard new agent types

## Next Steps

1. Implement temperature scaling for existing classifier
2. Create calibration dataset from routing logs
3. Develop monitoring dashboard for calibration metrics
4. Prototype contextual bandit for online learning
5. Design feedback collection system for HITL
6. Plan phased rollout with A/B testing

## Conclusion

A multi-model approach with proper confidence calibration is essential for reliable L0 routing in agentic architectures. By combining embedding-based classification, contextual bandits, and ensemble methods with robust calibration techniques, we can achieve both high accuracy and reliable confidence estimates for effective HITL integration.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

