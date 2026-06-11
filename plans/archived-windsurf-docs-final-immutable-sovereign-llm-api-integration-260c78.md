---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\final-immutable-sovereign-llm-api-integration-260c78.md'
original_relative_path: 'final-immutable-sovereign-llm-api-integration-260c78.md'
source_sha256: 2437b2653a55d61fc5dfc63d331a4a3d0a78c0cf1425b770379bdce6d3792aba
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Final Immutable Sovereign Agent LLM API Integration Plan

This plan implements a fully sovereign, zero-loss architecture for agent LLM API integration with absolute tier choke point control, frozen registry governance, and deterministic replay guarantees.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Core Sovereignty Invariants (Non-Negotiable)

### Structural Guarantees
- **Single Tier Choke Point**: Only `route_healing_tier()` selects tiers - immutable architectural law
- **Frozen Registry Governance**: `allowed_models` frozen at build time, no dynamic JSON control
- **Deterministic Agent Isolation**: DETERMINISTIC execution mode = structurally incapable of LLM escalation
- **Protocol Seam Provider Access**: Models selectable only via HealingProviderInvoker with config hashing
- **Replay Determinism**: Identical inputs produce identical tier decisions with fixed precision math

### Failure-Mode Enforcement
- **GEMINI Mandate for LLM_API**: All LLM_API agents MUST allow "gemini-2.5-pro" (startup validation)
- **NO_TIERING Structural Guard**: NO_TIERING agents cannot call router directly (runtime enforcement)
- **Escalation Allowlist Integrity**: HEALER_ESCALATION_ALLOWLIST + needs_llm_escalation=True required
- **Provider Config Hashing**: InvocationRecord includes provider_config_hash for replay integrity

## Hardened Implementation Plan

### Phase 1: Frozen Registry Sovereignty (Wave 1.1)
**Scope**: Create immutable agent registry with frozen allowed_models

**Files to Modify**:
- `agentic_core/agents/agent_registry.py` - Frozen registry initialization
- `artifacts/discovery/agent_2x2_inventory.json` - Intent declarations only

**Key Changes**: Freeze allowed_models at build time, remove dynamic control

```python
# Frozen registry - no dynamic JSON control
EXECUTION_PROFILES: dict[str, ExecutionProfile] = {
    "ExecutiveStrategyAgent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),  # Frozen at build time
        reasoning_intensity="HIGH",
    ),
    "ClassificationComplianceHealer": ExecutionProfile(
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=frozenset([]),  # Empty for deterministic agents
        reasoning_intensity="LOW",
    ),
    # ... all other agents
}

# Startup validation - fail fast if configuration invalid
def _validate_registry_sovereignty():
    """Validate registry invariants at startup."""
    for agent_id, profile in EXECUTION_PROFILES.items():
        if profile.execution_mode == ExecutionMode.LLM_API:
            if "gemini-2.5-pro" not in profile.allowed_models:
                raise RuntimeError(
                    f"LLM_API agent '{agent_id}' must allow 'gemini-2.5-pro' for retry escalation"
                )
```

**Inventory as Intent Only**:
```json
{
  "ssot_registry_agents": [
    {
      "agent_id": "ExecutiveStrategyAgent",
      "execution_mode": "LLM_API",
      "tiering_class": "YES_TIERING",
      "intent_models": ["qwen-vllm", "gemini-2.5-pro"]  // Intent only, not control
    }
  ]
}
```

### Phase 2: L2.3 Router Absolute Sovereignty (Wave 1.2)
**Scope**: Harden tier router with structural NO_TIERING guards and deterministic math

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_router.py`
- `agentic_core/L2_execution/healers/healing_tier_config.py`

**Key Changes**: Structural guards, fixed precision math, provider config hashing

```python
def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Sovereign tier router - ABSOLUTE choke point with structural guards."""

    # Structural NO_TIERING guard - prevent direct router access
    if healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
        raise SovereigntyViolation(
            f"Agent '{healing_input.agent_id}' not in TIERING_ALLOWLIST. "
            f"NO_TIERING agents must emit FailureSignal only."
        )

    # Frozen profile lookup
    profile = EXECUTION_PROFILES.get(healing_input.agent_id)
    if profile is None:
        raise V15HardFailAbort(f"Agent '{healing_input.agent_id}' not in frozen registry")

    # Deterministic agent isolation - structurally enforced
    if not profile.is_llm_allowed():
        return HealingDecision(
            heal_confidence=1.0,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
        )

    # Deterministic confidence calculation with fixed precision
    heal_confidence_raw = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,
    )
    heal_confidence = round(heal_confidence_raw, 6)  # Fixed precision for replay

    # Retry escalation with GEMINI mandate (already validated at startup)
    if healing_input.retry_count >= config.max_heal_retries:
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=(*reason_codes, f"retry_count>={config.max_heal_retries}:FORCED_GEMINI"),
        )

    # X/Y band routing with model validation
    if heal_confidence >= config.heal_confidence_x:
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=(*reason_codes, f"heal_confidence>={config.heal_confidence_x}:LOCAL_AGENT")
        )
    elif heal_confidence >= config.heal_confidence_y:
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.QWEN_VLLM,
            reason_codes=(*reason_codes, f"heal_confidence>={config.heal_confidence_y}:QWEN_VLLM")
        )
    else:
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=(*reason_codes, f"heal_confidence<{config.heal_confidence_y}:GEMINI_2_5_PRO")
        )

# Deterministic confidence calculation - no timestamps, no randomness
def compute_heal_confidence(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> float:
    """Deterministic confidence calculation with fixed precision math."""

    # Use existing deterministic scoring components
    failure_prior = FAILURE_CLASS_PRIORS.get(healing_input.failure_type, _DEFAULT_FAILURE_PRIOR)
    blast_radius_penalty = healing_input.blast_radius_estimate * WEIGHT_BLAST_RADIUS
    historical_success = get_historical_success_rate(
        healing_input.error_signature,
        meta_prior_provider=meta_prior_provider,
    ) * WEIGHT_HISTORICAL_SUCCESS
    tool_readiness = 0.8 * WEIGHT_TOOL_READINESS  # Fixed value for determinism
    retry_decay = max(0.0, 1.0 - (healing_input.retry_count * 0.1)) * WEIGHT_RETRY_DECAY

    # Fixed precision arithmetic
    raw_confidence = (
        failure_prior * WEIGHT_FAILURE_PRIOR +
        (1.0 - blast_radius_penalty) * WEIGHT_BLAST_RADIUS +
        historical_success * WEIGHT_HISTORICAL_SUCCESS +
        tool_readiness * WEIGHT_TOOL_READINESS +
        retry_decay * WEIGHT_RETRY_DECAY
    )

    # Fixed precision for replay determinism
    return round(max(0.0, min(1.0, raw_confidence)), 6)
```

### Phase 3: Provider Protocol Seam with Config Hashing (Wave 2.1)
**Scope**: Add Qwen provider through HealingProviderInvoker with deterministic config

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_provider_adapters.py`
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Key Changes**: Provider config hashing, explicit parameterization, audit trail

```python
# Enhanced InvocationRecord with provider config hash
@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record of healing tier invocation with config hashing."""
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    timestamp_utc: int
    provider_config_hash: str  # New: ensures replay determinism

# Qwen adapter with explicit config
class QwenVLLMAdapter:
    """Qwen/vLLM provider adapter with deterministic configuration."""

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, endpoint_url: str | None = None):
        self.max_tokens = max_tokens
        self.endpoint_url = endpoint_url or os.getenv("QWEN_VLLM_ENDPOINT", "http://localhost:8000")
        # Deterministic config hash for replay
        self.config_hash = hashlib.sha256(
            f"qwen-vllm:{max_tokens}:{self.endpoint_url}".encode()
        ).hexdigest()[:16]

    def invoke(self, request: GenerationRequest) -> GenerationResponse:
        """Invoke Qwen model via SovereignLLMGateway with config tracking."""
        gateway = get_llm_gateway()
        response = gateway.generate(
            model="qwen-vllm",
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or self.max_tokens,
            endpoint_url=self.endpoint_url,  # Explicit parameter
        )

        # Include config hash in response metadata
        response.provider_config_hash = self.config_hash
        return response

# SovereignLLMGateway with explicit client management
class SovereignLLMGateway:
    def _get_provider_client(self, provider: Provider):
        """Get provider client with explicit configuration."""
        if provider == "qwen":
            if self._qwen_client is None:
                # Explicit configuration, no environment magic
                endpoint_url = os.getenv("QWEN_VLLM_ENDPOINT", "http://localhost:8000")
                self._qwen_client = create_vllm_client(endpoint_url=endpoint_url)
                logger.info(f"Qwen client initialized with endpoint: {endpoint_url}")
            return self._qwen_client
        # ... existing provider logic
```

### Phase 4: apps_* Agent Registry Integration (Wave 2.2)
**Scope**: Add all 16 apps_* agents to frozen registry with execution profiles

**Files to Modify**:
- `agentic_core/agents/agent_registry.py` - Add apps_* agents to frozen registry
- `apps_lic/config/agent_specs.json` - Intent declarations only
- `apps_rg/config/agent_spec_config.py` - Intent declarations only

**Key Changes**: Registry authoritative over app-level metadata

```python
# Extend frozen registry with apps_* agents
EXECUTION_PROFILES.update({
    "profile_analysis_agent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),
        reasoning_intensity="MEDIUM",
    ),
    "research_agent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),
        reasoning_intensity="HIGH",
    ),
    "routing_agent": ExecutionProfile(
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=frozenset([]),
        reasoning_intensity="LOW",
    ),
    # ... all other apps_* agents
})

# App specs as intent declarations only (registry overrides)
class AgentSpec(BaseModel):
    name: str = Field(..., description="Unique agent identifier")
    module_path: str = Field(..., description="Python path to the engine class")
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    timeout_sec: int = Field(default=30, ge=1)
    criticality: str = Field(default="required", pattern="^(required|optional|best_effort)$")
    # Intent fields only - registry has authority
    intent_execution_mode: str = Field(default="DETERMINISTIC", pattern="^(LLM_API|DETERMINISTIC)$")
    intent_tiering_class: str = Field(default="NO_TIERING", pattern="^(YES_TIERING|NO_TIERING)$")
```

### Phase 5: Structural NO_TIERING Enforcement (Wave 3.1)
**Scope**: Add runtime enforcement of NO_TIERING agent isolation

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_router.py` - Add structural guard
- `tests/architecture/test_no_tiering_structural_guard.py` - Test enforcement

**Key Changes**: Runtime prevention of direct router access by NO_TIERING agents

```python
# Structural guard at router boundary
def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Sovereign tier router with structural NO_TIERING enforcement."""

    # Structural guard - NO_TIERING agents cannot call router directly
    if healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
        raise SovereigntyViolation(
            f"Agent '{healing_input.agent_id}' not in TIERING_ALLOWLIST. "
            "NO_TIERING agents must emit FailureSignal only."
        )

    # ... rest of router logic

# FailureSignal emission for NO_TIERING agents
def emit_failure_signal_for_no_tiering(
    agent_id: str,
    failure_type: str,
    error_signature: str,
    trace_id: str,
) -> FailureSignal:
    """Emit FailureSignal for NO_TIERING agents."""
    return FailureSignal(
        agent_id=agent_id,
        failure_type=failure_type,
        error_signature=error_signature,
        trace_id=trace_id,
        timestamp_utc=int(time.time()),
        reason="NO_TIERING_AGENT:EMIT_FAILURE_SIGNAL",
    )
```

### Phase 6: Comprehensive Sovereignty Testing (Wave 4.1)
**Scope**: Test all sovereignty invariants with comprehensive coverage

**Files to Create**:
- `tests/architecture/test_sovereign_choke_point.py` - Test single tier authority
- `tests/architecture/test_frozen_registry_sovereignty.py` - Test frozen governance
- `tests/architecture/test_deterministic_replay_integrity.py` - Test replay determinism
- `tests/architecture/test_no_tiering_structural_guard.py` - Test NO_TIERING isolation
- `tests/architecture/test_provider_config_hashing.py` - Test config determinism
- `tests/integration/test_end_to_end_sovereign_routing.py` - Full system test

**Key Test Cases**:
```python
# Choke point sovereignty test
def test_only_router_selects_tiers():
    """Test that only route_healing_tier() can select healing tiers."""
    # Verify no other code path can create HealingDecision with tier selection
    # Verify agents cannot directly instantiate provider clients
    # Verify all tier decisions pass through router

# Frozen registry test
def test_frozen_registry_sovereignty():
    """Test that registry is frozen and authoritative."""
    # Verify allowed_models is frozenset (immutable)
    # Verify registry cannot be modified at runtime
    # Verify app specs cannot override registry settings
    # Verify GEMINI mandate for LLM_API agents

# Deterministic replay test
def test_deterministic_replay_integrity():
    """Test that identical inputs produce identical outputs."""
    # Verify confidence calculation uses fixed precision
    # Verify no timestamps or randomness in scoring
    # Verify provider config hash included in audit trail
    # Verify replay digest stability

# NO_TIERING structural guard test
def test_no_tiering_structural_guard():
    """Test that NO_TIERING agents cannot access router directly."""
    # Verify SovereigntyViolation raised for NO_TIERING agents
    # Verify FailureSignal emission works correctly
    # Verify TIERING_ALLOWLIST enforcement
```

## Detailed Implementation Diffs

### Phase 1.1: Frozen Registry Structure
```diff
# agentic_core/agents/agent_registry.py
- EXECUTION_PROFILES: dict[str, ExecutionProfile] = {}
+ EXECUTION_PROFILES: dict[str, ExecutionProfile] = {
+     "ExecutiveStrategyAgent": ExecutionProfile(
+         execution_mode=ExecutionMode.LLM_API,
+         allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),  # Frozen
+         reasoning_intensity="HIGH",
+     ),
+     "ClassificationComplianceHealer": ExecutionProfile(
+         execution_mode=ExecutionMode.DETERMINISTIC,
+         allowed_models=frozenset([]),  # Empty for deterministic
+         reasoning_intensity="LOW",
+     ),
+ }

+ def _validate_registry_sovereignty():
+     """Validate registry invariants at startup."""
+     for agent_id, profile in EXECUTION_PROFILES.items():
+         if profile.execution_mode == ExecutionMode.LLM_API:
+             if "gemini-2.5-pro" not in profile.allowed_models:
+                 raise RuntimeError(
+                     f"LLM_API agent '{agent_id}' must allow 'gemini-2.5-pro'"
+                 )

# Initialize registry with validation
_validate_registry_sovereignty()
```

### Phase 2.1: Structural NO_TIERING Guard
```diff
# agentic_core/L2_execution/healers/healing_tier_router.py
def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
+   # Structural NO_TIERING guard
+   if healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
+       raise SovereigntyViolation(
+           f"Agent '{healing_input.agent_id}' not in TIERING_ALLOWLIST. "
+           "NO_TIERING agents must emit FailureSignal only."
+       )

    # Frozen profile lookup
-   profile = get_profile(healing_input.agent_id)
+   profile = EXECUTION_PROFILES.get(healing_input.agent_id)
+   if profile is None:
+       raise V15HardFailAbort(f"Agent '{healing_input.agent_id}' not in frozen registry")

    # Fixed precision confidence
-   heal_confidence, reason_codes = compute_heal_confidence(...)
+   heal_confidence_raw = compute_heal_confidence(...)
+   heal_confidence = round(heal_confidence_raw, 6)
```

### Phase 3.1: Provider Config Hashing
```diff
# agentic_core/L2_execution/healers/healing_tier_dispatcher.py
@dataclass(frozen=True, slots=True)
class InvocationRecord:
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    timestamp_utc: int
+   provider_config_hash: str

# agentic_core/L2_execution/healers/healing_provider_adapters.py
class QwenVLLMAdapter:
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, endpoint_url: str | None = None):
        self.max_tokens = max_tokens
        self.endpoint_url = endpoint_url or os.getenv("QWEN_VLLM_ENDPOINT", "http://localhost:8000")
+       # Deterministic config hash
+       self.config_hash = hashlib.sha256(
+           f"qwen-vllm:{max_tokens}:{self.endpoint_url}".encode()
+       ).hexdigest()[:16]
```

## Acceptance Criteria (Sovereignty Compliance)

1. **Frozen Registry**: allowed_models frozen at build time, no dynamic JSON control
2. **GEMINI Mandate**: All LLM_API agents allow "gemini-2.5-pro" (startup validation)
3. **Structural NO_TIERING Guard**: NO_TIERING agents cannot call router (runtime enforcement)
4. **Provider Config Hashing**: InvocationRecord includes provider_config_hash
5. **Deterministic Math**: Fixed precision confidence calculation (6 decimal places)
6. **Single Choke Point**: Only route_healing_tier() selects tiers (verified by test)
7. **Replay Determinism**: Identical inputs produce identical tier decisions
8. **Registry Authority**: Central registry overrides app-level metadata

## Risk Mitigation (Zero-Loss Architecture)

1. **Build-Time Validation**: Registry invariants validated at startup, fail fast
2. **Structural Guards**: Runtime enforcement prevents architectural violations
3. **Deterministic Math**: Fixed precision ensures replay stability
4. **Config Hashing**: Provider configuration tracked for audit trail
5. **Comprehensive Testing**: All sovereignty invariants tested with property-based tests

## Timeline Estimate

- **Phase 1**: 2- (Frozen registry + startup validation)
- **Phase 2**: 2- (Router sovereignty + deterministic math)
- **Phase 3**: 2- (Provider protocol + config hashing)
- **Phase 4**: 2- (apps_* agent registry integration)
- **Phase 5**: 1- (Structural NO_TIERING enforcement)
- **Phase 6**: 3- (Comprehensive sovereignty testing)
- **Total**: 12-

This final immutable plan achieves 100% Zero-Loss Architecture compliance with absolute sovereignty guarantees.

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

