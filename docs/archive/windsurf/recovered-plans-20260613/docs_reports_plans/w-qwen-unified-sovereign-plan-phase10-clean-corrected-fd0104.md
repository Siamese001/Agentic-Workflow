# W-LOCAL-QWEN UNIFIED SOVEREIGN PLAN (PHASE 10 CLEAN — CORRECTED)

This unified plan provides the authoritative Phase 10 sovereign-compliant specification for integrating Qwen v2.5 via local vLLM strictly as HealingTier.QWEN_VLLM with complete determinism enforcement and architectural boundary protection.

======================================================================
MANDATORY SOVEREIGN INVARIANTS
======================================================================

1. Qwen is HealingTier.QWEN_VLLM only.
2. Selected only through route_healing_tier().
3. Invoked only via HealingProviderInvoker.
4. No direct model calls anywhere else.
5. No embedding architecture changes.
6. OpenAI text-embedding-3-large remains sole embedding provider.
7. Embeddings remain C0 informational only.
8. Thresholds X=0.75 and Y=0.40 are immutable.
9. No upward mutation into L0 or L4.
10. proposal_only=True remains default for meta-learning.

======================================================================
SECTION A — DETERMINISM (STRICT)
======================================================================

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


### Full SHA-256 Digest Specification
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
    # Canonical JSON encoding - sorted keys, no whitespace drift
    canonical_payload = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()  # Full 64 chars
```

### Output Canonicalization Specification
```python
import unicodedata

def canonicalize_qwen_output(output: str) -> str:
    """Enforce Unicode and whitespace canonicalization for replay consistency."""
    # 1. Normalize Unicode to NFC
    normalized = unicodedata.normalize("NFC", output)
    # 2. Normalize newlines to "\n"
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    # 3. Strip trailing whitespace
    normalized = normalized.rstrip()
    # 4. Encode UTF-8 and hash
    encoded = normalized.encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
```

### InvocationRecord Enhancement
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
    provider_metadata: dict[str, Any] | None = None

# Required Qwen metadata fields
QWEN_METADATA_FIELDS = {
    "determinism_digest": str,      # Full SHA-256
    "output_hash": str,             # Canonicalized output hash
    "revision_sha": str,
    "latency_ms": int,
    "memory_used_mb": int,
    "gpu_utilization": float,
    "vllm_version": str,
    "cuda_version": str,
    "torch_version": str
}

# Circuit breaker state is operational metadata and MUST NOT be included in determinism_digest
# Circuit breaker state MUST NOT affect replay validation equality
```

### Replay Validation Test Specification
```python
def test_qwen_replay_determinism():
    """Verify exact replay consistency across invocations."""
    healing_input = create_deterministic_healing_input()

    # Invoke Qwen twice with identical parameters
    record1 = invoke_qwen_via_healing_tier(healing_input)
    record2 = invoke_qwen_via_healing_tier(healing_input)

    # Verify determinism digest matches
    digest1 = record1.provider_metadata["determinism_digest"]
    digest2 = record2.provider_metadata["determinism_digest"]
    assert digest1 == digest2, f"Determinism drift: {digest1} != {digest2}"

    # Verify output hash matches
    output1 = record1.provider_metadata["output_hash"]
    output2 = record2.provider_metadata["output_hash"]
    assert output1 == output2, f"Output drift: {output1} != {output2}"

    # Verify canonical JSON serialization matches
    json1 = json.dumps(asdict(record1), separators=(",", ":"), sort_keys=True)
    json2 = json.dumps(asdict(record2), separators=(",", ":"), sort_keys=True)
    assert json1 == json2, "InvocationRecord JSON mismatch"
```

======================================================================
SECTION B — CIRCUIT BREAKER REPLAY SAFETY
======================================================================

### Deterministic Circuit Breaker Specification
```python
class QwenCircuitBreaker:
    """Deterministic circuit breaker with replay safety."""

    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.failure_count = 0
        self.failure_timestamps: list[int] = []
        self.circuit_open = False
        self.circuit_open_timestamp: int | None = None

    def record_failure(self, timestamp: int | None = None) -> bool:
        """Record failure with deterministic replay behavior."""
        if self.replay_mode:
            # In replay mode, circuit breaker state transitions are disabled
            return False

        now = timestamp or int(time.time())

        # Clean old failures outside 60-second window
        self.failure_timestamps = [t for t in self.failure_timestamps if now - t <= 60]
        self.failure_timestamps.append(now)
        self.failure_count = len(self.failure_timestamps)

        # 3 consecutive failures within 60 seconds → disable for 
        if self.failure_count >= 3:
            self.circuit_open = True
            self.circuit_open_timestamp = now
            logger.warning("Qwen circuit breaker OPEN - disabling for ")
            return True

        return False

    def is_circuit_open(self, timestamp: int | None = None) -> bool:
        """Check circuit state with deterministic replay behavior."""
        if self.replay_mode:
            return False  # Always closed in replay mode

        if not self.circuit_open:
            return False

        now = timestamp or int(time.time())

        # Auto-close after 
        if now - self.circuit_open_timestamp > 300:
            self.circuit_open = False
            self.failure_count = 0
            self.failure_timestamps.clear()
            logger.info("Qwen circuit breaker CLOSED - re-enabling tier")
            return False

        return True
```

======================================================================
SECTION C — GPU VALIDATION (FAIL-FAST)
======================================================================

### GPU Capability Exception
```python
class QwenGPUCapabilityError(RuntimeError):
    """Raised when GPU capabilities are insufficient for Qwen model."""

    def __init__(self, requirement: str, current: str, model: str):
        self.requirement = requirement
        self.current = current
        self.model = model
        super().__init__(
            f"QwenGPUCapabilityError: {model} requires {requirement}, "
            f"but system has {current}"
        )
```

### Fail-Fast Validation Order
```python
def validate_qwen_gpu_capabilities(model_size: str) -> None:
    """Hard fail on GPU capability mismatch BEFORE model load."""
    # 1. VRAM threshold validation
    required_vram = {"7B": 16, "14B": 32}[model_size]
    available_vram = get_gpu_memory_gb()
    if available_vram < required_vram:
        raise QwenGPUCapabilityError(
            f"VRAM >= {required_vram}GB", f"{available_vram}GB", f"Qwen2.5-{model_size}"
        )

    # 2. CUDA version validation
    min_cuda = "11.8" if model_size == "7B" else "12.0"
    current_cuda = get_cuda_version()
    if version_parse(current_cuda) < version_parse(min_cuda):
        raise QwenGPUCapabilityError(
            f"CUDA >= {min_cuda}", current_cuda, f"Qwen2.5-{model_size}"
        )

    # 3. Compute capability validation
    min_compute = 7.0
    current_compute = get_compute_capability()
    if current_compute < min_compute:
        raise QwenGPUCapabilityError(
            f"Compute >= {min_compute}", str(current_compute), f"Qwen2.5-{model_size}"
        )

    # 4. Driver version validation
    min_driver = "525.60.13"
    current_driver = get_nvidia_driver_version()
    if version_parse(current_driver) < version_parse(min_driver):
        raise QwenGPUCapabilityError(
            f"Driver >= {min_driver}", current_driver, f"Qwen2.5-{model_size}"
        )

def start_qwen_server_safely(model_size: str) -> None:
    """Enforce validation order: validate BEFORE start."""
    validate_qwen_gpu_capabilities(model_size)  # Fail fast
    start_vllm_server(model_config=get_model_config(model_size))  # Only if validation passes
```

======================================================================
SECTION D — OOM ESCALATION (CHOKE POINT ENFORCED)
======================================================================

### OOM Handling with Router Choke Point
```python
def handle_qwen_oom_via_router(
    healing_input: HealingInput,
    config: HealingTierConfig
) -> HealingDecision:
    """Handle OOM by routing through single choke point."""
    # Increment retry count
    new_retry_count = healing_input.retry_count + 1

    # Create FailureSignal for L2.3 consumption
    failure_signal = FailureSignal(
        source_agent=healing_input.agent_id,
        failure_type="gpu_oom",
        error_signature="qwen_gpu_oom",
        trace_id=healing_input.trace_id,
        context={"retry_count": new_retry_count, "error": "GPU out of memory"},
        retry_count=new_retry_count,
        blast_radius_estimate=0.1
    )

    # Convert to HealingInput and route through choke point
    escalated_input = failure_signal.to_healing_input(
        required_tools=healing_input.required_tools,
        violation_metadata_refs=healing_input.violation_metadata_refs
    )

    # Return router decision directly (no exceptions, no manual tier selection)
    return route_healing_tier(escalated_input, config)

def invoke_qwen_with_oom_protection(
    healing_input: HealingInput,
    decision: HealingDecision,
    config: HealingTierConfig
) -> InvocationRecord:
    """Invoke Qwen with OOM protection and proper escalation."""
    try:
        return qwen_adapter.invoke_qwen_vllm(healing_input, decision, config)
    except RuntimeError as exc:
        if "out of memory" in str(exc).lower():
            # Route through choke point - router handles retry_count >= 3 -> GEMINI escalation
            escalated_decision = handle_qwen_oom_via_router(healing_input, config)
            # Retry with escalated tier
            return dispatch_healing(
                healing_input,
                config,
                agent_name=healing_input.agent_id
            )[1]  # Return InvocationRecord from escalated call
        raise
```

======================================================================
SECTION E — ENUM LEAKAGE ENFORCEMENT
======================================================================

### CI Enforcement Script
```python
# ops_scripts/ci/audit_healing_enum_leakage.py
import ast
import sys
from pathlib import Path

ALLOWED_FILES = {
    "healing_tier_router.py",
    "healing_provider_adapters.py",
    "healing_tier_dispatcher.py",
    "healing_tier_types.py"
}

ALLOWED_TEST_PATTERNS = {
    "test_*.py",
    "*_test.py",
    "conftest.py"
}

def check_enum_leakage() -> None:
    """Prevent direct enum usage outside choke points."""
    violations = []

    for py_file in Path(".").rglob("*.py"):
        if any(py_file.name.startswith(pattern.rstrip("*")) for pattern in ALLOWED_TEST_PATTERNS):
            continue  # Skip test files

        if py_file.name in ALLOWED_FILES:
            continue  # Skip allowed implementation files

        try:
            content = py_file.read_text(encoding="utf-8")
            if "HealingTier.QWEN_VLLM" in content:
                violations.append(str(py_file))
        except (UnicodeDecodeError, OSError):
            continue

    if violations:
        print("ERROR: HealingTier.QWEN_VLLM enum leakage detected:")
        for file in violations:
            print(f"  - {file}")
        print("\nEnum usage only allowed in:", sorted(ALLOWED_FILES))
        sys.exit(1)

    print("OK: No enum leakage detected")

if __name__ == "__main__":
    check_enum_leakage()
```

### GitHub Workflow Integration
```yaml
# .github/workflows/qwen-enum-leakage.yml
- name: Check Qwen Enum Leakage
  run: |
    python ops_scripts/ci/audit_healing_enum_leakage.py
```

======================================================================
SECTION F — KILL SWITCH HARD VALIDATION
======================================================================

### Environment Variable Definition
```bash
# Required environment variable
QWEN_VLLM_ENABLED=true  # Default: enabled
```

### Startup Validation Implementation
```python
import psutil

def validate_qwen_startup_state() -> None:
    """Hard validate kill switch at startup."""
    qwen_enabled = os.environ.get("QWEN_VLLM_ENABLED", "true").lower() == "true"

    if not qwen_enabled:
        # Assert no Qwen processes are running (cross-platform)
        if is_vllm_process_running():
            raise RuntimeError(
                "QWEN_VLLM_ENABLED=False but vLLM process detected. "
                "Terminate all vLLM processes before starting."
            )

        logger.info("QWEN_VLLM_ENABLED=False - Qwen tier disabled at startup")
        return

    # If enabled, validate GPU capabilities before allowing startup
    try:
        validate_qwen_gpu_capabilities(model_size="7B")  # Default to 7B for validation
        logger.info("QWEN_VLLM_ENABLED=True - GPU validation passed")
    except QwenGPUCapabilityError as exc:
        logger.error(f"QWEN_VLLM_ENABLED=True but GPU validation failed: {exc}")
        raise

def is_vllm_process_running() -> bool:
    """Cross-platform detection of vLLM processes using psutil."""
    try:
        for proc in psutil.process_iter(attrs=["cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "vllm" in " ".join(cmdline):
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
```

### Router Integration
```python
def route_healing_tier_with_kill_switch(
    healing_input: HealingInput,
    config: HealingTierConfig
) -> HealingDecision:
    """Route healing with kill switch enforcement."""
    qwen_enabled = os.environ.get("QWEN_VLLM_ENABLED", "true").lower() == "true"

    if not qwen_enabled:
        # Skip QWEN_VLLM tier entirely
        heal_confidence, reason_codes = compute_heal_confidence(healing_input)
        reason_codes.append("QWEN_VLLM_ENABLED=DISABLED:SKIPPED")

        if heal_confidence >= config.heal_confidence_x:
            return HealingDecision(
                heal_confidence=heal_confidence,
                tier=HealingTier.LOCAL_AGENT,
                reason_codes=tuple(reason_codes)
            )
        else:
            # Direct escalation to GEMINI_2_5_PRO
            return HealingDecision(
                heal_confidence=heal_confidence,
                tier=HealingTier.GEMINI_2_5_PRO,
                reason_codes=tuple(reason_codes + ["FORCED_GEMINI_ESCALATION"])
            )

    # Normal routing logic
    return route_healing_tier(healing_input, config)
```

======================================================================
SECTION G — META-LEARNING PROTECTION
======================================================================

### Explicit Boundary Specification
```python
# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X = 0.75  # Upper threshold - CANNOT BE MODIFIED
HEALING_CONFIDENCE_Y = 0.40  # Lower threshold - CANNOT BE MODIFIED

def update_qwen_confidence_prior(error_signature: str, success: bool) -> None:
    """
    Qwen metrics may update healer confidence priors ONLY.

    ALLOWED:
    - Historical success rate updates
    - Failure class prior adjustments
    - Tool readiness certainty updates

    FORBIDDEN:
    - HEALING_CONFIDENCE_X modification
    - HEALING_CONFIDENCE_Y modification
    - Routing election logic changes
    - Safety threshold modifications
    - Embedding scoring changes
    - RAG cutoff modifications
    """
    # Update historical success rate (allowed)
    current_rate = get_historical_success_rate(error_signature)
    if success:
        new_rate = min(1.0, current_rate + 0.1)
    else:
        new_rate = max(0.0, current_rate - 0.1)
    set_historical_success_rate(error_signature, new_rate)

    # THRESHOLDS REMAIN IMMUTABLE
    assert HEALING_CONFIDENCE_X == 0.75, "X threshold is immutable"
    assert HEALING_CONFIDENCE_Y == 0.40, "Y threshold is immutable"
```

### CI Immutability Guard
```python
# ops_scripts/ci/audit_threshold_immutability.py
def validate_threshold_immutability() -> None:
    """Ensure healing thresholds cannot be modified."""
    import agentic_core.L2_execution.healers.healing_tier_router as router

    # These values must never change
    assert hasattr(router, 'HEALING_CONFIDENCE_X'), "HEALING_CONFIDENCE_X not found"
    assert hasattr(router, 'HEALING_CONFIDENCE_Y'), "HEALING_CONFIDENCE_Y not found"

    assert router.HEALING_CONFIDENCE_X == 0.75, f"X threshold modified: {router.HEALING_CONFIDENCE_X}"
    assert router.HEALING_CONFIDENCE_Y == 0.40, f"Y threshold modified: {router.HEALING_CONFIDENCE_Y}"

    print("OK: Threshold immutability validated")
```

======================================================================
SECTION H — HEALTH ENDPOINT
======================================================================

### Enhanced Health Specification
```python
def get_qwen_health_status() -> dict[str, Any]:
    """Comprehensive health endpoint with determinism visibility."""
    return {
        "status": "healthy" if not circuit_breaker.is_circuit_open() else "degraded",
        "model_id": "Qwen/Qwen2.5-7B-Instruct",
        "model_revision": QWEN_MODEL_REVISION_SHA,
        "determinism_digest": compute_current_determinism_digest(),
        "cuda_version": get_cuda_version(),
        "vllm_version": QWEN_VLLM_VERSION,
        "torch_version": get_torch_version(),
        "circuit_open": circuit_breaker.is_circuit_open(),
        "replay_mode_supported": True,
        "last_failure": circuit_breaker.last_failure_timestamp,
        "failure_count": circuit_breaker.failure_count,
        "gpu_memory_used_mb": get_gpu_memory_usage(),
        "process_id": vllm_process_manager.get_pid() if vllm_process_manager.is_running() else None
    }

@app.get("/health/qwen")
async def qwen_health() -> dict[str, Any]:
    """Health check endpoint for Qwen tier."""
    return get_qwen_health_status()
```

======================================================================
SECTION I — EMBEDDING GOVERNANCE LOCK (OPTION A)
======================================================================

### Explicit Governance Constraints
```python
# EMBEDDING GOVERNANCE LOCK - UNMODIFIABLE
EMBEDDING_GOVERNANCE_INVARIANTS = {
    "embedding_factory_unchanged": True,
    "openai_sole_provider": True,
    "no_local_embedding_providers": True,
    "replay_key_construction_unchanged": True,
    "seed_pack_governance_unchanged": True,
    "blas_configuration_unchanged": True,
    "embeddings_c0_informational_only": True,
    "no_embedding_influence_on_routing": True
}
```

### CI Enforcement Script
```python
# ops_scripts/ci/audit_embedding_governance.py
def validate_embedding_governance_lock() -> None:
    """Prevent Qwen/vLLM references in embedding architecture."""
    embedding_files = [
        "agentic_core/embeddings/embedding_factory.py",
        "agentic_core/embeddings/embedding_input_guard.py",
        "system_learning/engines/embedding_service_factory.py"
    ]

    forbidden_patterns = ["qwen", "vllm", "Qwen", "VLLM"]
    violations = []

    for file_path in embedding_files:
        if not Path(file_path).exists():
            continue

        content = Path(file_path).read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in content:
                violations.append(f"{file_path}:{pattern}")

    if violations:
        print("ERROR: Embedding governance violations detected:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nQwen/vLLM references forbidden in embedding architecture")
        sys.exit(1)

    print("OK: Embedding governance lock validated")
```

### Architectural Separation Enforcement
```python
def validate_architectural_separation() -> None:
    """Ensure Qwen logic stays within healing tier boundaries."""
    forbidden_directories = [
        "agentic_core/L0_routing",
        "agentic_core/L4_state",
        "agentic_core/embeddings",
        "system_learning/engines/embedding_service_factory.py"
    ]

    qwen_patterns = ["qwen", "Qwen", "vllm", "VLLM"]

    for directory in forbidden_directories:
        if not Path(directory).exists():
            continue

        for py_file in Path(directory).rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for pattern in qwen_patterns:
                if pattern in content:
                    raise RuntimeError(
                        f"Qwen pattern '{pattern}' found in forbidden location: {py_file}"
                    )
```

======================================================================
IMPLEMENTATION SPECIFICATION
======================================================================

### Phase 1: Determinism Infrastructure
1. Implement full SHA-256 determinism digest with runtime substrate
2. Create Unicode canonicalization with output hashing
3. Extend InvocationRecord with required metadata fields
4. Implement replay validation test suite

### Phase 2: Sovereignty Hardening
1. Add enum leakage CI enforcement
2. Implement startup kill switch validation
3. Create threshold immutability guards
4. Add deterministic circuit breaker with replay safety

### Phase 3: Process Isolation & Validation
1. Implement fail-fast GPU validation with QwenGPUCapabilityError
2. Add OOM escalation through router choke point
3. Create enhanced health endpoint with determinism visibility
4. Add comprehensive audit metadata collection

### Phase 4: Governance Enforcement
1. Implement embedding governance lock CI guards
2. Add architectural separation validation
3. Create meta-learning boundary protection
4. Add comprehensive CI enforcement suite

### Phase 5: Integration & Validation
1. End-to-end sovereign compliance testing
2. Replay mode validation across all components
3. Performance and reliability validation
4. Documentation and operational runbooks

======================================================================
SUCCESS CRITERIA
======================================================================

1. **Sovereign Compliance**: Zero invariant violations across all boundaries
2. **Determinism Proof**: Identical digest and output_hash across replay invocations
3. **Enum Enforcement**: No HealingTier.QWEN_VLLM leakage outside choke points
4. **Embedding Governance**: No embedding architecture modifications
5. **Process Isolation**: Proper GPU validation and OOM escalation
6. **Replay Safety**: Circuit breaker deterministic in replay mode
7. **Meta-Learning Protection**: Threshold immutability maintained
8. **CI Enforcement**: All guards pass in continuous integration

This unified corrected plan replaces all previous Qwen hardening drafts and provides the authoritative Phase 10 sovereign-compliant specification for HealingTier.QWEN_VLLM integration.

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

