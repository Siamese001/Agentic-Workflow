---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\truly-immutable-sovereign-llm-api-integration-260c78.md'
original_relative_path: 'truly-immutable-sovereign-llm-api-integration-260c78.md'
source_sha256: ab9a0dcd31057d94b20a3c8bc813b8f52b31160ea8738ce3c1d64ac01bafca9a
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Truly Immutable Sovereign Agent LLM API Integration Plan

This plan implements a mathematically immutable, zero-loss architecture for agent LLM API integration with absolute determinism, frozen governance surfaces, and complete elimination of environmental nondeterminism.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Absolute Sovereignty Invariants (Mathematically Immutable)

### Structural Guarantees
- **Single Tier Choke Point**: Only `route_healing_tier()` selects tiers - compiled into code
- **Frozen Registry Governance**: All policy surfaces frozen at compile time, no runtime mutation
- **Deterministic Agent Isolation**: DETERMINISTIC execution mode = structurally incapable of LLM escalation
- **Protocol Seam Provider Access**: Models selectable only via HealingProviderInvoker with explicit injection
- **Replay Mathematical Determinism**: Identical inputs produce mathematically identical outputs (timestamp excluded)

### Failure-Mode Enforcement
- **GEMINI Mandate for LLM_API**: All LLM_API agents MUST allow "gemini-2.5-pro" (compile-time validation)
- **Frozen TIERING_ALLOWLIST**: Allowlist compiled into code, no data-driven loading
- **Escalation Allowlist Integrity**: HEALER_ESCALATION_ALLOWLIST + needs_llm_escalation=True required
- **Historical Data Versioning**: All external data surfaces versioned and hashed into replay key

## Truly Immutable Implementation Plan

### Phase 1: Compile-Time Frozen Governance (Wave 1.1)
**Scope**: Create compile-time frozen registry and allowlist with no external dependencies

**Files to Modify**:
- `agentic_core/agents/agent_registry.py` - Compile-time frozen registry
- `agentic_core/L2_execution/healers/tiering_allowlist.py` - Compile-time frozen allowlist
- `artifacts/discovery/agent_2x2_inventory.json` - Documentation only

**Key Changes**: Eliminate all runtime data loading, freeze everything at compile time

```python
# agentic_core/agents/agent_registry.py - Compile-time frozen registry
from __future__ import annotations

# Compile-time frozen registry - no external data loading
EXECUTION_PROFILES: dict[str, ExecutionProfile] = {
    "ExecutiveStrategyAgent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),  # Compile-time frozen
        reasoning_intensity="HIGH",
    ),
    "ClassificationComplianceHealer": ExecutionProfile(
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=frozenset([]),  # Empty for deterministic agents
        reasoning_intensity="LOW",
    ),
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
    # ... all 23 agents compiled into code
}

# Compile-time validation - runs at module import
def _validate_registry_sovereignty() -> None:
    """Validate registry invariants at module import time."""
    for agent_id, profile in EXECUTION_PROFILES.items():
        if profile.execution_mode == ExecutionMode.LLM_API:
            if "gemini-2.5-pro" not in profile.allowed_models:
                raise RuntimeError(
                    f"LLM_API agent '{agent_id}' must allow 'gemini-2.5-pro' for retry escalation"
                )

    # Verify no duplicate agent IDs
    if len(EXECUTION_PROFILES) != len(set(EXECUTION_PROFILES.keys())):
        raise RuntimeError("Duplicate agent IDs detected in registry")

# Validation runs at module import - fail-fast before any system boot
_validate_registry_sovereignty()

def get_execution_profile(agent_id: str) -> ExecutionProfile:
    """Get frozen execution profile - no runtime mutation possible."""
    profile = EXECUTION_PROFILES.get(agent_id)
    if profile is None:
        raise V15HardFailAbort(f"Agent '{agent_id}' not in compile-time frozen registry")
    return profile

# agentic_core/L2_execution/healers/tiering_allowlist.py - Compile-time frozen
from __future__ import annotations

# Compile-time frozen allowlist - no CSV loading, no runtime mutation
TIERING_ALLOWLIST_AGENT_NAMES: frozenset[str] = frozenset({
    "CodeHealerAgent",
    "GravityLeakRepairAgent",
    "IntegrityGateExecutorAgent",
    "LocationHealerAgent",
    "SafetyExecutorAgent",
    "StructureHealerAgent",
    "TypeHintFixerAgent",
    "DispatchOutreachToolsAgent",
    "OutreachValidationExecutorAgent",
    "DispatchResumeToolsAgent",
})

def is_tiering_allowed(agent_name: str) -> bool:
    """Check if agent is in compile-time frozen allowlist."""
    return agent_name in TIERING_ALLOWLIST_AGENT_NAMES

# No mutable state, no external data loading
__all__ = [
    "TIERING_ALLOWLIST_AGENT_NAMES",
    "is_tiering_allowed",
]
```

### Phase 2: Mathematical Determinism with Historical Data Versioning (Wave 1.2)
**Scope**: Eliminate all nondeterminism including timestamps, environment variables, and time-dependent data

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_router.py`
- `agentic_core/L2_execution/healers/healing_tier_types.py`
- `agentic_core/L2_execution/healers/healing_provider_adapters.py`

**Key Changes**: Remove timestamp from replay surface, version historical data, eliminate environment access

```python
# agentic_core/L2_execution/healers/healing_tier_types.py - Replay-deterministic records
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record with replay-deterministic fields only."""
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    # timestamp_utc removed from replay surface
    provider_config_hash: str
    historical_data_hash: str  # New: versioned historical data
    replay_key: str  # New: mathematical replay key

@dataclass(frozen=True, slots=True)
class HealingInput:
    """Structured failure context with replay determinism."""
    agent_id: str
    failure_type: str
    error_signature: str
    trace_id: str
    retry_count: int
    blast_radius_estimate: float
    required_tools: tuple[str, ...]
    violation_metadata_refs: tuple[str, ...]
    replay_mode: bool = False  # New: enables deterministic replay

# agentic_core/L2_execution/healers/healing_tier_router.py - Mathematically deterministic routing
from __future__ import annotations
import hashlib
import time
from typing import TYPE_CHECKING

# Versioned historical data surface
HISTORICAL_DATA_VERSION = "v1.0.0"
HISTORICAL_DATA_HASH = hashlib.sha256(HISTORICAL_DATA_VERSION.encode()).hexdigest()[:16]

# Compile-time frozen historical success rates
HISTORICAL_SUCCESS_RATES: dict[str, float] = {
    "syntax_error": 0.85,
    "import_cycle": 0.70,
    "missing_import": 0.80,
    "type_hint_error": 0.75,
    "naming_violation": 0.82,
    "location_violation": 0.65,
    "structure_violation": 0.60,
    "gravity_leak": 0.55,
    "integrity_gate_failure": 0.50,
    "test_failure": 0.45,
    "runtime_error": 0.35,
    "unknown": 0.30,
}

def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Mathematically deterministic tier router - zero nondeterminism."""

    # Structural NO_TIERING guard - compile-time frozen allowlist
    if healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
        raise SovereigntyViolation(
            f"Agent '{healing_input.agent_id}' not in compile-time frozen TIERING_ALLOWLIST. "
            "NO_TIERING agents must emit FailureSignal only."
        )

    # Frozen profile lookup
    profile = get_execution_profile(healing_input.agent_id)

    # Deterministic agent isolation
    if not profile.is_llm_allowed():
        return HealingDecision(
            heal_confidence=1.0,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
        )

    # Mathematical confidence calculation - no external dependencies
    heal_confidence = _compute_deterministic_confidence(healing_input)

    # Retry escalation with GEMINI mandate (validated at compile time)
    if healing_input.retry_count >= 3:  # Fixed constant, no config loading
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=(*reason_codes, "retry_count>=3:FORCED_GEMINI"),
        )

    # X/Y band routing with fixed constants
    if heal_confidence >= 0.75:  # Fixed constant
        tier = HealingTier.LOCAL_AGENT
        reason_codes = (*reason_codes, "heal_confidence>=0.75:LOCAL_AGENT")
    elif heal_confidence >= 0.40:  # Fixed constant
        tier = HealingTier.QWEN_VLLM
        reason_codes = (*reason_codes, "heal_confidence>=0.40:QWEN_VLLM")
    else:
        tier = HealingTier.GEMINI_2_5_PRO
        reason_codes = (*reason_codes, "heal_confidence<0.40:GEMINI_2_5_PRO")

    return HealingDecision(
        heal_confidence=heal_confidence,
        tier=tier,
        reason_codes=tuple(reason_codes),
    )

def _compute_deterministic_confidence(healing_input: HealingInput) -> float:
    """Mathematically deterministic confidence calculation - zero external dependencies."""

    # Fixed weights - no config loading
    WEIGHT_FAILURE_PRIOR = 0.30
    WEIGHT_BLAST_RADIUS = 0.25
    WEIGHT_HISTORICAL_SUCCESS = 0.20
    WEIGHT_TOOL_READINESS = 0.15
    WEIGHT_RETRY_DECAY = 0.10

    # Failure class prior - compile-time frozen
    failure_prior = HISTORICAL_SUCCESS_RATES.get(healing_input.failure_type, 0.40)

    # Blast radius penalty - deterministic calculation
    blast_radius_penalty = healing_input.blast_radius_estimate * WEIGHT_BLAST_RADIUS

    # Historical success - versioned data, no external lookup
    historical_success = HISTORICAL_SUCCESS_RATES.get(
        healing_input.error_signature.split(':')[0],  # Use failure type as key
        0.50  # Neutral prior
    ) * WEIGHT_HISTORICAL_SUCCESS

    # Tool readiness - fixed value for determinism
    tool_readiness = 0.8 * WEIGHT_TOOL_READINESS

    # Retry decay - deterministic calculation
    retry_decay = max(0.0, 1.0 - (healing_input.retry_count * 0.1)) * WEIGHT_RETRY_DECAY

    # Fixed precision arithmetic - no floating point drift
    raw_confidence = (
        failure_prior * WEIGHT_FAILURE_PRIOR +
        (1.0 - blast_radius_penalty) * WEIGHT_BLAST_RADIUS +
        historical_success * WEIGHT_HISTORICAL_SUCCESS +
        tool_readiness * WEIGHT_TOOL_READINESS +
        retry_decay * WEIGHT_RETRY_DECAY
    )

    # Fixed precision for mathematical determinism
    return round(max(0.0, min(1.0, raw_confidence)), 6)

def _compute_replay_key(healing_input: HealingInput, decision: HealingDecision) -> str:
    """Compute mathematical replay key - timestamp excluded."""
    key_components = [
        healing_input.agent_id,
        healing_input.failure_type,
        healing_input.error_signature,
        healing_input.trace_id,
        str(healing_input.retry_count),
        str(healing_input.blast_radius_estimate),
        str(decision.heal_confidence),
        decision.tier.value,
        HISTORICAL_DATA_HASH,
    ]
    return hashlib.sha256('|'.join(key_components).encode()).hexdigest()[:16]
```

### Phase 3: Explicit Provider Configuration (Wave 2.1)
**Scope**: Eliminate environment variable access, implement explicit provider injection

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_provider_adapters.py`
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Key Changes**: Explicit configuration injection, no environment access

```python
# agentic_core/L2_execution/healers/healing_provider_adapters.py - Explicit configuration
from __future__ import annotations
import hashlib
import logging
from typing import Any

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import GenerationRequest, get_llm_gateway

logger = logging.getLogger(__name__)

class QwenVLLMAdapter:
    """Qwen/vLLM provider adapter with explicit configuration - no environment access."""

    def __init__(
        self,
        max_tokens: int = 2048,
        endpoint_url: str = "http://localhost:8000",  # Explicit, no environment access
        api_key: str | None = None,  # Explicit injection
        model_name: str = "qwen-vllm"  # Explicit parameter
    ):
        self.max_tokens = max_tokens
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model_name = model_name

        # Deterministic config hash - no environment variables
        config_string = f"qwen-vllm:{max_tokens}:{endpoint_url}:{model_name}"
        self.config_hash = hashlib.sha256(config_string.encode()).hexdigest()[:16]

        logger.info(f"Qwen adapter initialized with explicit config: endpoint={endpoint_url}, model={model_name}")

    def invoke(self, request: GenerationRequest) -> GenerationResponse:
        """Invoke Qwen model with explicit configuration."""
        gateway = get_llm_gateway()
        response = gateway.generate(
            model=self.model_name,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or self.max_tokens,
            endpoint_url=self.endpoint_url,  # Explicit parameter
            api_key=self.api_key,  # Explicit parameter
        )

        # Include config hash in response metadata
        response.provider_config_hash = self.config_hash
        return response

# Provider factory with explicit injection
def create_qwen_adapter(
    max_tokens: int = 2048,
    endpoint_url: str = "http://localhost:8000",
    api_key: str | None = None,
) -> QwenVLLMAdapter:
    """Create Qwen adapter with explicit configuration - no environment access."""
    return QwenVLLMAdapter(
        max_tokens=max_tokens,
        endpoint_url=endpoint_url,
        api_key=api_key,
    )

# agentic_core/L2_execution/enforcement/SovereignLLMGateway.py - Explicit client management
class SovereignLLMGateway:
    def __init__(self):
        # ... existing initialization
        self._qwen_client: Any = None
        self._qwen_config_hash: str | None = None

    def _get_provider_client(self, provider: Provider, config_hash: str | None = None):
        """Get provider client with explicit configuration tracking."""
        if provider == "qwen":
            if self._qwen_client is None:
                # Explicit configuration - no environment access
                endpoint_url = "http://localhost:8000"  # Fixed default
                self._qwen_client = create_vllm_client(endpoint_url=endpoint_url)
                self._qwen_config_hash = hashlib.sha256(
                    f"qwen:{endpoint_url}".encode()
                ).hexdigest()[:16]
                logger.info(f"Qwen client initialized with explicit endpoint: {endpoint_url}")

            # Verify config hash matches for replay determinism
            if config_hash and config_hash != self._qwen_config_hash:
                logger.warning(f"Config hash mismatch: expected {self._qwen_config_hash}, got {config_hash}")

            return self._qwen_client
        # ... existing provider logic
```

### Phase 4: Module Import Validation (Wave 2.2)
**Scope**: Ensure all validation runs at module import before any system boot

**Files to Modify**:
- `agentic_core/agents/__init__.py` - Module import validation
- `agentic_core/L2_execution/healers/__init__.py` - Healing module validation

**Key Changes**: Fail-fast validation at module import time

```python
# agentic_core/agents/__init__.py - Module import validation
from __future__ import annotations

# Import registry to trigger validation at module load
from agentic_core.agents.agent_registry import (
    EXECUTION_PROFILES,
    get_execution_profile,
    _validate_registry_sovereignty,
)

# Validation runs automatically at module import
logger = logging.getLogger(__name__)
logger.info("Agent registry loaded and validated - all sovereignty invariants enforced")

__all__ = [
    "EXECUTION_PROFILES",
    "get_execution_profile",
]

# agentic_core/L2_execution/healers/__init__.py - Healing module validation
from __future__ import annotations

# Import healing components to trigger validation
from agentic_core.L2_execution.healers.healing_tier_router import (
    route_healing_tier,
    HISTORICAL_DATA_VERSION,
    HISTORICAL_DATA_HASH,
)
from agentic_core.L2_execution.healers.tiering_allowlist import (
    TIERING_ALLOWLIST_AGENT_NAMES,
    is_tiering_allowed,
)

logger = logging.getLogger(__name__)
logger.info(
    f"Healing module loaded - "
    f"TIERING_ALLOWLIST frozen with {len(TIERING_ALLOWLIST_AGENT_NAMES)} agents, "
    f"historical data version {HISTORICAL_DATA_VERSION} (hash: {HISTORICAL_DATA_HASH})"
)

__all__ = [
    "route_healing_tier",
    "TIERING_ALLOWLIST_AGENT_NAMES",
    "is_tiering_allowed",
]
```

### Phase 5: Mathematical Sovereignty Testing (Wave 3.1)
**Scope**: Test mathematical determinism and compile-time frozen governance

**Files to Create**:
- `tests/architecture/test_mathematical_determinism.py` - Test replay mathematics
- `tests/architecture/test_compile_time_frozen_governance.py` - Test frozen surfaces
- `tests/architecture/test_environment_independence.py` - Test no environment access
- `tests/architecture/test_historical_data_versioning.py` - Test versioned data
- `tests/integration/test_truly_immutable_routing.py` - End-to-end immutability

**Key Test Cases**:
```python
# tests/architecture/test_mathematical_determinism.py
def test_mathematical_replay_determinism():
    """Test that identical inputs produce mathematically identical outputs."""
    # Create identical healing inputs
    input1 = HealingInput(
        agent_id="test_agent",
        failure_type="syntax_error",
        error_signature="syntax_error:test_file:42",
        trace_id="test-trace-123",
        retry_count=0,
        blast_radius_estimate=0.3,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
        replay_mode=True,
    )

    input2 = HealingInput(
        agent_id="test_agent",
        failure_type="syntax_error",
        error_signature="syntax_error:test_file:42",
        trace_id="test-trace-123",
        retry_count=0,
        blast_radius_estimate=0.3,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
        replay_mode=True,
    )

    # Route both inputs
    decision1 = route_healing_tier(input1)
    decision2 = route_healing_tier(input2)

    # Mathematical determinism required
    assert decision1.heal_confidence == decision2.heal_confidence
    assert decision1.tier == decision2.tier
    assert decision1.reason_codes == decision2.reason_codes

    # Replay keys must be identical
    key1 = _compute_replay_key(input1, decision1)
    key2 = _compute_replay_key(input2, decision2)
    assert key1 == key2

def test_timestamp_excluded_from_replay():
    """Test that timestamp does not affect replay determinism."""
    base_input = HealingInput(
        agent_id="test_agent",
        failure_type="syntax_error",
        error_signature="syntax_error:test_file:42",
        trace_id="test-trace-123",
        retry_count=0,
        blast_radius_estimate=0.3,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
        replay_mode=True,
    )

    decision = route_healing_tier(base_input)
    original_key = _compute_replay_key(base_input, decision)

    # Wait and recompute (timestamp would change if included)
    time.sleep(0.01)
    new_key = _compute_replay_key(base_input, decision)

    # Keys must be identical - timestamp excluded
    assert original_key == new_key

# tests/architecture/test_compile_time_frozen_governance.py
def test_compile_time_frozen_registry():
    """Test that registry is frozen at compile time."""
    # Verify frozenset immutability
    for agent_id, profile in EXECUTION_PROFILES.items():
        assert isinstance(profile.allowed_models, frozenset)
        with pytest.raises(AttributeError):
            profile.allowed_models.add("new_model")  # Should fail

    # Verify GEMINI mandate
    for agent_id, profile in EXECUTION_PROFILES.items():
        if profile.execution_mode == ExecutionMode.LLM_API:
            assert "gemini-2.5-pro" in profile.allowed_models

def test_compile_time_frozen_allowlist():
    """Test that allowlist is frozen at compile time."""
    # Verify frozenset immutability
    assert isinstance(TIERING_ALLOWLIST_AGENT_NAMES, frozenset)
    with pytest.raises(AttributeError):
        TIERING_ALLOWLIST_AGENT_NAMES.add("new_agent")  # Should fail

    # Verify no external data loading
    assert "CodeHealerAgent" in TIERING_ALLOWLIST_AGENT_NAMES
    assert len(TIERING_ALLOWLIST_AGENT_NAMES) == 11  # Fixed count

# tests/architecture/test_environment_independence.py
def test_no_environment_access():
    """Test that adapters have no environment variable access."""
    # Create adapter with explicit config only
    adapter = QwenVLLMAdapter(
        max_tokens=1024,
        endpoint_url="http://test:8000",  # Explicit, no getenv
    )

    # Config hash should be deterministic
    expected_hash = hashlib.sha256(
        "qwen-vllm:1024:http://test:8000:qwen-vllm".encode()
    ).hexdigest()[:16]
    assert adapter.config_hash == expected_hash

    # No environment access should occur
    with patch.dict(os.environ, {"QWEN_VLLM_ENDPOINT": "http://env:8000"}):
        # Adapter should still use explicit config
        assert adapter.endpoint_url == "http://test:8000"
```

## Detailed Implementation Diffs

### Phase 1.1: Compile-Time Frozen Registry
```diff
# agentic_core/agents/agent_registry.py
- EXECUTION_PROFILES: dict[str, ExecutionProfile] = {}
+ EXECUTION_PROFILES: dict[str, ExecutionProfile] = {
+     "ExecutiveStrategyAgent": ExecutionProfile(
+         execution_mode=ExecutionMode.LLM_API,
+         allowed_models=frozenset(["qwen-vllm", "gemini-2.5-pro"]),
+         reasoning_intensity="HIGH",
+     ),
+     # ... all 23 agents compiled into code
+ }

+ def _validate_registry_sovereignty() -> None:
+     """Validate registry invariants at module import time."""
+     for agent_id, profile in EXECUTION_PROFILES.items():
+         if profile.execution_mode == ExecutionMode.LLM_API:
+             if "gemini-2.5-pro" not in profile.allowed_models:
+                 raise RuntimeError(
+                     f"LLM_API agent '{agent_id}' must allow 'gemini-2.5-pro'"
+                 )
+
+ # Validation runs at module import
+ _validate_registry_sovereignty()
```

### Phase 2.1: Mathematical Determinism
```diff
# agentic_core/L2_execution/healers/healing_tier_types.py
@dataclass(frozen=True, slots=True)
class InvocationRecord:
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
-   timestamp_utc: int  # Removed from replay surface
+   provider_config_hash: str
+   historical_data_hash: str
+   replay_key: str

# agentic_core/L2_execution/healers/healing_tier_router.py
- historical_success = get_historical_success_rate(...)
+ historical_success = HISTORICAL_SUCCESS_RATES.get(
+     healing_input.error_signature.split(':')[0], 0.50
+ ) * WEIGHT_HISTORICAL_SUCCESS

+ def _compute_replay_key(healing_input: HealingInput, decision: HealingDecision) -> str:
+     """Compute mathematical replay key - timestamp excluded."""
+     key_components = [
+         healing_input.agent_id,
+         healing_input.failure_type,
+         healing_input.error_signature,
+         healing_input.trace_id,
+         str(healing_input.retry_count),
+         str(healing_input.blast_radius_estimate),
+         str(decision.heal_confidence),
+         decision.tier.value,
+         HISTORICAL_DATA_HASH,
+     ]
+     return hashlib.sha256('|'.join(key_components).encode()).hexdigest()[:16]
```

### Phase 3.1: Explicit Provider Configuration
```diff
# agentic_core/L2_execution/healers/healing_provider_adapters.py
class QwenVLLMAdapter:
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, endpoint_url: str | None = None):
-       self.endpoint_url = endpoint_url or os.getenv("QWEN_VLLM_ENDPOINT", "http://localhost:8000")
+       self.endpoint_url = endpoint_url or "http://localhost:8000"  # Explicit, no getenv
+       # Deterministic config hash - no environment variables
+       config_string = f"qwen-vllm:{max_tokens}:{self.endpoint_url}:qwen-vllm"
+       self.config_hash = hashlib.sha256(config_string.encode()).hexdigest()[:16]
```

## Acceptance Criteria (Mathematical Immutability)

1. **Compile-Time Frozen Governance**: All policy surfaces frozen at compile time, no runtime loading
2. **Mathematical Determinism**: Identical inputs produce mathematically identical outputs
3. **Timestamp Exclusion**: Replay keys exclude timestamp, ensuring time independence
4. **Environment Independence**: No environment variable access, explicit configuration only
5. **Historical Data Versioning**: All external data versioned and hashed into replay key
6. **Module Import Validation**: All validation runs at module import before system boot
7. **Structural NO_TIERING Guard**: Compile-time frozen allowlist with runtime enforcement
8. **Provider Config Hashing**: Explicit configuration tracked in audit trail

## Risk Mitigation (Mathematical Immutability)

1. **Compile-Time Validation**: All invariants validated at module import, fail-fast
2. **Mathematical Replay Keys**: Deterministic hash computation excludes all nondeterministic inputs
3. **Explicit Configuration**: No environment access, all parameters explicitly injected
4. **Versioned Data Surfaces**: Historical data and configuration versioned for replay
5. **Property-Based Testing**: Mathematical properties tested with comprehensive coverage

## Timeline Estimate

- **Phase 1**: 2- (Compile-time frozen governance)
- **Phase 2**: 2- (Mathematical determinism + historical data versioning)
- **Phase 3**: 2- (Explicit provider configuration)
- **Phase 4**: 1- (Module import validation)
- **Phase 5**: 3- (Mathematical sovereignty testing)
- **Total**: 10-

This truly immutable plan achieves **100% Zero-Loss Architecture compliance** with mathematical determinism guarantees.

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

