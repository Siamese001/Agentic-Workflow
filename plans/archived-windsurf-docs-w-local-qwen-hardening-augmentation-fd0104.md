---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\w-local-qwen-hardening-augmentation-fd0104.md'
original_relative_path: 'w-local-qwen-hardening-augmentation-fd0104.md'
source_sha256: 72c402e04e75401b74db6c5fb1e70d312445343bb009e49585483c851ac0c429
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W-LOCAL-QWEN HARDENING AUGMENTATION - Sovereign Healing Tier Integration

This plan hardens the Qwen v2.5 local vLLM installation to operate strictly as a Healing Tier provider under Phase 10 architecture, ensuring complete sovereignty compliance while maintaining embedding governance invariants.

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

### Implementation Points
1. Add `QWEN_VLLM_ENABLED` check in `route_healing_tier()`
2. Log tier skipping with explicit reason code
3. Maintain deterministic routing behavior regardless of setting

## SECTION 3 — DETERMINISM ENFORCEMENT

### Pinned Revisions
```python
# In healing_tier_config.py
QWEN_MODEL_REVISION_SHA = "a1b2c3d4e5f6..."  # Pin exact model commit
QWEN_TOKENIZER_REVISION_SHA = "f6e5d4c3b2a1..."  # Pin exact tokenizer commit
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

### Determinism Digest Implementation
```python
def compute_qwen_determinism_digest(
    model_revision: str,
    tokenizer_revision: str,
    inference_params: dict
) -> str:
    """Compute W-QWEN-DETERMINISM-DIGEST for audit trail."""
    payload = f"{model_revision}:{tokenizer_revision}:{inference_params}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
```

### Digest Integration Points
1. **Per Invocation**: Append to `InvocationRecord`
2. **L4B Snapshot**: Include in healing snapshot metadata
3. **Replay Mode**: Reject non-deterministic configurations
4. **Audit Trail**: Log digest with each healing event

## SECTION 4 — GPU HARD FAIL VALIDATION

### Startup Validation
```python
def validate_gpu_capabilities(model_size: str) -> None:
    """Hard fail on GPU capability mismatch."""
    # VRAM threshold validation
    # CUDA version validation
    # Compute capability validation
    # Driver version validation
```

### Model-Specific Requirements
- **Qwen2.5-7B**: Minimum 16GB VRAM, CUDA 11.8+
- **Qwen2.5-14B**: Minimum 32GB VRAM, CUDA 12.0+
- **Compute Capability**: Minimum 7.0 (Turing架构)

### Runtime Safeguards
1. **OOM Detection**: Catch CUDA OOM exceptions
2. **Escalation on Failure**: Auto-escalate to GEMINI_2_5_PRO
3. **FailureSignal Emission**: Include OOM reason code
4. **Memory Monitoring**: Track GPU memory usage per invocation

## SECTION 5 — PROCESS ISOLATION

### vLLM Process Requirements
- **Separate Process**: vLLM runs in isolated process
- **Boundary Client Access**: Only via `tools/vllm_boundary_client.py`
- **Memory Isolation**: No shared memory with embedding factory
- **State Immutability**: No system state mutation

### Process Management
```python
class VLLMProcessManager:
    """Manage isolated vLLM server process."""
    def start_server(self, model_config: dict) -> ProcessHandle
    def stop_server(self) -> None
    def health_check(self) -> bool
    def get_memory_usage(self) -> dict
```

### Communication Protocol
- **HTTP API Only**: OpenAI-compatible endpoint
- **No Direct SDK**: No in-process vLLM imports
- **Timeout Enforcement**: 30-second request timeout
- **Circuit Breaker**: Auto-disable on repeated failures

## SECTION 6 — AUDIT REQUIREMENTS

### Enhanced InvocationRecord
```python
@dataclass(frozen=True, slots=True)
class QwenInvocationRecord(InvocationRecord):
    """Extended record for Qwen invocations with full audit trail."""
    revision_sha: str
    determinism_digest: str
    latency_ms: int
    memory_used_mb: int
    gpu_utilization: float
    trace_id: str
```

### Required Metadata per Invocation
- **tier**: "QWEN_VLLM"
- **model_id**: "Qwen/Qwen2.5-7B-Instruct" or "Qwen/Qwen2.5-14B-Instruct"
- **revision_sha**: Pinned model commit hash
- **heal_confidence**: Router confidence score
- **latency_ms**: Request latency in milliseconds
- **memory_used_mb**: GPU memory consumed
- **determinism_digest**: W-QWEN-DETERMINISM-DIGEST
- **trace_id**: Correlation identifier

### L4B Snapshot Integration
- **HealingOutcomeIntakeAdapter**: Persist Qwen metadata to L4B
- **Immutable Records**: No post-hoc modification
- **Canonical Serialization**: Deterministic JSON encoding

## SECTION 7 — EMBEDDING GOVERNANCE LOCK

### Explicit Constraints
1. **EmbeddingServiceFactory**: Remains unchanged - OpenAI-only
2. **OpenAI text-embedding-3-large**: Remains sole production embedding provider
3. **Local Embedding Providers**: FORBIDDEN - no vLLM embedding integration
4. **Replay Key Construction**: No changes - existing keys preserved
5. **Seed Pack Modifications**: No changes - existing packs preserved
6. **BLAS Configuration**: No changes - existing optimization preserved
7. **Embedding Results**: Remain C0 informational only

### CI Guard Implementation
```bash
# .github/workflows/embedding-governance.yml
- name: Check Embedding Governance
  run: |
    python -m ops_scripts.ci.audit_embedding_governance \
      --forbidden-patterns "qwen|vllm" \
      --protected-files "embedding_factory.py"
```

## SECTION 8 — CI ENFORCEMENT

### Static Enforcement Rules
Fail build if any of these patterns are detected:

1. **Import Violations**:
   ```python
   # FORBIDDEN outside boundary files
   from vllm import LLM, SamplingParams
   import vllm
   ```

2. **Direct Model References**:
   ```python
   # FORBIDDEN outside HealingProviderInvoker
   model = "Qwen/Qwen2.5-7B-Instruct"
   ```

3. **Direct API Calls**:
   ```python
   # FORBIDDEN outside boundary client
   response = requests.post("http://localhost:8000/v1/chat/completions")
   ```

4. **Tier Bypass Attempts**:
   ```python
   # FORBIDDEN - must use route_healing_tier()
   if confidence > 0.5:
       return HealingTier.QWEN_VLLM
   ```

### Enforcement Scripts
- `ops_scripts/ci/audit_healing_tier_enforcement.py`
- `ops_scripts/ci/audit_vllm_import_boundaries.py`
- `ops_scripts/ci/audit_embedding_governance.py`

## SECTION 9 — META-LEARNING PROTECTION

### Confidence Tuning Only
Qwen performance metrics may influence:
- **Healer confidence tuning** ONLY
- **Historical success rate updates** ONLY

### Prohibited Influences
Qwen must NOT influence:
- **Routing thresholds**: Direct threshold modifications
- **Safety tier thresholds**: Safety policy changes
- **L0 election logic**: Agent selection criteria
- **Embedding scoring**: Embedding quality metrics
- **RAG cutoffs**: Retrieval threshold changes

### Validation Requirements
- **ReplayValidator**: Must pass all replay tests
- **OscillationDetector**: Must detect and prevent healing oscillations
- **proposal_only=True**: Default mode for all meta-learning operations

## SECTION 10 — SUCCESS CRITERIA UPDATE

### Revised Success Metrics
Replace latency-focused criteria with sovereignty-focused criteria:

1. **Determinism Proof**: Identical digest across 2+ invocations
2. **Sovereignty Compliance**: Zero invariant violations
3. **Tier Enforcement**: No tier bypass attempts detected
4. **Embedding Governance**: No embedding factory changes
5. **OOM Handling**: Proper escalation on GPU memory failures
6. **Kill Switch**: QWEN_VLLM_ENABLED toggle validated

### Validation Tests
```python
def test_qwen_determinism_digest():
    """Verify identical digest across invocations."""

def test_qwen_tier_enforcement():
    """Verify no tier bypass possible."""

def test_qwen_embedding_governance():
    """Verify embedding factory unchanged."""

def test_qwen_oom_escalation():
    """Verify proper OOM handling."""
```

## IMPLEMENTATION PHASES

### Phase 1: Sovereignty Infrastructure
1. Add QWEN_VLLM_ENABLED kill switch
2. Implement determinism digest computation
3. Create GPU validation utilities
4. Add CI enforcement scripts

### Phase 2: Process Isolation
1. Implement VLLMProcessManager
2. Harden boundary client with timeouts
3. Add circuit breaker logic
4. Create health check endpoints

### Phase 3: Audit & Monitoring
1. Extend InvocationRecord for Qwen metadata
2. Integrate with L4B snapshot persistence
3. Add performance monitoring
4. Create audit trail visualization

### Phase 4: Validation & Testing
1. Create comprehensive test suite
2. Add replay mode validation
3. Implement OOM simulation tests
4. Add CI enforcement validation

### Phase 5: Meta-Learning Integration
1. Add confidence tuning hooks
2. Implement historical success tracking
3. Create oscillation detection
4. Validate proposal-only operations

## HARDENING SUMMARY

This plan transforms Qwen v2.5 from a potential architectural disruption into a sovereign-compliant healing tier that:
- **Respects all sovereignty boundaries**
- **Maintains embedding governance invariants**
- **Provides deterministic, auditable healing**
- **Fails gracefully with proper escalation**
- **Integrates seamlessly with existing architecture**

The hardened approach ensures Qwen enhances healing capabilities without compromising the sovereign architecture principles established in Phase 10.

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

