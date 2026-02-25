# Architectural Hardening Specifications

This directory contains formal specifications for architectural hardening of the execute_ssot unified architecture.

## Specification Index

### Core Authority & Degradation

1. **[AUTHORITY_HIERARCHY_INVARIANTS.md](./AUTHORITY_HIERARCHY_INVARIANTS.md)**
   - Governs: All Layers (L0, L1, L2, L4, L5, L6, UWG, Meta-Learning)
   - Defines formal authority hierarchy as invariant rules
   - **Cross-references:** DEGRADATION_MATRIX.md, L0_DECOMPOSITION_SPEC.md, UWG_ISOLATION_SPEC.md

2. **[DEGRADATION_MATRIX.md](./DEGRADATION_MATRIX.md)**
   - Governs: All Layers (L0, L1, L2, L4, L5, L6, UWG, Meta-Learning Bus, FAISS, Redis, vLLM, Circuit Breaker, Tracing)
   - Defines fail-closed degradation behavior for all subsystems
   - **Cross-references:** AUTHORITY_HIERARCHY_INVARIANTS.md, L6_DRIFT_SAFEGUARDS_SPEC.md, LATENCY_BUDGET_SLA_SPEC.md

### Layer-Specific Specifications

3. **[L0_DECOMPOSITION_SPEC.md](./L0_DECOMPOSITION_SPEC.md)**
   - Governs: L0 Layer (L0a Cryptographic Ingress Gate, L0b Deterministic Router, L0c Dispatch Sealer)
   - Defines L0 decomposition into three sublayers with explicit authority boundaries
   - Defines UUIDv7 trace_id monotonicity format
   - **Cross-references:** AUTHORITY_HIERARCHY_INVARIANTS.md, UWG_ISOLATION_SPEC.md, LATENCY_BUDGET_SLA_SPEC.md

4. **[REPLAY_DETERMINISM_RULES.md](./REPLAY_DETERMINISM_RULES.md)**
   - Governs: L2 Execution Layer (Deterministic Execution, Replay Validation)
   - Defines L2 determinism canonicalization rules for guaranteed replay integrity
   - **Cross-references:** HEALER_RETRY_HARDENING_SPEC.md, PTC_SCOPE_LOCK_SPEC.md

5. **[HEALER_RETRY_HARDENING_SPEC.md](./HEALER_RETRY_HARDENING_SPEC.md)**
   - Governs: L2 Execution Layer (Healer Retry Logic, Semantic Diff Scoring, Scope Lock)
   - Defines healer retry hardening with strictness escalation and scope enforcement
   - **Cross-references:** REPLAY_DETERMINISM_RULES.md, LATENCY_BUDGET_SLA_SPEC.md

6. **[L6_DRIFT_SAFEGUARDS_SPEC.md](./L6_DRIFT_SAFEGUARDS_SPEC.md)**
   - Governs: L6 Observability Layer (Anomaly Detection, Drift Safeguards, Threshold Mutation Control)
   - Defines L6 drift safeguards with anomaly confidence delta caps and distribution shift detection
   - **Cross-references:** DEGRADATION_MATRIX.md, POLICY_EPOCH_SPEC.md

### Cross-Cutting Specifications

7. **[UWG_ISOLATION_SPEC.md](./UWG_ISOLATION_SPEC.md)**
   - Governs: UWG (Universal Write Gateway) (Independent Daemon, Mutation Control, Trace Validation)
   - Defines UWG isolation as independent host-level daemon with strict mutation controls
   - Defines UUIDv7 trace_id monotonicity validation
   - **Cross-references:** L0_DECOMPOSITION_SPEC.md, AUTHORITY_HIERARCHY_INVARIANTS.md, LATENCY_BUDGET_SLA_SPEC.md

8. **[PTC_SCOPE_LOCK_SPEC.md](./PTC_SCOPE_LOCK_SPEC.md)**
   - Governs: L2 Execution Layer (Prompt-Tool Contract, Tool Invocation Control)
   - Defines static tool contract enforcement with no dynamic registration or side-channel invocations
   - **Cross-references:** REPLAY_DETERMINISM_RULES.md

9. **[POLICY_EPOCH_SPEC.md](./POLICY_EPOCH_SPEC.md)**
   - Governs: Meta-Learning Bus (Policy Epoch Management, Threshold Configuration, Shadow Evaluation)
   - Defines meta-learning constraints with staged threshold updates and human approval gates
   - **Cross-references:** L6_DRIFT_SAFEGUARDS_SPEC.md, AUTHORITY_HIERARCHY_INVARIANTS.md

10. **[LATENCY_BUDGET_SLA_SPEC.md](./LATENCY_BUDGET_SLA_SPEC.md)**
    - Governs: All Layers (L0, L1, L2, L5, L6, UWG - Latency Enforcement, Timeout Behavior)
    - Defines per-layer SLA latency budgets with explicit abort/escalate behavior
    - **Cross-references:** DEGRADATION_MATRIX.md, L0_DECOMPOSITION_SPEC.md, UWG_ISOLATION_SPEC.md

## Key Invariants

### Authority Hierarchy
- L1 proposes
- L0 authorizes
- L5 blocks
- L2 executes
- UWG mutates
- L4 records
- L6 observes (never blocks)
- Meta-learning optimizes (never executes or authorizes)

### Trace ID Monotonicity
- **Format:** UUIDv7 (RFC 9562)
- **Enforced at:** L0a ingress, UWG validation
- **Comparison:** Timestamp-based (first 48 bits)
- **Collision Detection:** Exact UUID match
- **Gap Detection:** Timestamp difference > 1000ms

### Timeout Enforcement
- **Portable Pattern:** Monotonic timing + cooperative cancellation (intra-process)
- **Hard Timeout:** Separate process/subprocess with timeout parameter
- **No SIGALRM:** All specs use portable timeout patterns

### L6 Non-Blocking Invariant
- L6 failures → continue degraded + log/buffer
- L6 never aborts or escalates
- L0 makes routing decisions based on L6 signals

## Consistency Requirements

All specifications must maintain:
1. **SCOPE section** at the top declaring governed layers
2. **Authority alignment** with AUTHORITY_HIERARCHY_INVARIANTS.md
3. **Degradation behavior** consistent with DEGRADATION_MATRIX.md
4. **Trace ID format** consistent with L0_DECOMPOSITION_SPEC.md and UWG_ISOLATION_SPEC.md
5. **Timeout patterns** using portable monotonic timing (no SIGALRM)

## Verification

Run consistency check:
```bash
python docs/tools/check_spec_consistency.py
```

This script verifies:
- Required SCOPE headers exist in each spec
- L6 spec contains no "abort/escalate/block" verbs
- trace_id format string is identical across L0 and UWG specs
