# L6 Drift Safeguards Specification

## SCOPE
Governs: **L6 Observability Layer** (Anomaly Detection, Drift Safeguards, Threshold Mutation Control)

Defines L6 drift safeguards with anomaly confidence delta caps and distribution shift detection.

---

Anomaly confidence delta caps, distribution shift detection, and threshold mutation rate limits.

---

## Anomaly Confidence Delta Cap

```python
@dataclass
class AnomalyConfidenceDelta:
    current_confidence: float
    previous_confidence: float
    delta: float
    epoch_id: str
    timestamp: str

class AnomalyConfidenceDeltaCap:
    """Cap anomaly confidence changes per epoch"""

    def __init__(self, max_delta_per_epoch: float = 0.1):
        """
        Initialize delta cap.

        REQUIREMENTS:
        - Max delta per epoch: 0.1 (10%)
        - Larger deltas trigger freeze
        - Delta history tracked
        """

        self.max_delta_per_epoch = max_delta_per_epoch
        self.confidence_history = []
        self.current_confidence = 0.5  # Baseline

    def validate_confidence_update(self, new_confidence: float,
                                   epoch_id: str) -> Tuple[bool, str]:
        """
        Validate confidence update against delta cap.

        REQUIREMENTS:
        - Delta must be ≤ max_delta_per_epoch
        - Sudden spikes rejected
        - Gradual changes allowed
        """

        # Calculate delta
        delta = abs(new_confidence - self.current_confidence)

        # Check against cap
        if delta > self.max_delta_per_epoch:
            return False, f"Delta {delta:.3f} exceeds cap {self.max_delta_per_epoch}"

        # Record delta
        self._record_delta(new_confidence, epoch_id, delta)

        # Update current confidence
        self.current_confidence = new_confidence

        return True, "OK"

    def _record_delta(self, new_confidence: float, epoch_id: str, delta: float):
        """Record confidence delta"""

        self.confidence_history.append(AnomalyConfidenceDelta(
            current_confidence=new_confidence,
            previous_confidence=self.current_confidence,
            delta=delta,
            epoch_id=epoch_id,
            timestamp=datetime.now().isoformat()
        ))

    def get_delta_trend(self, window: int = 10) -> str:
        """Get delta trend over window"""

        if len(self.confidence_history) < window:
            return "INSUFFICIENT_DATA"

        recent_deltas = [d.delta for d in self.confidence_history[-window:]]
        avg_delta = sum(recent_deltas) / len(recent_deltas)

        if avg_delta > self.max_delta_per_epoch * 0.8:
            return "HIGH_VOLATILITY"
        elif avg_delta > self.max_delta_per_epoch * 0.5:
            return "MODERATE_VOLATILITY"
        else:
            return "STABLE"
```

---

## Distribution Shift Detection

```python
@dataclass
class DistributionShiftMetrics:
    kl_divergence: float
    js_divergence: float
    wasserstein_distance: float
    shift_detected: bool
    timestamp: str

class DistributionShiftDetector:
    """Detect distribution shifts in anomaly patterns"""

    def __init__(self, shift_threshold: float = 0.2):
        """
        Initialize shift detector.

        REQUIREMENTS:
        - Track anomaly distribution over time
        - Detect significant shifts
        - Trigger freeze on shift
        """

        self.shift_threshold = shift_threshold
        self.baseline_distribution = None
        self.current_distribution = None
        self.shift_history = []

    def update_distribution(self, anomaly_samples: List[float]):
        """Update current distribution from samples"""

        import numpy as np

        # Build histogram
        hist, bins = np.histogram(anomaly_samples, bins=20, density=True)

        # Store distribution
        if self.baseline_distribution is None:
            self.baseline_distribution = hist
            self.current_distribution = hist
        else:
            self.current_distribution = hist

    def detect_shift(self) -> Tuple[bool, DistributionShiftMetrics]:
        """
        Detect distribution shift.

        METHODS:
        - KL divergence
        - JS divergence
        - Wasserstein distance
        """

        if self.baseline_distribution is None:
            return False, None

        # Calculate divergences
        kl_div = self._kl_divergence(self.baseline_distribution,
                                     self.current_distribution)

        js_div = self._js_divergence(self.baseline_distribution,
                                     self.current_distribution)

        wasserstein = self._wasserstein_distance(self.baseline_distribution,
                                                 self.current_distribution)

        # Detect shift (any metric exceeds threshold)
        shift_detected = (
            kl_div > self.shift_threshold or
            js_div > self.shift_threshold or
            wasserstein > self.shift_threshold
        )

        # Create metrics
        metrics = DistributionShiftMetrics(
            kl_divergence=kl_div,
            js_divergence=js_div,
            wasserstein_distance=wasserstein,
            shift_detected=shift_detected,
            timestamp=datetime.now().isoformat()
        )

        # Record shift
        self.shift_history.append(metrics)

        return shift_detected, metrics

    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate KL divergence KL(P||Q)"""

        import numpy as np

        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        p = p + epsilon
        q = q + epsilon

        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)

        # Calculate KL divergence
        return np.sum(p * np.log(p / q))

    def _js_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Jensen-Shannon divergence"""

        import numpy as np

        # Calculate M = (P + Q) / 2
        m = (p + q) / 2

        # JS divergence = (KL(P||M) + KL(Q||M)) / 2
        return (self._kl_divergence(p, m) + self._kl_divergence(q, m)) / 2

    def _wasserstein_distance(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Wasserstein distance (Earth Mover's Distance)"""

        import numpy as np

        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)

        # Calculate cumulative distributions
        p_cumsum = np.cumsum(p)
        q_cumsum = np.cumsum(q)

        # Wasserstein distance = L1 distance between CDFs
        return np.sum(np.abs(p_cumsum - q_cumsum))

    def trigger_freeze(self, metrics: DistributionShiftMetrics):
        """Trigger freeze on distribution shift"""

        print(f"FREEZE: Distribution shift detected")
        print(f"  KL divergence: {metrics.kl_divergence:.4f}")
        print(f"  JS divergence: {metrics.js_divergence:.4f}")
        print(f"  Wasserstein: {metrics.wasserstein_distance:.4f}")

        # Emit freeze event
        self._emit_freeze_event(metrics)

    def _emit_freeze_event(self, metrics: DistributionShiftMetrics):
        """Emit freeze event for monitoring"""

        # Log to L6 observability
        pass
```

---

## Threshold Mutation Rate Limits

```python
@dataclass
class ThresholdMutation:
    threshold_name: str
    old_value: float
    new_value: float
    delta: float
    epoch_id: str
    timestamp: str

class ThresholdMutationRateLimiter:
    """Limit rate of threshold mutations"""

    def __init__(self, max_mutations_per_hour: int = 5,
                 max_delta_per_mutation: float = 0.05):
        """
        Initialize rate limiter.

        REQUIREMENTS:
        - Max 5 mutations per hour
        - Max 0.05 (5%) delta per mutation
        - Cooldown period between mutations
        """

        self.max_mutations_per_hour = max_mutations_per_hour
        self.max_delta_per_mutation = max_delta_per_mutation
        self.mutation_history = []
        self.cooldown_seconds = 600  # 10 minutes

    def validate_mutation(self, threshold_name: str,
                         old_value: float, new_value: float,
                         epoch_id: str) -> Tuple[bool, str]:
        """
        Validate threshold mutation against rate limits.

        CHECKS:
        - Mutations per hour
        - Delta per mutation
        - Cooldown period
        """

        # Calculate delta
        delta = abs(new_value - old_value)

        # Check delta limit
        if delta > self.max_delta_per_mutation:
            return False, f"Delta {delta:.3f} exceeds limit {self.max_delta_per_mutation}"

        # Check rate limit
        recent_mutations = self._get_recent_mutations(hours=1)
        if len(recent_mutations) >= self.max_mutations_per_hour:
            return False, f"Rate limit exceeded: {len(recent_mutations)} mutations in last hour"

        # Check cooldown
        if not self._check_cooldown(threshold_name):
            return False, f"Cooldown period active for {threshold_name}"

        # Record mutation
        self._record_mutation(threshold_name, old_value, new_value, delta, epoch_id)

        return True, "OK"

    def _get_recent_mutations(self, hours: int) -> List[ThresholdMutation]:
        """Get mutations within last N hours"""

        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=hours)

        return [
            m for m in self.mutation_history
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]

    def _check_cooldown(self, threshold_name: str) -> bool:
        """Check if cooldown period has passed"""

        from datetime import datetime, timedelta

        # Find last mutation for this threshold
        for mutation in reversed(self.mutation_history):
            if mutation.threshold_name == threshold_name:
                last_mutation_time = datetime.fromisoformat(mutation.timestamp)
                cooldown_end = last_mutation_time + timedelta(seconds=self.cooldown_seconds)

                if datetime.now() < cooldown_end:
                    return False
                break

        return True

    def _record_mutation(self, threshold_name: str, old_value: float,
                        new_value: float, delta: float, epoch_id: str):
        """Record threshold mutation"""

        self.mutation_history.append(ThresholdMutation(
            threshold_name=threshold_name,
            old_value=old_value,
            new_value=new_value,
            delta=delta,
            epoch_id=epoch_id,
            timestamp=datetime.now().isoformat()
        ))
```

---

## Shadow Anomaly Classifier Evaluation

```python
class ShadowAnomalyClassifier:
    """Shadow classifier for evaluation before activation"""

    def __init__(self, baseline_classifier):
        """
        Initialize shadow classifier.

        REQUIREMENTS:
        - Runs in parallel with baseline
        - No impact on production
        - Evaluation before activation
        """

        self.baseline_classifier = baseline_classifier
        self.shadow_classifier = None
        self.evaluation_results = []

    def start_shadow_evaluation(self, new_classifier, runs_required: int = 1000):
        """Start shadow evaluation"""

        self.shadow_classifier = new_classifier
        self.runs_required = runs_required
        self.runs_completed = 0

    def evaluate_sample(self, sample: Dict[str, Any]):
        """Evaluate sample with both classifiers"""

        if not self.shadow_classifier:
            return

        # Baseline classification
        baseline_result = self.baseline_classifier.classify(sample)

        # Shadow classification
        shadow_result = self.shadow_classifier.classify(sample)

        # Record results
        self.evaluation_results.append({
            'sample': sample,
            'baseline': baseline_result,
            'shadow': shadow_result,
            'match': baseline_result == shadow_result,
            'timestamp': datetime.now().isoformat()
        })

        self.runs_completed += 1

    def finalize_evaluation(self) -> Dict[str, Any]:
        """Finalize shadow evaluation"""

        if self.runs_completed < self.runs_required:
            return {
                'status': 'INCOMPLETE',
                'runs_completed': self.runs_completed,
                'runs_required': self.runs_required
            }

        # Calculate metrics
        total = len(self.evaluation_results)
        matches = sum(1 for r in self.evaluation_results if r['match'])
        match_rate = matches / total if total > 0 else 0

        # Calculate false positive/negative rates
        fp_rate = self._calculate_false_positive_rate()
        fn_rate = self._calculate_false_negative_rate()

        # Determine pass/fail
        passed = (
            match_rate >= 0.95 and  # 95% agreement
            fp_rate <= 0.05 and     # 5% false positive max
            fn_rate <= 0.05         # 5% false negative max
        )

        return {
            'status': 'PASSED' if passed else 'FAILED',
            'runs_completed': self.runs_completed,
            'match_rate': match_rate,
            'false_positive_rate': fp_rate,
            'false_negative_rate': fn_rate
        }

    def _calculate_false_positive_rate(self) -> float:
        """Calculate false positive rate"""

        # Shadow classified as anomaly, baseline did not
        fp_count = sum(
            1 for r in self.evaluation_results
            if r['shadow']['is_anomaly'] and not r['baseline']['is_anomaly']
        )

        total_negatives = sum(
            1 for r in self.evaluation_results
            if not r['baseline']['is_anomaly']
        )

        return fp_count / total_negatives if total_negatives > 0 else 0

    def _calculate_false_negative_rate(self) -> float:
        """Calculate false negative rate"""

        # Shadow did not classify as anomaly, baseline did
        fn_count = sum(
            1 for r in self.evaluation_results
            if not r['shadow']['is_anomaly'] and r['baseline']['is_anomaly']
        )

        total_positives = sum(
            1 for r in self.evaluation_results
            if r['baseline']['is_anomaly']
        )

        return fn_count / total_positives if total_positives > 0 else 0
```

---

## L6 Drift Safeguard Integration

```python
class L6DriftSafeguardManager:
    """Manage all L6 drift safeguards"""

    def __init__(self):
        """Initialize all safeguards"""

        self.confidence_delta_cap = AnomalyConfidenceDeltaCap(max_delta_per_epoch=0.1)
        self.shift_detector = DistributionShiftDetector(shift_threshold=0.2)
        self.mutation_rate_limiter = ThresholdMutationRateLimiter(
            max_mutations_per_hour=5,
            max_delta_per_mutation=0.05
        )
        self.shadow_classifier = None

        self.frozen = False
        self.freeze_reason = None

    def validate_anomaly_update(self, new_confidence: float,
                               anomaly_samples: List[float],
                               epoch_id: str) -> Tuple[bool, str]:
        """
        Validate anomaly update against all safeguards.

        CHECKS:
        1. Confidence delta cap
        2. Distribution shift
        3. Mutation rate limit
        4. Freeze status
        """

        # Check if frozen
        if self.frozen:
            return False, f"L6 frozen: {self.freeze_reason}"

        # Check confidence delta
        valid, error = self.confidence_delta_cap.validate_confidence_update(
            new_confidence, epoch_id
        )
        if not valid:
            self._trigger_freeze(f"Confidence delta cap exceeded: {error}")
            return False, error

        # Check distribution shift
        self.shift_detector.update_distribution(anomaly_samples)
        shift_detected, metrics = self.shift_detector.detect_shift()

        if shift_detected:
            self._trigger_freeze(f"Distribution shift detected")
            self.shift_detector.trigger_freeze(metrics)
            return False, "Distribution shift detected"

        return True, "OK"

    def validate_threshold_mutation(self, threshold_name: str,
                                   old_value: float, new_value: float,
                                   epoch_id: str) -> Tuple[bool, str]:
        """Validate threshold mutation"""

        # Check if frozen
        if self.frozen:
            return False, f"L6 frozen: {self.freeze_reason}"

        # Check mutation rate limit
        valid, error = self.mutation_rate_limiter.validate_mutation(
            threshold_name, old_value, new_value, epoch_id
        )

        if not valid:
            self._trigger_freeze(f"Mutation rate limit exceeded: {error}")
            return False, error

        return True, "OK"

    def _trigger_freeze(self, reason: str):
        """Trigger L6 freeze"""

        self.frozen = True
        self.freeze_reason = reason

        print(f"L6 FREEZE TRIGGERED: {reason}")

        # Emit freeze event
        self._emit_freeze_event(reason)

    def _emit_freeze_event(self, reason: str):
        """Emit freeze event for monitoring"""

        # Log to L6 observability
        pass

    def unfreeze(self, approver_id: str):
        """Unfreeze L6 (requires approval)"""

        if not self._verify_approver_authority(approver_id):
            raise PermissionError(f"Approver {approver_id} lacks authority")

        self.frozen = False
        self.freeze_reason = None

        print(f"L6 UNFROZEN by {approver_id}")

    def _verify_approver_authority(self, approver_id: str) -> bool:
        """Verify approver has authority to unfreeze"""

        # Check against authorized approvers list
        return True  # Placeholder
```

---

## Invariants

1. **Anomaly confidence delta ≤ 0.1 per epoch**
2. **Distribution shift triggers freeze**
3. **Max 5 threshold mutations per hour**
4. **Max 0.05 delta per threshold mutation**
5. **Shadow classifier must pass evaluation before activation**
6. **Freeze requires manual unfreeze**

---

## Monitoring Requirements

All L6 drift events must emit:
- Confidence delta
- Distribution shift metrics
- Mutation count
- Freeze status
- Freeze reason
- Unfreeze approver

All safeguard violations must be logged:
- Violation type
- Threshold values
- Epoch ID
- Timestamp
- Action taken

---

## Failure Modes

| Failure | Action | Recovery |
|---------|--------|----------|
| Confidence delta exceeded | Freeze L6 | Manual review + unfreeze |
| Distribution shift detected | Freeze L6 | Investigate shift + unfreeze |
| Mutation rate exceeded | Freeze L6 | Wait cooldown + unfreeze |
| Shadow evaluation failed | Reject classifier | Retrain + re-evaluate |
