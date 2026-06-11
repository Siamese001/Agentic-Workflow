---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\L0_DECOMPOSITION_SPEC.md'
original_relative_path: 'L0_DECOMPOSITION_SPEC.md'
source_sha256: f5945b3ea8cb11fa91a8f812c78b0bb17a848c7d4d4626b11e7edf1eb88f1c49
recovered_status: LOST_RECOVERED
last_commit: 'd399bca49f2'
last_commit_date: '2026-02-23 08:15:26 -0500'
created_date: '2026-02-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L0 Routing Decomposition Specification

## SCOPE
Governs: **L0 Layer** (L0a Cryptographic Ingress Gate, L0b Deterministic Router, L0c Dispatch Sealer)

Defines decomposition of L0 routing authority into three sublayers with explicit boundaries.

---

L0 routing layer decomposed into three isolated components with explicit authority boundaries.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         L0 ROUTING                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ L0a: Cryptographic Ingress Gate                      │  │
│  │ • Hash verification                                   │  │
│  │ • Trace binding                                       │  │
│  │ • Policy hash stamping                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ L0b: Deterministic Router                            │  │
│  │ • Rule-table routing                                  │  │
│  │ • Capability arbitration                              │  │
│  │ • Budget enforcement                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ L0c: Dispatch Sealer                                 │  │
│  │ • DAG emission                                        │  │
│  │ • Route mode stamping                                 │  │
│  │ • InstructionPacket sealing                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

ML Routing: Advisory-only, cannot directly select final path
```

---

## L0a: Cryptographic Ingress Gate

### Responsibilities
- HMAC verification of incoming requests
- Trace ID binding and validation
- Policy hash stamping for audit trail
- Request integrity validation

### Interface
```python
@dataclass
class IngressValidationResult:
    valid: bool
    trace_id: str
    policy_hash: str
    hmac_verified: bool
    timestamp: str
    rejection_reason: Optional[str] = None

class CryptographicIngressGate:
    """L0a: Entry point for all execute_ssot operations"""

    def validate_ingress(self, request: ExecutionRequest) -> IngressValidationResult:
        """
        Validate cryptographic integrity of incoming request.

        HARD REQUIREMENTS:
        - HMAC must be valid
        - Trace ID must be monotonically increasing
        - Policy hash must match current epoch
        - Timestamp must be within acceptable skew

        FAILURE BEHAVIOR:
        - Invalid HMAC → Abort, no retry
        - Stale policy hash → Reject, escalate to Path D
        - Trace ID collision → Abort, log security event
        """

        # 1. HMAC verification
        if not self._verify_hmac(request):
            return IngressValidationResult(
                valid=False,
                trace_id="",
                policy_hash="",
                hmac_verified=False,
                timestamp="",
                rejection_reason="HMAC_VERIFICATION_FAILED"
            )

        # 2. Trace ID validation
        if not self._validate_trace_id(request.trace_id):
            return IngressValidationResult(
                valid=False,
                trace_id=request.trace_id,
                policy_hash="",
                hmac_verified=True,
                timestamp="",
                rejection_reason="TRACE_ID_INVALID"
            )

        # 3. Policy hash stamping
        current_policy_hash = self._get_current_policy_hash()
        if request.policy_hash != current_policy_hash:
            return IngressValidationResult(
                valid=False,
                trace_id=request.trace_id,
                policy_hash=current_policy_hash,
                hmac_verified=True,
                timestamp="",
                rejection_reason="POLICY_HASH_MISMATCH"
            )

        # 4. Timestamp validation
        if not self._validate_timestamp(request.timestamp):
            return IngressValidationResult(
                valid=False,
                trace_id=request.trace_id,
                policy_hash=current_policy_hash,
                hmac_verified=True,
                timestamp=request.timestamp,
                rejection_reason="TIMESTAMP_SKEW_EXCEEDED"
            )

        return IngressValidationResult(
            valid=True,
            trace_id=request.trace_id,
            policy_hash=current_policy_hash,
            hmac_verified=True,
            timestamp=request.timestamp
        )

    def _verify_hmac(self, request: ExecutionRequest) -> bool:
        """Verify HMAC signature using shared secret"""
        import hmac
        import hashlib

        expected_hmac = hmac.new(
            key=self.shared_secret.encode(),
            msg=request.payload.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_hmac, request.hmac)

    def _validate_trace_id(self, trace_id: str) -> bool:
        """Ensure trace ID is monotonically increasing"""
        if not trace_id:
            return False

        # Check against last seen trace ID
        last_trace_id = self._get_last_trace_id()
        if last_trace_id and trace_id <= last_trace_id:
            return False

        return True

    def _get_current_policy_hash(self) -> str:
        """Get current policy epoch hash from L4"""
        return self.policy_store.get_current_epoch_hash()

    def _validate_timestamp(self, timestamp: str) -> bool:
        """Validate timestamp is within acceptable skew (±5 minutes)"""
        from datetime import datetime, timedelta

        request_time = datetime.fromisoformat(timestamp)
        current_time = datetime.now()
        skew = abs((current_time - request_time).total_seconds())

        return skew <= 300  # 5 minutes
```

### Invariants
1. **No execution without valid HMAC**
2. **Trace IDs must be monotonically increasing**
3. **Policy hash must match current epoch**
4. **Timestamp skew must be ≤ 5 minutes**

### Failure Modes
| Failure | Action | Escalation |
|---------|--------|------------|
| HMAC invalid | Abort, no retry | Log security event |
| Trace ID collision | Abort, flag replay attack | Escalate to L5 |
| Policy hash stale | Reject, return current hash | Path D |
| Timestamp skew | Reject, log clock drift | None |

---

## L0b: Deterministic Router

### Responsibilities
- Rule-table based routing decisions
- Capability arbitration between paths
- Budget enforcement and tracking
- ML routing advisory integration (non-binding)

### Interface
```python
@dataclass
class RoutingDecision:
    path: str  # "A", "B", "C", "D"
    confidence: float
    rule_matched: str
    ml_advisory: Optional[str] = None
    budget_remaining: int = 0
    capabilities_required: List[str] = field(default_factory=list)

class DeterministicRouter:
    """L0b: Rule-based routing with ML advisory"""

    def route_request(self, validated_request: IngressValidationResult,
                     violation: Dict[str, Any]) -> RoutingDecision:
        """
        Determine execution path using deterministic rule table.

        HARD REQUIREMENTS:
        - Rule table must be consulted first
        - ML routing is advisory-only
        - Budget must be checked before routing
        - Final path selection is deterministic

        ROUTING PRIORITY:
        1. Budget enforcement (hard gate)
        2. Rule table match (deterministic)
        3. ML advisory (non-binding suggestion)
        4. Default path selection (safest)
        """

        # 1. Budget enforcement (hard gate)
        if not self._check_budget():
            return RoutingDecision(
                path="D",
                confidence=1.0,
                rule_matched="BUDGET_EXHAUSTED",
                budget_remaining=0
            )

        # 2. Rule table routing (deterministic)
        rule_decision = self._match_routing_rules(violation)
        if rule_decision:
            return rule_decision

        # 3. ML advisory (non-binding)
        ml_suggestion = self._get_ml_advisory(violation)

        # 4. Final path selection (deterministic override)
        final_path = self._select_final_path(rule_decision, ml_suggestion)

        return RoutingDecision(
            path=final_path,
            confidence=rule_decision.confidence if rule_decision else 0.5,
            rule_matched=rule_decision.rule_matched if rule_decision else "DEFAULT",
            ml_advisory=ml_suggestion,
            budget_remaining=self._get_budget_remaining(),
            capabilities_required=self._get_required_capabilities(final_path)
        )

    def _check_budget(self) -> bool:
        """Check if budget allows execution"""
        current_budget = self.budget_tracker.get_remaining()
        return current_budget > 0

    def _match_routing_rules(self, violation: Dict[str, Any]) -> Optional[RoutingDecision]:
        """Match violation against deterministic rule table"""

        # Rule table structure:
        # [
        #   {
        #     "condition": {"violation_type": "IMPORT_CYCLE", "confidence": ">0.8"},
        #     "path": "A",
        #     "rule_id": "R001"
        #   },
        #   ...
        # ]

        for rule in self.routing_rules:
            if self._evaluate_rule_condition(rule["condition"], violation):
                return RoutingDecision(
                    path=rule["path"],
                    confidence=1.0,  # Rule match = 100% confidence
                    rule_matched=rule["rule_id"],
                    budget_remaining=self._get_budget_remaining()
                )

        return None

    def _get_ml_advisory(self, violation: Dict[str, Any]) -> Optional[str]:
        """Get ML routing suggestion (advisory-only)"""

        # Check if L6 is available
        if not self.l6_available:
            return None

        # Get ML suggestion
        try:
            ml_path = self.ml_router.suggest_path(violation)
            return ml_path
        except Exception as e:
            # ML failure does not block routing
            return None

    def _select_final_path(self, rule_decision: Optional[RoutingDecision],
                          ml_suggestion: Optional[str]) -> str:
        """
        Select final path with deterministic override.

        PRIORITY:
        1. Rule decision (if exists)
        2. Default safe path (Path A)

        ML suggestion is logged but NEVER directly used for final selection.
        """

        if rule_decision:
            return rule_decision.path

        # Default to safest path
        return "A"

    def _get_required_capabilities(self, path: str) -> List[str]:
        """Get capabilities required for path"""
        capability_map = {
            "A": ["L5_SAFETY", "L2_EXECUTION"],
            "B": ["L5_SAFETY", "L2_EXECUTION", "L1_COGNITION"],
            "C": ["L6_OBSERVABILITY"],
            "D": ["HUMAN_APPROVAL"]
        }
        return capability_map.get(path, [])
```

### Invariants
1. **Budget check is mandatory before routing**
2. **Rule table consulted before ML advisory**
3. **ML routing cannot directly select final path**
4. **Default path is always deterministic (Path A)**

### Failure Modes
| Failure | Action | Escalation |
|---------|--------|------------|
| Budget exhausted | Force Path D | None |
| Rule table corrupted | Force Path A | Log corruption event |
| ML advisory fails | Ignore, use rule decision | None |
| No rule match | Default to Path A | None |

---

## L0c: Dispatch Sealer

### Responsibilities
- DAG (Directed Acyclic Graph) emission
- Route mode stamping for audit
- InstructionPacket sealing with HMAC
- Execution trace initialization

### Interface
```python
@dataclass
class SealedDispatch:
    instruction_packet: InstructionPacket
    dag: ExecutionDAG
    route_mode: str
    seal_hmac: str
    trace_id: str
    timestamp: str

class DispatchSealer:
    """L0c: Seal and emit execution instructions"""

    def seal_dispatch(self, routing_decision: RoutingDecision,
                     violation: Dict[str, Any],
                     validated_request: IngressValidationResult) -> SealedDispatch:
        """
        Seal execution dispatch with cryptographic integrity.

        HARD REQUIREMENTS:
        - InstructionPacket must be sealed with HMAC
        - DAG must be acyclic and validated
        - Route mode must be stamped for audit
        - Trace ID must be bound to dispatch

        FAILURE BEHAVIOR:
        - Sealing failure → Abort, escalate to L5
        - DAG cycle detected → Abort, log violation
        - HMAC generation fails → Abort, log crypto failure
        """

        # 1. Build InstructionPacket
        instruction_packet = self._build_instruction_packet(
            routing_decision,
            violation
        )

        # 2. Build execution DAG
        dag = self._build_execution_dag(routing_decision.path, violation)

        # 3. Validate DAG is acyclic
        if not self._validate_dag_acyclic(dag):
            raise ValueError("DAG contains cycle - execution would deadlock")

        # 4. Stamp route mode
        route_mode = self._stamp_route_mode(routing_decision)

        # 5. Generate seal HMAC
        seal_hmac = self._generate_seal_hmac(
            instruction_packet,
            dag,
            route_mode,
            validated_request.trace_id
        )

        # 6. Emit sealed dispatch
        return SealedDispatch(
            instruction_packet=instruction_packet,
            dag=dag,
            route_mode=route_mode,
            seal_hmac=seal_hmac,
            trace_id=validated_request.trace_id,
            timestamp=validated_request.timestamp
        )

    def _build_instruction_packet(self, routing_decision: RoutingDecision,
                                  violation: Dict[str, Any]) -> InstructionPacket:
        """Build instruction packet for execution"""
        return InstructionPacket(
            path=routing_decision.path,
            violation=violation,
            capabilities=routing_decision.capabilities_required,
            budget_allocated=self._allocate_budget(routing_decision),
            constraints=self._build_constraints(routing_decision)
        )

    def _build_execution_dag(self, path: str, violation: Dict[str, Any]) -> ExecutionDAG:
        """Build execution DAG for path"""

        # DAG structure depends on path
        if path == "A":
            # Deterministic path: L5 → L2 → UWG
            return ExecutionDAG(
                nodes=["L5_SAFETY", "L2_EXECUTION", "UWG_MUTATION"],
                edges=[("L5_SAFETY", "L2_EXECUTION"), ("L2_EXECUTION", "UWG_MUTATION")]
            )
        elif path == "B":
            # ML path: L5 → L1 → L2 → UWG
            return ExecutionDAG(
                nodes=["L5_SAFETY", "L1_COGNITION", "L2_EXECUTION", "UWG_MUTATION"],
                edges=[
                    ("L5_SAFETY", "L1_COGNITION"),
                    ("L1_COGNITION", "L2_EXECUTION"),
                    ("L2_EXECUTION", "UWG_MUTATION")
                ]
            )
        elif path == "C":
            # Safe mode: L6 only
            return ExecutionDAG(
                nodes=["L6_OBSERVABILITY"],
                edges=[]
            )
        else:  # Path D
            # Human intervention: No execution
            return ExecutionDAG(
                nodes=["HUMAN_APPROVAL"],
                edges=[]
            )

    def _validate_dag_acyclic(self, dag: ExecutionDAG) -> bool:
        """Validate DAG contains no cycles using topological sort"""
        from collections import defaultdict, deque

        # Build adjacency list
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for node in dag.nodes:
            in_degree[node] = 0

        for src, dst in dag.edges:
            graph[src].append(dst)
            in_degree[dst] += 1

        # Topological sort (Kahn's algorithm)
        queue = deque([node for node in dag.nodes if in_degree[node] == 0])
        sorted_count = 0

        while queue:
            node = queue.popleft()
            sorted_count += 1

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If sorted_count != node count, there's a cycle
        return sorted_count == len(dag.nodes)

    def _stamp_route_mode(self, routing_decision: RoutingDecision) -> str:
        """Stamp route mode for audit trail"""
        if routing_decision.ml_advisory:
            return f"DETERMINISTIC_WITH_ML_ADVISORY:{routing_decision.path}"
        else:
            return f"DETERMINISTIC:{routing_decision.path}"

    def _generate_seal_hmac(self, instruction_packet: InstructionPacket,
                           dag: ExecutionDAG, route_mode: str, trace_id: str) -> str:
        """Generate HMAC seal for dispatch"""
        import hmac
        import hashlib
        import json

        # Canonical serialization
        payload = json.dumps({
            "instruction_packet": instruction_packet.to_dict(),
            "dag": dag.to_dict(),
            "route_mode": route_mode,
            "trace_id": trace_id
        }, sort_keys=True)

        return hmac.new(
            key=self.seal_secret.encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
```

### Invariants
1. **All dispatches must be sealed with HMAC**
2. **DAG must be acyclic (validated before sealing)**
3. **Route mode must be stamped for audit**
4. **Trace ID must be bound to dispatch**

### Failure Modes
| Failure | Action | Escalation |
|---------|--------|------------|
| Sealing fails | Abort, escalate to L5 | Critical |
| DAG cycle detected | Abort, log violation | Critical |
| HMAC generation fails | Abort, log crypto failure | Critical |
| Invalid instruction packet | Abort, log validation error | High |

---

## Integration Contract

### L0a → L0b Interface
```python
validated_request: IngressValidationResult = l0a.validate_ingress(request)
if not validated_request.valid:
    abort_with_reason(validated_request.rejection_reason)

routing_decision: RoutingDecision = l0b.route_request(validated_request, violation)
```

### L0b → L0c Interface
```python
routing_decision: RoutingDecision = l0b.route_request(validated_request, violation)

sealed_dispatch: SealedDispatch = l0c.seal_dispatch(
    routing_decision,
    violation,
    validated_request
)
```

### L0c → L2 Interface
```python
sealed_dispatch: SealedDispatch = l0c.seal_dispatch(...)

# L2 receives sealed dispatch and validates seal
if not l2.validate_seal(sealed_dispatch.seal_hmac):
    abort("Seal validation failed")

l2.execute(sealed_dispatch.instruction_packet, sealed_dispatch.dag)
```

---

## ML Routing Advisory Protocol

### Advisory-Only Constraint
```python
class MLRoutingAdvisor:
    """ML routing is advisory-only - cannot directly select path"""

    def suggest_path(self, violation: Dict[str, Any]) -> str:
        """
        Suggest path based on ML model.

        CRITICAL: This is ADVISORY ONLY.
        Final path selection is deterministic in L0b.
        """

        # Check L6 availability
        if not self.l6_anomaly_detector.is_available():
            return None  # No ML without L6

        # Get ML prediction
        ml_prediction = self.ml_model.predict(violation)

        # Return suggestion (not decision)
        return ml_prediction

    def log_advisory_vs_actual(self, ml_suggestion: str, actual_path: str):
        """Log ML advisory vs actual deterministic decision for learning"""
        self.meta_learning_bus.emit({
            "event": "ml_advisory_comparison",
            "ml_suggestion": ml_suggestion,
            "actual_path": actual_path,
            "timestamp": datetime.now().isoformat()
        })
```

### Invariant
**ML routing NEVER directly selects final path. Only L0b deterministic logic selects path.**

---

## Authority Boundaries

| Component | Authority | Cannot Do |
|-----------|-----------|-----------|
| L0a | Validate ingress, reject invalid requests | Route requests, execute code |
| L0b | Route requests, enforce budget | Mutate state, execute code |
| L0c | Seal dispatches, emit DAG | Route requests, execute code |
| ML Advisor | Suggest paths | Select final path, override rules |

---

## Failure Recovery

### L0a Failure
- Abort request immediately
- Log security event
- No retry allowed

### L0b Failure
- Default to Path A (safest)
- Log routing failure
- Continue with deterministic path

### L0c Failure
- Abort dispatch
- Escalate to L5
- No execution without seal

---

## Monitoring Requirements

All L0 components must emit:
- Component identifier (L0a/L0b/L0c)
- Operation performed
- Success/failure status
- Latency (must meet SLA)
- Degradation events

SLA Requirements:
- L0a validation: ≤ 50ms
- L0b routing: ≤ 100ms
- L0c sealing: ≤ 50ms
- **Total L0 latency: ≤ 200ms**

SLA violation → Escalate to Path D
