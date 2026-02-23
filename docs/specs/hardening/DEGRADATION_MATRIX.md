# Layer Degradation Contract

## SCOPE
Governs: **All Layers** (L0, L1, L2, L4, L5, L6, UWG, Meta-Learning Bus, FAISS, Redis, vLLM, Circuit Breaker, Tracing)

Defines fail-closed degradation behavior for all subsystems in execute_ssot unified architecture.

---

Fail-closed semantics for all subsystem failures in execute_ssot unified architecture.

---

## L6 Observability Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L6 anomaly signal unavailable | Continue execution, log degradation, signal L0 to disable ML routing | L6 observes only - cannot block execution, signals L0 for routing decision |
| L6 metrics collection timeout | Continue execution, buffer metrics locally, log degradation | Observability loss acceptable, execution must proceed |
| L6 trace emission failure | Continue execution, buffer traces locally, log degradation | L6 failure never blocks execution - buffer for async retry |
| L6 dashboard unavailable | Continue execution, buffer metrics locally, log degradation | Display layer failure does not block execution |

**Invariant:** L6 never aborts or escalates. L6 failures → continue degraded + log/buffer. L0 makes routing decisions based on L6 signals.

---

## L5 Safety Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L5 timeout > SLA (500ms) | Hard reject execution, no soft pass-through | Safety cannot be bypassed under time pressure |
| L5 validation agent crash | Abort healing session, escalate to Path D | Safety agent failure = unsafe to proceed |
| L5 policy read failure | Escalate to Path D (human intervention) | Cannot execute without safety policy |
| L5 circuit breaker open | Block all healing operations, enter safe mode | Repeated safety failures require manual reset |

**Invariant:** L5 timeout or failure = hard abort. No execution without safety clearance.

---

## L4 State Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L4 policy read fails | Escalate to Path D (human approval required) | Cannot determine authority without policy |
| L4 Redis unavailable | Degrade to in-memory state, warn on restart | Temporary state loss acceptable |
| L4 FAISS unavailable | Disable meta-learning, continue deterministic | Learning loss acceptable, execution proceeds |
| L4 state corruption detected | Abort session, restore from last snapshot | Corrupted state = unsafe to continue |

**Invariant:** Policy read failure = Path D escalation. No autonomous execution without policy.

---

## L2 Execution Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L2 execution lease timeout | Abort operation, release resources | Runaway execution must be terminated |
| L2 sandbox escape detected | Kill process, escalate to L5 | Security breach = immediate termination |
| L2 determinism violation | Abort replay, flag non-deterministic code | Replay integrity compromised |
| L2 resource limit exceeded | Graceful shutdown, log resource exhaustion | Prevent OOM/system instability |

**Invariant:** Execution lease timeout = hard abort. No infinite execution loops.

---

## L1 Cognition Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L1 confidence below threshold | Route to L0 for deterministic fallback | Low confidence = unsafe for autonomous action |
| L1 LLM API unavailable | Disable ML routing, force deterministic path | Cannot make ML decisions without LLM |
| L1 prompt injection detected | Reject input, escalate to L5 | Security threat = immediate rejection |
| L1 hallucination detected | Abort operation, log hallucination event | Cannot trust hallucinated output |

**Invariant:** LLM unavailable = deterministic routing only. No ML without LLM.

---

## L0 Routing Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| L0a HMAC verification fails | Abort run, no retry | Cryptographic failure = security breach |
| L0b routing table corrupted | Force Path A (safest deterministic path) | Cannot trust corrupted routing logic |
| L0c dispatch sealing fails | Abort operation, escalate to L5 | Cannot execute without sealed dispatch |
| L0 budget exhausted | Hard reject new operations | Budget enforcement is non-negotiable |

**Invariant:** HMAC failure = immediate abort. No execution without cryptographic integrity.

---

## UWG (Universal Write Gateway) Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| UWG HMAC verification fails | Abort run, no retry | Write integrity compromised |
| UWG policy hash mismatch | Reject write, escalate to L5 | Stale policy = unsafe to mutate |
| UWG trace_id non-monotonic | Abort session, flag replay attack | Trace ordering violation = security threat |
| UWG daemon unavailable | Block all mutations, enter read-only mode | No writes without UWG |

**Invariant:** No mutation without signed ExecutionTrace. UWG failure = read-only mode.

---

## Meta-Learning Bus Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| Meta-learning write fails | Log failure, continue execution | Learning loss acceptable, execution proceeds |
| Threshold update rejected | Revert to previous epoch, log rejection | Safety thresholds require approval |
| Shadow evaluation fails | Abort threshold activation, maintain current | Cannot activate untested thresholds |
| Policy epoch mismatch | Reject meta-learning write, escalate | Epoch integrity mandatory |

**Invariant:** Threshold updates require shadow evaluation pass. No live mutation without testing.

---

## FAISS Vector Store Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| FAISS index corrupted | Rebuild from backup, enter degraded mode | Corrupted index = unreliable patterns |
| FAISS GPU unavailable | Fallback to CPU search, log degradation | GPU loss acceptable, slower search |
| FAISS write fails | Log failure, continue without pattern storage | Learning loss acceptable |
| FAISS search timeout | Return empty results, continue deterministic | Search timeout = no pattern boost |

**Invariant:** FAISS failure = deterministic execution. No blocking on vector search.

---

## Redis Cache Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| Redis unavailable | Degrade to in-memory cache, warn on restart | Cache loss acceptable, slower execution |
| Redis eviction detected | Rebuild cache on-demand, log eviction | Eviction expected, rebuild as needed |
| Redis connection timeout | Retry with exponential backoff, max 3 attempts | Transient network issues tolerated |
| Redis corruption detected | Flush cache, restart clean | Corrupted cache = unreliable data |

**Invariant:** Redis failure = in-memory fallback. No blocking on cache operations.

---

## vLLM (Qwen) Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| vLLM GPU OOM | Reduce batch size, retry with smaller batches | GPU memory exhaustion = reduce load |
| vLLM inference timeout | Abort operation, escalate to deterministic | Inference timeout = unsafe to wait |
| vLLM model load fails | Disable vLLM, force external API fallback | Model failure = use backup LLM |
| vLLM quality degradation | Switch to external API, log degradation | Quality loss = use higher quality model |

**Invariant:** vLLM failure = external API fallback or deterministic routing. No blocking on local LLM.

---

## Circuit Breaker Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| Circuit breaker open | Block operation, return cached result or error | Repeated failures = stop trying |
| Circuit breaker stuck open | Manual reset required, escalate to ops | Stuck circuit = operational issue |
| Circuit breaker half-open test fails | Return to open state, extend timeout | Test failure = not yet recovered |
| Circuit breaker threshold exceeded | Open circuit, log threshold breach | Failure rate too high = stop |

**Invariant:** Circuit open = hard block. No retry until circuit closes.

---

## Tracing Degradation

| Failure Condition | Behavior | Rationale |
|-------------------|----------|-----------|
| Trace emission fails | Buffer traces locally, retry async | Trace loss unacceptable, buffer required |
| Trace storage full | Rotate oldest traces, log rotation | Storage full = make space |
| Trace corruption detected | Abort trace, start new trace chain | Corrupted trace = unreliable audit |
| Trace ID collision | Generate new ID, log collision | Collision = integrity violation |

**Invariant:** Trace emission failure = local buffering. No trace loss allowed.

---

## Escalation Paths

### Path A: Deterministic Execution
- No ML routing
- No LLM calls
- Rule-based decisions only
- Maximum safety, minimum capability

### Path B: Degraded ML Execution
- ML routing with reduced confidence
- Cached LLM responses only
- No new pattern learning
- Reduced capability, maintained safety

### Path C: Safe Mode
- Read-only operations only
- No mutations allowed
- Observability only
- Zero risk, zero execution

### Path D: Human Intervention Required
- Abort all autonomous operations
- Escalate to human operator
- Await manual approval
- Maximum safety, zero autonomy

---

## Degradation Decision Matrix

| Subsystem Failure | Path A | Path B | Path C | Path D |
|-------------------|--------|--------|--------|--------|
| L6 unavailable | ✓ | | | |
| L5 timeout | | | | ✓ |
| L4 policy fail | | | | ✓ |
| L2 timeout | ✓ | | | |
| L1 LLM fail | ✓ | | | |
| L0 HMAC fail | | | | ✓ |
| UWG unavailable | | | ✓ | |
| FAISS fail | ✓ | | | |
| Redis fail | | ✓ | | |
| vLLM fail | ✓ | | | |
| Circuit open | | ✓ | | |

---

## Monitoring Requirements

All degradation events must emit:
- Timestamp
- Subsystem identifier
- Failure condition
- Chosen degradation path
- Impact assessment
- Recovery action

Degradation events trigger:
- L6 anomaly detection
- L5 safety review
- L4 state snapshot
- Ops team notification (for Path D)

---

## Recovery Procedures

### Automatic Recovery
- Circuit breaker timeout expiry
- Redis reconnection
- FAISS index rebuild
- Cache warming

### Manual Recovery
- L5 safety policy update
- L4 policy restoration
- UWG daemon restart
- Path D escalation resolution

---

## Invariant Enforcement

All degradation paths must satisfy:
1. **Safety First:** Never compromise safety for availability
2. **Fail Closed:** Default to most restrictive path on ambiguity
3. **Audit Trail:** All degradation events logged and traceable
4. **Deterministic Fallback:** Always have deterministic path available
5. **No Silent Failures:** All failures must be observable and actionable

**Violation of any invariant = immediate Path D escalation.**
