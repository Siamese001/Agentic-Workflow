# Policy Epoch Specification

## SCOPE
Governs: **Meta-Learning Bus** (Policy Epoch Management, Threshold Configuration, Shadow Evaluation)

Defines meta-learning constraints with staged threshold updates and human approval gates.

---

Meta-learning bus constraints with staged threshold configuration and shadow evaluation.

---

## Policy Epoch Structure

```python
@dataclass
class PolicyEpoch:
    epoch_id: str  # UUID v4
    version: int  # Monotonically increasing
    created_at: str  # ISO 8601 timestamp
    activated_at: Optional[str]  # ISO 8601 timestamp
    deactivated_at: Optional[str]  # ISO 8601 timestamp
    status: str  # "STAGED", "SHADOW", "ACTIVE", "DEPRECATED"

    # Threshold configuration
    threshold_config: ThresholdConfig

    # Approval metadata
    approved_by: Optional[str]  # Human approver ID
    approval_timestamp: Optional[str]

    # Shadow evaluation results
    shadow_evaluation: Optional[ShadowEvaluationResult]

    # Rollback capability
    parent_epoch_id: Optional[str]  # For rollback chain

    # Audit trail
    change_log: List[str]
```

---

## Threshold Configuration

```python
@dataclass
class ThresholdConfig:
    # Confidence thresholds
    high_confidence_threshold: float  # >0.80 default
    medium_confidence_threshold: float  # 0.40 default

    # Safety thresholds
    safety_timeout_ms: int  # 500ms default
    max_healing_operations: int  # 100 default

    # Meta-learning thresholds
    pattern_similarity_threshold: float  # 0.75 default
    min_success_rate: float  # 0.6 default

    # Circuit breaker thresholds
    failure_threshold: int  # 3 default
    timeout_seconds: int  # 60 default

    # Budget thresholds
    max_llm_calls_per_session: int  # 1000 default
    max_vllm_tokens_per_call: int  # 1500 default

    # Routing thresholds
    ml_routing_confidence_min: float  # 0.7 default
    deterministic_fallback_threshold: float  # 0.5 default
```

---

## Staged Threshold Update Protocol

### Stage 1: Proposal
```python
class ThresholdProposal:
    """Propose threshold changes for review"""

    def propose_threshold_update(self, changes: Dict[str, Any],
                                 rationale: str) -> PolicyEpoch:
        """
        Create new policy epoch in STAGED status.

        REQUIREMENTS:
        - Changes must be validated against schema
        - Rationale must be provided
        - Parent epoch must be identified
        - No live mutation allowed
        """

        # Validate changes
        self._validate_threshold_changes(changes)

        # Create new epoch
        new_epoch = PolicyEpoch(
            epoch_id=str(uuid.uuid4()),
            version=self._get_next_version(),
            created_at=datetime.now().isoformat(),
            activated_at=None,
            deactivated_at=None,
            status="STAGED",
            threshold_config=self._apply_changes(
                self._get_current_config(),
                changes
            ),
            approved_by=None,
            approval_timestamp=None,
            shadow_evaluation=None,
            parent_epoch_id=self._get_current_epoch_id(),
            change_log=[f"Proposed: {rationale}"]
        )

        # Store in staging area
        self.staging_store.save(new_epoch)

        return new_epoch

    def _validate_threshold_changes(self, changes: Dict[str, Any]):
        """Validate threshold changes against constraints"""

        # Safety threshold constraints
        if "high_confidence_threshold" in changes:
            if not 0.7 <= changes["high_confidence_threshold"] <= 0.95:
                raise ValueError("high_confidence_threshold must be in [0.7, 0.95]")

        if "medium_confidence_threshold" in changes:
            if not 0.3 <= changes["medium_confidence_threshold"] <= 0.7:
                raise ValueError("medium_confidence_threshold must be in [0.3, 0.7]")

        # Safety timeout constraints
        if "safety_timeout_ms" in changes:
            if not 100 <= changes["safety_timeout_ms"] <= 5000:
                raise ValueError("safety_timeout_ms must be in [100, 5000]")

        # Budget constraints
        if "max_healing_operations" in changes:
            if not 10 <= changes["max_healing_operations"] <= 10000:
                raise ValueError("max_healing_operations must be in [10, 10000]")
```

### Stage 2: Shadow Evaluation
```python
@dataclass
class ShadowEvaluationResult:
    runs_completed: int
    runs_required: int  # N runs before activation
    success_rate: float
    error_rate: float
    performance_delta: float  # vs current epoch
    anomaly_count: int
    evaluation_start: str
    evaluation_end: Optional[str]
    status: str  # "IN_PROGRESS", "PASSED", "FAILED"
    failure_reasons: List[str]

class ShadowEvaluator:
    """Evaluate staged thresholds in shadow mode"""

    def start_shadow_evaluation(self, epoch_id: str, runs_required: int = 100):
        """
        Start shadow evaluation for staged epoch.

        REQUIREMENTS:
        - Staged epoch must exist
        - Current epoch continues to be active
        - Shadow epoch runs in parallel (no mutations)
        - Minimum N runs required before activation
        """

        epoch = self.staging_store.get(epoch_id)
        if epoch.status != "STAGED":
            raise ValueError(f"Epoch {epoch_id} is not in STAGED status")

        # Update epoch to SHADOW status
        epoch.status = "SHADOW"
        epoch.shadow_evaluation = ShadowEvaluationResult(
            runs_completed=0,
            runs_required=runs_required,
            success_rate=0.0,
            error_rate=0.0,
            performance_delta=0.0,
            anomaly_count=0,
            evaluation_start=datetime.now().isoformat(),
            evaluation_end=None,
            status="IN_PROGRESS",
            failure_reasons=[]
        )

        self.staging_store.save(epoch)

        # Start shadow runner
        self.shadow_runner.start(epoch_id)

    def record_shadow_run(self, epoch_id: str, run_result: Dict[str, Any]):
        """Record shadow evaluation run result"""

        epoch = self.staging_store.get(epoch_id)
        if epoch.status != "SHADOW":
            raise ValueError(f"Epoch {epoch_id} is not in SHADOW status")

        eval_result = epoch.shadow_evaluation
        eval_result.runs_completed += 1

        # Update metrics
        eval_result.success_rate = (
            (eval_result.success_rate * (eval_result.runs_completed - 1) +
             run_result["success"]) / eval_result.runs_completed
        )

        eval_result.error_rate = (
            (eval_result.error_rate * (eval_result.runs_completed - 1) +
             run_result["error"]) / eval_result.runs_completed
        )

        # Check for anomalies
        if run_result.get("anomaly_detected"):
            eval_result.anomaly_count += 1

        # Check if evaluation complete
        if eval_result.runs_completed >= eval_result.runs_required:
            self._finalize_shadow_evaluation(epoch)

        self.staging_store.save(epoch)

    def _finalize_shadow_evaluation(self, epoch: PolicyEpoch):
        """Finalize shadow evaluation and determine pass/fail"""

        eval_result = epoch.shadow_evaluation
        eval_result.evaluation_end = datetime.now().isoformat()

        # Pass criteria
        pass_criteria = {
            "min_success_rate": 0.95,  # 95% success rate required
            "max_error_rate": 0.05,    # 5% error rate max
            "max_anomaly_rate": 0.02,  # 2% anomaly rate max
            "max_performance_delta": 0.1  # 10% performance degradation max
        }

        # Check criteria
        failures = []

        if eval_result.success_rate < pass_criteria["min_success_rate"]:
            failures.append(
                f"Success rate {eval_result.success_rate:.2%} < "
                f"{pass_criteria['min_success_rate']:.2%}"
            )

        if eval_result.error_rate > pass_criteria["max_error_rate"]:
            failures.append(
                f"Error rate {eval_result.error_rate:.2%} > "
                f"{pass_criteria['max_error_rate']:.2%}"
            )

        anomaly_rate = eval_result.anomaly_count / eval_result.runs_completed
        if anomaly_rate > pass_criteria["max_anomaly_rate"]:
            failures.append(
                f"Anomaly rate {anomaly_rate:.2%} > "
                f"{pass_criteria['max_anomaly_rate']:.2%}"
            )

        # Determine status
        if failures:
            eval_result.status = "FAILED"
            eval_result.failure_reasons = failures
            epoch.change_log.append(f"Shadow evaluation FAILED: {', '.join(failures)}")
        else:
            eval_result.status = "PASSED"
            epoch.change_log.append("Shadow evaluation PASSED")
```

### Stage 3: Human Approval
```python
class ThresholdApprovalGate:
    """Human approval gate for threshold updates"""

    def request_approval(self, epoch_id: str) -> str:
        """
        Request human approval for threshold update.

        REQUIREMENTS:
        - Shadow evaluation must have PASSED
        - Approval request must include full context
        - Approval must be explicit (no auto-approval)
        """

        epoch = self.staging_store.get(epoch_id)

        # Verify shadow evaluation passed
        if not epoch.shadow_evaluation or epoch.shadow_evaluation.status != "PASSED":
            raise ValueError(
                f"Epoch {epoch_id} has not passed shadow evaluation"
            )

        # Generate approval request
        approval_request = self._generate_approval_request(epoch)

        # Submit to approval queue
        approval_id = self.approval_queue.submit(approval_request)

        epoch.change_log.append(f"Approval requested: {approval_id}")
        self.staging_store.save(epoch)

        return approval_id

    def approve_threshold_update(self, epoch_id: str, approver_id: str):
        """
        Approve threshold update for activation.

        REQUIREMENTS:
        - Approver must have authority
        - Approval must be logged
        - Epoch transitions to ready for activation
        """

        epoch = self.staging_store.get(epoch_id)

        # Verify approver authority
        if not self._verify_approver_authority(approver_id):
            raise PermissionError(f"Approver {approver_id} lacks authority")

        # Record approval
        epoch.approved_by = approver_id
        epoch.approval_timestamp = datetime.now().isoformat()
        epoch.change_log.append(f"Approved by {approver_id}")

        self.staging_store.save(epoch)

    def reject_threshold_update(self, epoch_id: str, approver_id: str,
                                reason: str):
        """Reject threshold update"""

        epoch = self.staging_store.get(epoch_id)

        # Record rejection
        epoch.status = "REJECTED"
        epoch.change_log.append(f"Rejected by {approver_id}: {reason}")

        self.staging_store.save(epoch)
```

### Stage 4: Activation
```python
class ThresholdActivator:
    """Activate approved threshold updates"""

    def activate_epoch(self, epoch_id: str):
        """
        Activate approved epoch.

        REQUIREMENTS:
        - Epoch must be approved
        - No active sessions can be running
        - Activation must be atomic
        - Previous epoch must be deactivated
        """

        epoch = self.staging_store.get(epoch_id)

        # Verify approval
        if not epoch.approved_by:
            raise ValueError(f"Epoch {epoch_id} has not been approved")

        # Check for active sessions
        if self._has_active_sessions():
            raise RuntimeError("Cannot activate epoch while sessions are active")

        # Atomic activation
        with self.activation_lock:
            # Deactivate current epoch
            current_epoch = self._get_current_epoch()
            current_epoch.status = "DEPRECATED"
            current_epoch.deactivated_at = datetime.now().isoformat()
            self.epoch_store.save(current_epoch)

            # Activate new epoch
            epoch.status = "ACTIVE"
            epoch.activated_at = datetime.now().isoformat()
            epoch.change_log.append("Activated")

            # Move from staging to active store
            self.epoch_store.save(epoch)
            self.staging_store.delete(epoch_id)

            # Update current epoch pointer
            self._set_current_epoch(epoch_id)

    def _has_active_sessions(self) -> bool:
        """Check if any healing sessions are active"""
        return self.session_manager.get_active_count() > 0
```

---

## Hard Requirements

### Safety Threshold Updates
```python
SAFETY_THRESHOLD_CONSTRAINTS = {
    "high_confidence_threshold": {
        "min": 0.70,
        "max": 0.95,
        "requires_approval": True,
        "shadow_runs_required": 100
    },
    "medium_confidence_threshold": {
        "min": 0.30,
        "max": 0.70,
        "requires_approval": True,
        "shadow_runs_required": 100
    },
    "safety_timeout_ms": {
        "min": 100,
        "max": 5000,
        "requires_approval": True,
        "shadow_runs_required": 50
    }
}
```

### Routing Threshold Updates
```python
ROUTING_THRESHOLD_CONSTRAINTS = {
    "ml_routing_confidence_min": {
        "min": 0.60,
        "max": 0.90,
        "requires_approval": False,  # Can auto-activate after shadow
        "shadow_runs_required": 200
    },
    "deterministic_fallback_threshold": {
        "min": 0.40,
        "max": 0.70,
        "requires_approval": False,
        "shadow_runs_required": 200
    }
}
```

### Meta-Learning Threshold Updates
```python
META_LEARNING_THRESHOLD_CONSTRAINTS = {
    "pattern_similarity_threshold": {
        "min": 0.60,
        "max": 0.95,
        "requires_approval": False,
        "shadow_runs_required": 300
    },
    "min_success_rate": {
        "min": 0.50,
        "max": 0.90,
        "requires_approval": False,
        "shadow_runs_required": 300
    }
}
```

---

## Invariants

1. **No live threshold mutation during active sessions**
2. **Safety threshold updates require human approval**
3. **Routing threshold updates require shadow evaluation pass**
4. **All threshold updates must be versioned**
5. **All threshold updates must be rollback-capable**
6. **Shadow evaluation requires minimum N runs**
7. **Activation must be atomic**
8. **Previous epoch must be deactivated before new activation**

---

## Rollback Protocol

```python
class EpochRollback:
    """Rollback to previous policy epoch"""

    def rollback_to_epoch(self, target_epoch_id: str):
        """
        Rollback to previous epoch.

        REQUIREMENTS:
        - Target epoch must exist
        - Target epoch must be DEPRECATED (not REJECTED)
        - No active sessions
        - Rollback must be atomic
        """

        target_epoch = self.epoch_store.get(target_epoch_id)

        # Verify target epoch is valid for rollback
        if target_epoch.status not in ["DEPRECATED", "ACTIVE"]:
            raise ValueError(
                f"Cannot rollback to epoch with status {target_epoch.status}"
            )

        # Check for active sessions
        if self._has_active_sessions():
            raise RuntimeError("Cannot rollback while sessions are active")

        # Atomic rollback
        with self.activation_lock:
            # Deactivate current epoch
            current_epoch = self._get_current_epoch()
            current_epoch.status = "DEPRECATED"
            current_epoch.deactivated_at = datetime.now().isoformat()
            current_epoch.change_log.append(f"Rolled back to {target_epoch_id}")
            self.epoch_store.save(current_epoch)

            # Reactivate target epoch
            target_epoch.status = "ACTIVE"
            target_epoch.activated_at = datetime.now().isoformat()
            target_epoch.change_log.append("Reactivated via rollback")
            self.epoch_store.save(target_epoch)

            # Update current epoch pointer
            self._set_current_epoch(target_epoch_id)

    def emergency_rollback(self):
        """Emergency rollback to last known good epoch"""

        current_epoch = self._get_current_epoch()

        # Find parent epoch
        if not current_epoch.parent_epoch_id:
            raise ValueError("No parent epoch for rollback")

        # Immediate rollback
        self.rollback_to_epoch(current_epoch.parent_epoch_id)
```

---

## Versioning Strategy

```python
class EpochVersioning:
    """Epoch versioning and lineage tracking"""

    def get_epoch_lineage(self, epoch_id: str) -> List[PolicyEpoch]:
        """Get full lineage of epoch (parent chain)"""

        lineage = []
        current_id = epoch_id

        while current_id:
            epoch = self.epoch_store.get(current_id)
            lineage.append(epoch)
            current_id = epoch.parent_epoch_id

        return lineage

    def get_version_diff(self, epoch_id_a: str, epoch_id_b: str) -> Dict[str, Any]:
        """Get diff between two epoch versions"""

        epoch_a = self.epoch_store.get(epoch_id_a)
        epoch_b = self.epoch_store.get(epoch_id_b)

        # Compare threshold configs
        diff = {}

        for field in epoch_a.threshold_config.__dataclass_fields__:
            value_a = getattr(epoch_a.threshold_config, field)
            value_b = getattr(epoch_b.threshold_config, field)

            if value_a != value_b:
                diff[field] = {
                    "old": value_a,
                    "new": value_b,
                    "delta": value_b - value_a if isinstance(value_a, (int, float)) else None
                }

        return diff
```

---

## Monitoring Requirements

All epoch operations must emit:
- Epoch ID
- Operation type (PROPOSE, SHADOW, APPROVE, ACTIVATE, ROLLBACK)
- Status change
- Approver ID (if applicable)
- Timestamp
- Change log entry

Shadow evaluation must emit:
- Run count
- Success rate
- Error rate
- Anomaly count
- Performance delta
- Pass/fail status

---

## Failure Modes

| Failure | Action | Recovery |
|---------|--------|----------|
| Shadow evaluation fails | Reject epoch, log failures | Revise thresholds, re-propose |
| Approval timeout | Auto-reject after 7 days | Re-submit for approval |
| Activation fails | Rollback to previous epoch | Investigate activation failure |
| Rollback fails | Emergency stop, manual intervention | Restore from backup |

---

## Storage Schema

```sql
CREATE TABLE policy_epochs (
    epoch_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    activated_at TIMESTAMP,
    deactivated_at TIMESTAMP,
    status TEXT NOT NULL,
    threshold_config_json TEXT NOT NULL,
    approved_by TEXT,
    approval_timestamp TIMESTAMP,
    shadow_evaluation_json TEXT,
    parent_epoch_id TEXT,
    change_log_json TEXT NOT NULL,
    FOREIGN KEY (parent_epoch_id) REFERENCES policy_epochs(epoch_id)
);

CREATE INDEX idx_epochs_status ON policy_epochs(status);
CREATE INDEX idx_epochs_version ON policy_epochs(version);
CREATE INDEX idx_epochs_parent ON policy_epochs(parent_epoch_id);
```
