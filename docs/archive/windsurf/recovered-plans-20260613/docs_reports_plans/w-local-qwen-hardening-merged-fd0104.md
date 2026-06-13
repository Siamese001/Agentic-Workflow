# W-LOCAL-QWEN HARDENING AUGMENTATION - Phase 10 Sovereign Clean

This plan hardens the Qwen v2.5 local vLLM installation to operate strictly as a Healing Tier provider under Phase 10 architecture, incorporating comprehensive determinism enforcement and sovereignty compliance based on critical feedback.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## SECTION 1 — STRICT ROLE DECLARATION

### Architectural Classification
- **Qwen v2.5 (via vLLM)**: Classified as `HealingTier.QWEN_VLLM`
- **Invocation Path**: ONLY through `HealingProviderInvoker.invoke_qwen_vllm()`
- **Selection Method**: ONLY via `route_healing_tier()` in `healing_tier_router.py`
- **Escalation Path**: LOCAL_AGENT → QWEN_VLLM → GEMINI_2_5_PRO

### Prohibited Access Patterns
1. **Direct model calls to Qwen**: FORBIDDEN - must route through healing tier
2. **Direct vLLM imports**: FORBIDDEN outside `tools/vllm_boundary_client.py` and `HealingProviderInvoker`
3. **Qwen logic in L0 routing**: FORBIDDEN - L0 must remain model-agnostic
4. **Qwen logic in L4 state**: FORBIDDEN - state must remain provider-agnostic
5. **Qwen logic in embedding factory**: FORBIDDEN - embeddings remain OpenAI-only
6. **Qwen logic in meta-learning proposer**: FORBIDDEN - proposals must remain model-agnostic

## SECTION 2 — KILL SWITCH IMPLEMENTATION

### Environment Variable
```bash
QWEN_VLLM_ENABLED=true  # Default: enabled
```

### Kill Switch Behavior
- **FALSE**: `route_healing_tier()` skips QWEN_VLLM tier entirely
- **Escalation Path**: LOCAL_AGENT → GEMINI_2_5_PRO (direct escalation)
- **Fail-Closed**: System continues operating without Qwen tier

### Startup Validation Enforcement
```python
def validate_qwen_startup_state() -> None:
    """Hard validate kill switch at startup."""
    if not QWEN_VLLM_ENABLED:
        assert vllm_process_manager.is_running() is False, \
            "QWEN_VLLM_ENABLED=False but vLLM process detected"
        logger.info("QWEN_VLLM_ENABLED=False - Qwen tier disabled at startup")
```

## SECTION 3 — DETERMINISM ENFORCEMENT (HARDENED)

### Pinned Revisions with Runtime Substrate
```python
# In healing_tier_config.py
QWEN_MODEL_REVISION_SHA = "a1b2c3d4e5f6..."  # Pin exact model commit
QWEN_TOKENIZER_REVISION_SHA = "f6e5d4c3b2a1..."  # Pin exact tokenizer commit
QWEN_VLLM_VERSION = "0.4.2"  # Pin vLLM version
QWEN_CUDA_VERSION = "12.1"  # Pin CUDA version
QWEN_TORCH_VERSION = "2.1.0"  # Pin PyTorch version
```

### Full Determinism Digest (No Truncation)
```python
def compute_qwen_determinism_digest(
    model_id: str,
    model_revision: str,
    tokenizer_revision: str,
    inference_params: dict,
    vllm_version: str,
    cuda_version: str,
    torch_version: str
) -> str:
    """Compute W-QWEN-DETERMINISM-DIGEST with full SHA-256."""
    payload = {
        "model_id": model_id,
        "model_revision": model_revision,
        "tokenizer_revision": tokenizer_revision,
        "inference_params": inference_params,
        "vllm_version": vllm_version,
        "cuda_version": cuda_version,
        "torch_version": torch_version
    }
    # Canonical JSON encoding
    canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()  # Full 64 chars
```

### Output Canonicalization
```python
def canonicalize_output(output: str) -> str:
    """Enforce output canonicalization for replay consistency."""
    # Normalize whitespace and encoding
    normalized = output.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()

def compute_output_hash(output: str) -> str:
    """Compute deterministic output hash."""
    return canonicalize_output(output)
```

### Inference Parameter Locking
```python
QWEN_DETERMINISTIC_PARAMS = {
    "temperature": 0.0,      # Fixed temperature
    "top_p": 1.0,           # Fixed top_p
    "max_tokens": 2048,     # Fixed max_tokens
    "seed": 42,             # Fixed seed for reproducibility
}
```

## SECTION 4 — GPU HARD FAIL VALIDATION (FAIL-FAST)

### Pre-Load Validation Order
```python
def validate_gpu_capabilities(model_size: str) -> None:
    """Hard fail on GPU capability mismatch BEFORE model load."""
    # 1. VRAM threshold validation
    # 2. CUDA version validation
    # 3. Compute capability validation
    # 4. Driver version validation
    # FAIL FAST - abort before any memory allocation

def start_qwen_safely() -> None:
    """Enforce validation order: validate BEFORE start."""
    validate_gpu_capabilities(model_size="7B")  # Fail fast
    start_vllm_server()  # Only if validation passes
```

### Model-Specific Requirements
- **Qwen2.5-7B**: Minimum 16GB VRAM, CUDA 11.8+
- **Qwen2.5-14B**: Minimum 32GB VRAM, CUDA 12.0+
- **Compute Capability**: Minimum 7.0 (Turing架构)

## SECTION 5 — PROCESS ISOLATION

### vLLM Process Requirements
- **Separate Process**: vLLM runs in isolated process
- **Boundary Client Access**: Only via `tools/vllm_boundary_client.py`
- **Memory Isolation**: No shared memory with embedding factory
- **State Immutability**: No system state mutation

### Circuit Breaker with Deterministic Thresholds
```python
class QwenCircuitBreaker:
    """Deterministic circuit breaker for Qwen tier."""

    def __init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False
        self.circuit_open_time = None

    def record_failure(self) -> bool:
        """Record failure and check circuit breaker rules."""
        now = time.time()

        # Reset if outside window
        if self.last_failure_time and (now - self.last_failure_time) > 60:
            self.failure_count = 0

        self.failure_count += 1
        self.last_failure_time = now

        # 3 consecutive failures within 60 seconds → disable for 
        if self.failure_count >= 3:
            self.circuit_open = True
            self.circuit_open_time = now
            logger.warning("Qwen circuit breaker OPEN - disabling for ")
            return True

        return False

    def is_circuit_open(self) -> bool:
        """Check if circuit is currently open."""
        if not self.circuit_open:
            return False

        # Auto-close after 
        if time.time() - self.circuit_open_time > 300:
            self.circuit_open = False
            self.failure_count = 0
            logger.info("Qwen circuit breaker CLOSED - re-enabling tier")
            return False

        return True
```

## SECTION 6 — AUDIT REQUIREMENTS (UNIFIED RECORD)

### Enhanced InvocationRecord (No Subclassing)
```python
@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record of a single provider invocation."""
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    # Optional provider metadata (prevents type branching)
    provider_metadata: dict[str, Any] | None = None
```

### Required Qwen Metadata
```python
qwen_metadata = {
    "revision_sha": QWEN_MODEL_REVISION_SHA,
    "determinism_digest": determinism_digest,
    "output_hash": output_hash,
    "latency_ms": latency_ms,
    "memory_used_mb": memory_used_mb,
    "gpu_utilization": gpu_utilization,
    "vllm_version": QWEN_VLLM_VERSION,
    "cuda_version": QWEN_CUDA_VERSION,
    "circuit_open": circuit_breaker.is_circuit_open()
}
```

## SECTION 7 — TIER CHOKE ENFORCEMENT (ENUM GUARD)

### CI Enforcement Rules
Fail build if `HealingTier.QWEN_VLLM` appears outside:
- `healing_tier_router.py`
- `HealingProviderInvoker` implementations
- Test mock files (explicitly allowed)

### Enforcement Script
```bash
# ops_scripts/ci/audit_healing_enum_leakage.py
def check_enum_leakage():
    """Prevent direct enum usage outside choke points."""
    forbidden_files = find_python_files(exclude=[
        "healing_tier_router.py",
        "healing_provider_adapters.py",
        "test_*.py"
    ])

    for file in forbidden_files:
        if "HealingTier.QWEN_VLLM" in file_content:
            raise BuildError(f"Enum leakage detected in {file}")
```

## SECTION 8 — OOM ESCALATION WITH RETRY BOUNDS

### Explicit Retry Rules
```python
def handle_oom_with_escalation(retry_count: int) -> HealingDecision:
    """Handle OOM with explicit retry bounds."""
    if retry_count >= 3:
        # Force escalation to GEMINI tier per Phase 10 invariant
        return HealingDecision(
            heal_confidence=0.0,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=("oom_retry_exhausted", "forced_gemini_escalation")
        )

    # Increment retry and attempt local recovery
    raise OOMRecoverableError(f"OOM attempt {retry_count + 1}/3")
```

## SECTION 9 — EMBEDDING GOVERNANCE LOCK

### Explicit Constraints (UNCHANGED)
1. **EmbeddingServiceFactory**: Remains unchanged - OpenAI-only
2. **OpenAI text-embedding-3-large**: Remains sole production embedding provider
3. **Local Embedding Providers**: FORBIDDEN - no vLLM embedding integration
4. **Replay Key Construction**: No changes - existing keys preserved
5. **Seed Pack Modifications**: No changes - existing packs preserved
6. **BLAS Configuration**: No changes - existing optimization preserved
7. **Embedding Results**: Remain C0 informational only

## SECTION 10 — META-LEARNING PROTECTION

### Threshold Lock Invariant
```python
# FIXED THRESHOLDS - CANNOT BE MODIFIED BY QWEN METRICS
HEALING_CONFIDENCE_X = 0.75  # Immutable
HEALING_CONFIDENCE_Y = 0.40  # Immutable

def update_healer_confidence_prior(error_signature: str, qwen_success: bool) -> None:
    """Qwen may update confidence priors but NOT threshold values."""
    # Allowed: Update historical success rates
    # FORBIDDEN: Modify HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y
    pass
```

### CI Guard for Threshold Protection
```python
def validate_threshold_immutability():
    """Ensure thresholds cannot be modified by meta-learning."""
    assert HEALING_CONFIDENCE_X == 0.75, "X threshold modified"
    assert HEALING_CONFIDENCE_Y == 0.40, "Y threshold modified"
```

## SECTION 11 — HEALTH CHECK WITH DETERMINISM

### Enhanced Health Endpoint
```json
{
  "status": "healthy",
  "model_id": "Qwen/Qwen2.5-7B-Instruct",
  "model_revision": "a1b2c3d4e5f6...",
  "determinism_digest": "sha256_full_hash_here",
  "cuda_version": "12.1",
  "vllm_version": "0.4.2",
  "torch_version": "2.1.0",
  "circuit_open": false,
  "last_failure": null
}
```

## SECTION 12 — REPLAY VALIDATION TESTS

### Determinism Test Case
```python
def test_qwen_replay_determinism():
    """Verify exact replay consistency across invocations."""
    # Setup identical healing input
    healing_input = create_test_healing_input()

    # Invoke Qwen twice with identical parameters
    record1 = invoke_qwen_deterministic(healing_input)
    record2 = invoke_qwen_deterministic(healing_input)

    # Compare all determinism artifacts
    assert record1.provider_metadata["determinism_digest"] == \
           record2.provider_metadata["determinism_digest"]

    assert record1.provider_metadata["output_hash"] == \
           record2.provider_metadata["output_hash"]

    # Compare canonical JSON serialization
    json1 = json.dumps(asdict(record1), separators=(",", ":"), sort_keys=True)
    json2 = json.dumps(asdict(record2), separators=(",", ":"), sort_keys=True)
    assert json1 == json2, "InvocationRecord JSON mismatch"
```

## SECTION 13 — CI ENFORCEMENT SUITE

### Comprehensive CI Rules
1. **Import Boundary Enforcement**: vLLM imports only in allowed files
2. **Enum Leakage Prevention**: HealingTier.QWEN_VLLM only in choke points
3. **Embedding Governance Lock**: No Qwen references in embedding factory
4. **Threshold Immutability**: X=0.75, Y=0.40 cannot be modified
5. **Determinism Completeness**: Full SHA-256, no truncation
6. **Output Canonicalization**: Output hashes required for all invocations

## IMPLEMENTATION PHASES

### Phase 1: Determinism Infrastructure
1. Implement full SHA-256 determinism digest
2. Add runtime substrate to payload
3. Create output canonicalization
4. Add replay validation tests

### Phase 2: Sovereignty Hardening
1. Add enum leakage CI guards
2. Implement startup kill switch validation
3. Create threshold immutability guards
4. Add circuit breaker with deterministic rules

### Phase 3: Process Isolation & Validation
1. Implement fail-fast GPU validation
2. Add OOM escalation with retry bounds
3. Create enhanced health endpoint
4. Add comprehensive audit metadata

### Phase 4: Integration & Testing
1. Unified InvocationRecord implementation
2. End-to-end replay validation
3. CI enforcement suite
4. Meta-learning protection validation

## HARDENING SUMMARY

This plan incorporates all critical feedback to achieve Phase 10 sovereign compliance:

**Determinism Strengthening:**
- Full SHA-256 digests (no truncation)
- Runtime substrate inclusion
- Output canonicalization with hashing
- Comprehensive replay validation

**Sovereignty Enforcement:**
- Enum leakage prevention
- Startup kill switch validation
- Threshold immutability protection
- Process isolation with circuit breaker

**Audit & Monitoring:**
- Unified InvocationRecord design
- Comprehensive metadata collection
- Health check with determinism visibility
- CI enforcement across all boundaries

The hardened plan ensures Qwen operates as a fully sovereign healing tier provider with zero impact on embedding governance or architectural invariants.

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

