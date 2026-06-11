---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\HITL_Confidence_Recalibration_Design_Options.md'
original_relative_path: 'HITL_Confidence_Recalibration_Design_Options.md'
source_sha256: 84d9f2631cca50d506ed50a4c8a0556aa1c16a644dfb45078ca485819f12e13c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# HITL Confidence Recalibration Design Options

**Analysis Date**: 2026-03-14
**ADG Evidence**: `tools/evidence/_adg_hitl_redis_analysis.py`
**Methodology**: ADG-first dependency graph analysis per §0 DEFAULT ANALYSIS MODE

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


## **ADG Analysis Summary**

### **Key Findings from ADG Redis Cache**

**HITL Infrastructure** (Layer: L_SHARED)
- `agentic_core.mixins.hitl_mixin.HITLMixin` - Core mixin
- `agentic_core.mixins.hitl_mixin.RiskLevel` - Risk enum (LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4)
- `agentic_core.mixins.hitl_mixin.ApprovalStatus` - Status enum
- `agentic_core.mixins.hitl_mixin.ApprovalRequest` - Request dataclass
- `agentic_core.mixins.hitl_mixin.ApprovalRequiredError` - Exception
- `agentic_core.mixins.hitl_mixin.ApprovalRejectedError` - Exception
- `agentic_core.mixins.hitl_mixin.ApprovalTimeoutError` - Exception

**System Learning Confidence Infrastructure** (Layer: L_SL)
- `system_learning.confidence.engine.HealingConfidenceScorer` - Confidence scoring engine
- `system_learning.engines.l0_routing_confidence_monitor.L0RoutingConfidenceProposerAdapter` - Routing confidence adapter
- `system_learning.engines.l0_routing_confidence_monitor.RoutingConfidenceChangePackage` - Change proposal type

**System Learning Adapter Patterns** (Layer: L_SL)
- `system_learning.adapters.l1_meta_adapter.L1MetaAdapter` - Meta-learning adapter
- `system_learning.adapters.l4_meta_prior_provider.L4MetaPriorProvider` - Prior provider
- `system_learning.adapters.live_run_pipeline_adapter.LiveRunPipelineAdapter` - Pipeline adapter
- `system_learning.engines.healing_outcome_intake_adapter.HealingOutcomeIntakeAdapter` - Outcome intake
- `system_learning.engines.prompt_outcome_bus_adapter.PromptOutcomeBusAdapter` - Outcome bus

**System Learning Proposer Patterns** (Layer: L_SL)
- `system_learning.engines.l1_model_proposer.L1ModelProposer` - Model calibration proposer
- `system_learning.engines.l5_policy_proposer.L5PolicyProposer` - Policy proposer
- `system_learning.engines.rag_proposer.RAGProposer` - RAG proposer

**Existing Approval Infrastructure** (Layer: L_SL)
- `system_learning.pipelines.approval_gates.ApprovalGate` - Approval gate protocol
- `system_learning.pipelines.approval_gates.ApprovalDecision` - Decision type
- `system_learning.pipelines.approval_gate_impl.AutoApprovalGate` - Auto-approval implementation
- `system_learning.types.meta_learning_types.MetaLearningApprovalArtifact` - Approval artifact

**Related Risk Types**
- `apps_shared.types.risk_level_types.RiskLevel` (L_APP)
- `agentic_core.L5_safety.enforcement.conf_calib_gate.RiskLevel` (L5)
- `agentic_core.L5_safety.gates.tool_safety_gate.ToolRiskLevel` (L5)

---

## **Design Option 1: Feedback-Driven Risk Recalibration (RECOMMENDED)**

### **Architecture**
Mirrors the **L0RoutingConfidenceProposerAdapter** pattern to create a HITL-specific confidence recalibration system.

### **New Components**

#### **1. HITLOutcomeAdapter** (`system_learning/adapters/hitl_outcome_adapter.py`)
```python
@dataclass(frozen=True, slots=True)
class HITLOutcome:
    """Immutable HITL approval outcome for confidence analysis."""
    operation_name: str
    initial_risk_level: RiskLevel  # from agentic_core.mixins.hitl_mixin
    approval_status: ApprovalStatus  # APPROVED, REJECTED, TIMEOUT
    response_time_seconds: float
    rejection_reason: str | None
    context_fingerprint: str  # SHA256 of ApprovalRequest.context
    resolved_by: str
    created_at: float
    resolved_at: float

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization for fingerprinting."""
        data = {
            "operation_name": self.operation_name,
            "initial_risk_level": self.initial_risk_level.value,
            "approval_status": self.approval_status.value,
            "response_time_seconds": round(self.response_time_seconds, 2),
            "context_fingerprint": self.context_fingerprint,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
```

#### **2. HITLConfidenceScorer** (`system_learning/confidence/hitl_confidence_scorer.py`)
```python
class HITLConfidenceScorer:
    """Scores HITL operations to detect risk level miscalibration."""

    def __init__(self):
        # guardian: allow-magic-config
        self._approval_rate_threshold = 0.95  # Downgrade if > 95% approved
        # guardian: allow-magic-config
        self._rejection_rate_threshold = 0.40  # Upgrade if > 40% rejected
        # guardian: allow-magic-config
        self._timeout_rate_threshold = 0.20   # Escalate if > 20% timeout
        # guardian: allow-magic-config
        self._min_observations = 10  # Minimum samples before recalibration

    def score(self, outcomes: Sequence[HITLOutcome]) -> HITLConfidenceReport:
        """
        Analyze HITL outcomes and generate recalibration recommendations.

        Returns:
            HITLConfidenceReport with per-operation confidence scores
            and risk level adjustment proposals.
        """
        # Group by operation_name
        # Calculate approval_rate, rejection_rate, timeout_rate, avg_response_time
        # Detect miscalibration patterns
        # Generate RiskLevelChangePackage proposals
```

#### **3. HITLRiskChangePackage** (`system_learning/types/hitl_types.py`)
```python
@dataclass(frozen=True, slots=True)
class HITLRiskChangePackage:
    """Immutable risk level recalibration proposal."""

    operation_name: str
    old_risk_level: RiskLevel
    new_risk_level: RiskLevel
    justification: str

    # Evidence metrics
    approval_rate: float
    rejection_rate: float
    timeout_rate: float
    avg_response_time_seconds: float
    observation_count: int
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        data = {
            "operation_name": self.operation_name,
            "old_risk_level": self.old_risk_level.value,
            "new_risk_level": self.new_risk_level.value,
            "justification": self.justification,
            "approval_rate": round(self.approval_rate, 4),
            "rejection_rate": round(self.rejection_rate, 4),
            "timeout_rate": round(self.timeout_rate, 4),
            "observation_count": self.observation_count,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
```

#### **4. HITLRiskProposerAdapter** (`system_learning/engines/hitl_risk_proposer.py`)
```python
class HITLRiskProposerAdapter:
    """Proposes HITL risk level adjustments based on approval patterns."""

    def propose(
        self,
        snapshot: Any,
        outcomes: list[HITLOutcome],
        config: dict[str, Any],
        now_utc: int,
        history: dict[str, Any],
        cooldown: CooldownPolicy,
        sample: SampleSizePolicy,
    ) -> list[HITLRiskChangePackage]:
        """
        Propose risk level adjustments for operations with miscalibrated risk.

        Recalibration Rules:
        - MEDIUM → LOW: approval_rate > 0.95, avg_response_time < 30s
        - LOW → MEDIUM: rejection_rate > 0.40 or timeout_rate > 0.20
        - MEDIUM → HIGH: rejection_rate > 0.60 or timeout_rate > 0.30
        - HIGH → CRITICAL: timeout_rate > 0.50
        """
```

### **Integration Points**

#### **Hook into HITLMixin.approve()** (`agentic_core/mixins/hitl_mixin.py:281-311`)
```python
def approve(self, request_id: str, approved_by: str, notes: str='') -> ApprovalRequest:
    # ... existing approval logic ...

    # NEW: Emit outcome to system_learning
    outcome = HITLOutcome(
        operation_name=request.operation_name,
        initial_risk_level=request.risk_level,
        approval_status=ApprovalStatus.APPROVED,
        response_time_seconds=clock_provider.time() - request.created_at,
        rejection_reason=None,
        context_fingerprint=self._hash_context(request.context),
        resolved_by=approved_by,
        created_at=request.created_at,
        resolved_at=request.resolved_at,
    )
    self._emit_hitl_outcome(outcome)  # NEW method

    return request
```

#### **Hook into HITLMixin.reject()** (`agentic_core/mixins/hitl_mixin.py:313-344`)
```python
def reject(self, request_id: str, rejected_by: str, notes: str='') -> ApprovalRequest:
    # ... existing rejection logic ...

    # NEW: Emit outcome to system_learning
    outcome = HITLOutcome(
        operation_name=request.operation_name,
        initial_risk_level=request.risk_level,
        approval_status=ApprovalStatus.REJECTED,
        response_time_seconds=clock_provider.time() - request.created_at,
        rejection_reason=notes,
        context_fingerprint=self._hash_context(request.context),
        resolved_by=rejected_by,
        created_at=request.created_at,
        resolved_at=request.resolved_at,
    )
    self._emit_hitl_outcome(outcome)  # NEW method

    return request
```

#### **New HITLMixin Method**
```python
def _emit_hitl_outcome(self, outcome: HITLOutcome) -> None:
    """Emit HITL outcome to system_learning for confidence recalibration."""
    # Store in Redis with TTL (similar to adg:drift:* pattern)
    # Key: hitl:outcome:<operation_name>:<timestamp>
    # TTL:  (604800 seconds)
    # Value: JSON-serialized HITLOutcome
```

### **Redis Storage Schema**

```
# Outcome storage (7-day TTL)
hitl:outcome:<operation_name>:<timestamp> → JSON(HITLOutcome)

# Aggregated metrics (1-hour TTL)
hitl:metrics:<operation_name> → HASH {
    approval_rate: float,
    rejection_rate: float,
    timeout_rate: float,
    avg_response_time: float,
    observation_count: int,
    last_updated: int
}

# Proposed risk changes (24-hour TTL)
hitl:proposal:<operation_name> → JSON(HITLRiskChangePackage)
```

### **Workflow Integration**

Create `/hitl-recalibration` workflow:
```bash
# 1. Collect HITL outcomes from Redis
python tools/system_learning/collect_hitl_outcomes.py

# 2. Score outcomes and generate proposals
python tools/system_learning/score_hitl_confidence.py

# 3. Review proposals (HITL gate)
python tools/system_learning/review_hitl_proposals.py

# 4. Apply approved recalibrations
python tools/system_learning/apply_hitl_recalibrations.py
```

---

## **Design Option 2: Arbitration-Based Multi-Strategy Risk Assessment**

### **Architecture**
Use `system_learning.arbitration.engine.ArbitrationEngine` to select between multiple risk assessment strategies.

### **Risk Assessment Candidates**

```python
# Strategy 1: Rule-based (current HITLMixin behavior)
ArbitrationCandidate(
    id="rule_based_risk",
    kind="rule_based",
    score=0.8,
    cost=0.1,
    payload={"risk_level": RiskLevel.MEDIUM}
)

# Strategy 2: Historical pattern matching
ArbitrationCandidate(
    id="historical_pattern_risk",
    kind="pattern_based",
    score=0.85,
    cost=0.2,
    payload={
        "risk_level": RiskLevel.LOW,
        "similar_operations": 15,
        "avg_approval_rate": 0.97
    }
)

# Strategy 3: Context embedding similarity
ArbitrationCandidate(
    id="embedding_similarity_risk",
    kind="embedding_based",
    score=0.90,
    cost=0.5,
    payload={
        "risk_level": RiskLevel.LOW,
        "nearest_neighbor_count": 5,
        "avg_neighbor_approval_rate": 0.94
    }
)
```

### **Arbitration Policy**
```python
policy = ArbitrationPolicy(
    allowed_kinds={"rule_based", "pattern_based", "embedding_based"},
    weights={
        "rule_based": 1.0,
        "pattern_based": 1.2,
        "embedding_based": 1.5
    },
    thresholds={"min_score": 0.7},
    caps={"max_winners": 1}
)
```

### **Integration**
```python
def require_approval(self, operation_name: str, context: dict) -> ApprovalRequest:
    # Generate risk assessment candidates
    candidates = [
        self._rule_based_risk_assessment(operation_name),
        self._pattern_based_risk_assessment(operation_name, context),
        self._embedding_based_risk_assessment(operation_name, context),
    ]

    # Arbitrate
    decision = ArbitrationEngine().arbitrate(candidates, policy)

    # Use winning risk level
    winning_payload = candidates[decision.winner_ids[0]].payload
    risk_level = winning_payload["risk_level"]

    # Create approval request with arbitrated risk level
    request = self.create_approval_request(operation_name, context)
    request.risk_level = risk_level  # Override with arbitrated value

    if self.check_approval_required(operation_name):
        raise ApprovalRequiredError(request)
    return request
```

---

## **Design Option 3: Lightweight Threshold Auto-Tuning**

### **Architecture**
Minimal extension to `HITLConfig` with auto-tuning based on approval history.

### **New HITLConfig Fields**
```python
@dataclass
class HITLConfig:
    # ... existing fields ...

    # NEW: Auto-tuning configuration
    enable_auto_tuning: bool = False
    auto_tune_window_size: int = 20  # Last N approvals per operation
    auto_downgrade_approval_threshold: float = 0.95
    auto_upgrade_rejection_threshold: float = 0.40
```

### **New HITLMixin Method**
```python
def _auto_tune_risk_level(self, operation_name: str) -> None:
    """Auto-tune risk level based on recent approval history."""
    if not self._hitl_config.enable_auto_tuning:
        return

    # Get last N outcomes for this operation
    recent_outcomes = self._get_recent_outcomes(
        operation_name,
        limit=self._hitl_config.auto_tune_window_size
    )

    if len(recent_outcomes) < self._hitl_config.auto_tune_window_size:
        return  # Not enough data

    approval_rate = sum(1 for o in recent_outcomes if o.status == ApprovalStatus.APPROVED) / len(recent_outcomes)
    rejection_rate = sum(1 for o in recent_outcomes if o.status == ApprovalStatus.REJECTED) / len(recent_outcomes)

    current_risk = self._sensitive_operations[operation_name]["risk_level"]

    # Downgrade if consistently approved
    if approval_rate >= self._hitl_config.auto_downgrade_approval_threshold:
        if current_risk == RiskLevel.MEDIUM:
            self._propose_risk_downgrade(operation_name, RiskLevel.LOW, approval_rate)

    # Upgrade if frequently rejected
    if rejection_rate >= self._hitl_config.auto_upgrade_rejection_threshold:
        if current_risk == RiskLevel.LOW:
            self._propose_risk_upgrade(operation_name, RiskLevel.MEDIUM, rejection_rate)
        elif current_risk == RiskLevel.MEDIUM:
            self._propose_risk_upgrade(operation_name, RiskLevel.HIGH, rejection_rate)
```

---

## **Recommendation**

**Option 1 (Feedback-Driven Risk Recalibration)** is recommended because:

1. **Mirrors existing patterns**: Follows `L0RoutingConfidenceProposerAdapter` architecture
2. **Deterministic**: Pure functions, no side effects, testable
3. **Observable**: Redis-backed metrics with TTL
4. **Gated**: Proposals require human approval (meta-HITL)
5. **Layered correctly**: System learning (L_SL) → HITL mixin (L_SHARED)
6. **ADG-compatible**: Clear dependency graph, no circular imports

### **Implementation Phases**

**Phase 1: Outcome Collection**
- Add `_emit_hitl_outcome()` to HITLMixin
- Store outcomes in Redis with 7-day TTL
- Create `HITLOutcome` dataclass

**Phase 2: Confidence Scoring**
- Implement `HITLConfidenceScorer`
- Create `HITLRiskChangePackage`
- Build aggregation pipeline

**Phase 3: Proposer Integration**
- Implement `HITLRiskProposerAdapter`
- Integrate with meta-learning pipeline
- Add approval gate for proposals

**Phase 4: Auto-Application (Optional)**
- Add auto-apply logic for high-confidence proposals
- Implement rollback mechanism
- Add audit trail

---

## **References**

- **ADG Evidence**: `tools/evidence/_adg_hitl_redis_analysis.py`
- **HITL Mixin**: `agentic_core/mixins/hitl_mixin.py`
- **Confidence Engine**: `system_learning/confidence/engine.py`
- **L0 Confidence Monitor**: `system_learning/engines/l0_routing_confidence_monitor.py`
- **Arbitration Engine**: `system_learning/arbitration/engine.py`
- **Approval Gates**: `system_learning/pipelines/approval_gates.py`

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

