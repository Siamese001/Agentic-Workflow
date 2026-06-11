---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hardened-agent-llm-api-sovereign-healing-260c78.md'
original_relative_path: 'hardened-agent-llm-api-sovereign-healing-260c78.md'
source_sha256: b601bc03e4066f32d1be96f1d89cad644e7ddeaa02cf817ac1ab4a8610d4d441
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hardened Agent LLM API Integration & Sovereign Healing Plan

This plan implements a sovereign, zero-loss architecture for agent LLM API integration using centralized tier routing through L2.3 choke point, preserving deterministic healing boundaries and escalation allowlists.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Architectural Foundations

### Core Invariants (Non-Negotiable)
- **Single Tier Choke Point**: Only `route_healing_tier()` may select LOCAL/QWEN/GEMINI tiers
- **Provider Selection Sealing**: Models selectable only via HealingProviderInvoker protocol seam
- **Deterministic Agent Protection**: DETERMINISTIC execution mode = structurally incapable of LLM escalation
- **Escalation Allowlist Guard**: HEALER_ESCALATION_ALLOWLIST + needs_llm_escalation=True required
- **Replay Determinism**: Tier decisions must be replay-identical via deterministic scoring only

### Current Infrastructure Analysis
- **Tiering Allowlist**: 11 YES_TIERING agents, all others are NO_TIERING (emit FailureSignal only)
- **HealingProviderInvoker**: Protocol seam with DefaultHealingProviderInvoker implementation
- **Agent Registry**: ExecutionProfile with execution_mode (LLM_API/DETERMINISTIC) and allowed_models
- **Confidence Bands**: heal_confidence >= 0.75 → LOCAL, 0.40 ≤ score < 0.75 → QWEN, score < 0.40 → GEMINI
- **Retry Escalation**: retry_count >= 3 forces GEMINI_2_5_PRO (if model allowed)

## Hardened Implementation Plan

### Phase 1: SSOT Registry Clarification (Wave 1.1)
**Scope**: Extend agent_2x2_inventory.json with execution eligibility only

**Files to Modify**:
- `artifacts/discovery/agent_2x2_inventory.json`

**Key Changes**: Add tiering_class and execution_mode without routing logic

```json
{
  "ssot_registry_agents": [
    {
      "agent_id": "ExecutiveStrategyAgent",
      "execution_mode": "LLM_API",
      "tiering_class": "YES_TIERING",
      "allowed_models": ["qwen-vllm", "gemini-2.5-pro"]
    },
    {
      "agent_id": "ClassificationComplianceHealer",
      "execution_mode": "DETERMINISTIC",
      "tiering_class": "NO_TIERING",
      "allowed_models": []
    }
  ],
  "apps_lic_agents": [
    {
      "agent_id": "profile_analysis_agent",
      "execution_mode": "LLM_API",
      "tiering_class": "NO_TIERING",
      "allowed_models": ["qwen-vllm", "gemini-2.5-pro"]
    }
  ]
}
```

**Architectural Compliance**: No confidence_threshold, provider_preference, or routing logic in inventory.

### Phase 2: L2.3 Router Sovereignty Hardening (Wave 1.2)
**Scope**: Strengthen centralized tier router with agent profile enforcement

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_router.py`
- `agentic_core/L2_execution/healers/healing_tier_config.py`

**Key Changes**:
1. **Agent Profile Enforcement**: Existing logic already enforces execution_mode constraints
2. **Deterministic Scoring**: Remove any semantic embedding influence on confidence
3. **Model Validation**: Fail-closed validation of allowed_models per agent profile
4. **Escalation Allowlist**: Preserve existing HEALER_ESCALATION_ALLOWLIST + needs_llm_escalation guard

```python
# Enhanced route_healing_tier (preserving existing architecture)
def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Sovereign tier router - ONLY place that selects healing tiers."""

    # Existing agent execution profile enforcement (already hardened)
    profile = get_profile(healing_input.agent_id)
    if not profile.is_llm_allowed():
        # Deterministic agents forced to LOCAL_AGENT only
        return HealingDecision(
            heal_confidence=1.0,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
        )

    # Existing deterministic confidence calculation (no semantic influence)
    heal_confidence, reason_codes = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,
    )

    # Existing retry escalation invariant
    if healing_input.retry_count >= config.max_heal_retries:
        if not profile.can_use_model("gemini-2.5-pro"):
            raise V15HardFailAbort(f"Agent not allowed model gemini-2.5-pro")
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=(*reason_codes, f"retry_count>={config.max_heal_retries}:FORCED_GEMINI"),
        )

    # Existing X/Y band routing with model validation
    if heal_confidence >= config.heal_confidence_x:
        return HealingDecision(heal_confidence=heal_confidence, tier=HealingTier.LOCAL_AGENT, reason_codes=(*reason_codes, f"heal_confidence>={config.heal_confidence_x}:LOCAL_AGENT"))
    elif heal_confidence >= config.heal_confidence_y:
        if not profile.can_use_model("qwen-vllm"):
            raise V15HardFailAbort(f"Agent not allowed model qwen-vllm")
        return HealingDecision(heal_confidence=heal_confidence, tier=HealingTier.QWEN_VLLM, reason_codes=(*reason_codes, f"heal_confidence>={config.heal_confidence_y}:QWEN_VLLM"))
    else:
        if not profile.can_use_model("gemini-2.5-pro"):
            raise V15HardFailAbort(f"Agent not allowed model gemini-2.5-pro")
        return HealingDecision(heal_confidence=heal_confidence, tier=HealingTier.GEMINI_2_5_PRO, reason_codes=(*reason_codes, f"heal_confidence<{config.heal_confidence_y}:GEMINI_2_5_PRO"))
```

### Phase 3: Qwen Provider Integration via Protocol Seam (Wave 2.1)
**Scope**: Add Qwen provider through HealingProviderInvoker protocol

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_provider_adapters.py`
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Key Changes**: Add Qwen adapter following existing protocol pattern

```python
# In healing_provider_adapters.py - following existing pattern
class QwenVLLMAdapter:
    """Qwen/vLLM provider adapter implementing HealingProviderInvoker protocol."""

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
        self.max_tokens = max_tokens
        self._client = None

    def invoke(self, request: GenerationRequest) -> GenerationResponse:
        """Invoke Qwen model via SovereignLLMGateway."""
        gateway = get_llm_gateway()
        return gateway.generate(
            model="qwen-vllm",
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or self.max_tokens,
        )

# In SovereignLLMGateway.py - add Qwen provider support
def _get_provider_client(self, provider: Provider):
    """Get provider client - centralized provider management."""
    if provider == "qwen":
        if self._qwen_client is None:
            # Use existing client wrapper pattern
            from data.sdks_mcps.client_wrappers import create_vllm_client
            self._qwen_client = create_vllm_client()
        return self._qwen_client
    # ... existing provider logic
```

### Phase 4: apps_* Agent Registry Integration (Wave 2.2)
**Scope**: Add all 16 apps_* agents to agent registry with execution profiles

**Files to Modify**:
- `agentic_core/agents/agent_registry.py` (or appropriate registry location)
- `apps_lic/config/agent_specs.json` - Add minimal execution metadata
- `apps_rg/config/agent_spec_config.py` - Add execution_mode field

**Key Changes**: Register agents with execution modes, no routing logic

```python
# Agent registry additions
{
    "profile_analysis_agent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=["qwen-vllm", "gemini-2.5-pro"],
        reasoning_intensity="MEDIUM",
    ),
    "research_agent": ExecutionProfile(
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=["qwen-vllm", "gemini-2.5-pro"],
        reasoning_intensity="HIGH",
    ),
    # ... other apps_* agents
}
```

### Phase 5: Deterministic Agent Sovereignty (Wave 3.1)
**Scope**: Harden deterministic agents to prevent LLM escalation

**Files to Modify**:
- `agentic_core/L2_execution/healers/classification_compliance_healer.py`
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py`

**Key Changes**: Ensure deterministic agents cannot escalate

```python
# In sovereign_healing_engine.py - preserve existing invariants
def can_escalate_to_llm(self, agent_id: str, check_id: str) -> bool:
    """Check if agent can escalate to LLM healing."""
    # Existing escalation allowlist guard
    if check_id not in HEALER_ESCALATION_ALLOWLIST:
        return False

    # Existing agent execution mode guard
    try:
        profile = get_profile(agent_id)
        return profile.is_llm_allowed()  # Only LLM_API agents can escalate
    except KeyError:
        return False  # Unregistered agents cannot escalate
```

### Phase 6: Audit Trail & InvocationRecord Integrity (Wave 3.2)
**Scope**: Ensure complete audit coverage for all tier decisions

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`
- `agentic_core/L2_execution/types/heal_contract_types.py`

**Key Changes**: Preserve existing InvocationRecord structure

```python
# Preserve existing InvocationRecord structure
@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record of healing tier invocation."""
    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    timestamp_utc: int
```

### Phase 7: Comprehensive Testing (Wave 4.1)
**Scope**: Test sovereign architecture compliance

**Files to Create**:
- `tests/architecture/test_sovereign_tier_routing.py` - Test choke point invariants
- `tests/unit/test_agent_execution_profile_enforcement.py` - Test execution mode guards
- `tests/unit/test_qwen_provider_adapter.py` - Test Qwen via protocol seam
- `tests/integration/test_deterministic_agent_sovereignty.py` - Test deterministic isolation

**Key Test Cases**:
1. **Choke Point Test**: Only route_healing_tier() selects tiers
2. **Deterministic Guard Test**: DETERMINISTIC agents never get LLM tiers
3. **Provider Seam Test**: Qwen works only through HealingProviderInvoker
4. **Escalation Allowlist Test**: NO_TIERING agents emit FailureSignal only
5. **Replay Determinism Test**: Same inputs produce same tier decisions

## Detailed File Diffs

### Phase 1.1: Enhanced Agent Inventory
```diff
{
  "ssot_registry_agents": [
    {
      "agent_id": "ExecutiveStrategyAgent",
-     "allowed_models": ["claude-3-sonnet", "gpt-4"],
-     "allowed_providers": ["anthropic", "openai"],
-     "execution_mode": "LLM_API",
-     "policy_version": 1,
-     "reasoning_intensity": "HIGH"
+     "execution_mode": "LLM_API",
+     "tiering_class": "YES_TIERING",
+     "allowed_models": ["qwen-vllm", "gemini-2.5-pro"]
    },
    {
      "agent_id": "ClassificationComplianceHealer",
-     "allowed_models": [],
-     "allowed_providers": [],
-     "execution_mode": "DETERMINISTIC",
-     "policy_version": 1,
-     "reasoning_intensity": "LOW"
+     "execution_mode": "DETERMINISTIC",
+     "tiering_class": "NO_TIERING",
+     "allowed_models": []
    }
  ],
+ "apps_lic_agents": [
+   {
+     "agent_id": "profile_analysis_agent",
+     "execution_mode": "LLM_API",
+     "tiering_class": "NO_TIERING",
+     "allowed_models": ["qwen-vllm", "gemini-2.5-pro"]
+   }
+ ],
+ "apps_rg_agents": [...]
}
```

### Phase 3.1: Qwen Provider Adapter
```diff
# In healing_provider_adapters.py
+ class QwenVLLMAdapter:
+     """Qwen/vLLM provider adapter implementing HealingProviderInvoker protocol."""
+
+     def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
+         self.max_tokens = max_tokens
+         self._client = None
+
+     def invoke(self, request: GenerationRequest) -> GenerationResponse:
+         """Invoke Qwen model via SovereignLLMGateway."""
+         gateway = get_llm_gateway()
+         return gateway.generate(
+             model="qwen-vllm",
+             messages=request.messages,
+             temperature=request.temperature,
+             max_tokens=request.max_tokens or self.max_tokens,
+         )

# In SovereignLLMGateway.py
+ Provider = Literal["openai", "anthropic", "google", "qwen"]

  def _get_provider_client(self, provider: Provider):
      if provider == "qwen":
          if self._qwen_client is None:
              from data.sdks_mcps.client_wrappers import create_vllm_client
              self._qwen_client = create_vllm_client()
          return self._qwen_client
      # ... existing logic
```

### Phase 4.1: Agent Registry Integration
```diff
# In agent registry
+ {
+     "profile_analysis_agent": ExecutionProfile(
+         execution_mode=ExecutionMode.LLM_API,
+         allowed_models=["qwen-vllm", "gemini-2.5-pro"],
+         reasoning_intensity="MEDIUM",
+     ),
+     "research_agent": ExecutionProfile(
+         execution_mode=ExecutionMode.LLM_API,
+         allowed_models=["qwen-vllm", "gemini-2.5-pro"],
+         reasoning_intensity="HIGH",
+     ),
+ }

# In apps_rg/config/agent_spec_config.py
class AgentSpec(BaseModel):
    name: str = Field(..., description="Unique agent identifier")
    module_path: str = Field(..., description="Python path to the engine class")
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    timeout_sec: int = Field(default=30, ge=1)
    criticality: str = Field(default="required", pattern="^(required|optional|best_effort)$")
+   execution_mode: str = Field(default="DETERMINISTIC", pattern="^(LLM_API|DETERMINISTIC)$")
+   tiering_class: str = Field(default="NO_TIERING", pattern="^(YES_TIERING|NO_TIERING)$")
```

## Acceptance Criteria

1. **Sovereign Tier Routing**: Only route_healing_tier() selects tiers (verified by test)
2. **Deterministic Agent Protection**: DETERMINISTIC agents never get LLM tiers (verified by test)
3. **Provider Protocol Seam**: Qwen accessible only through HealingProviderInvoker (verified by test)
4. **Escalation Allowlist Integrity**: HEALER_ESCALATION_ALLOWLIST + needs_llm_escalation enforced (verified by test)
5. **Replay Determinism**: Same inputs produce identical tier decisions (verified by test)
6. **Complete Agent Coverage**: All 23 agents have execution profiles in registry
7. **Model Validation**: Fail-closed validation of allowed_models per agent
8. **Audit Trail Completeness**: Every tier decision produces InvocationRecord

## Risk Mitigation

1. **Architecture Compliance**: All changes preserve existing choke point invariants
2. **Determinism Protection**: No semantic signals influence routing decisions
3. **Test Coverage**: Comprehensive invariant testing prevents regression
4. **Rollback Safety**: Changes are additive only, existing paths preserved
5. **Performance Impact**: Minimal - registry lookup is cached, routing unchanged

## Timeline Estimate

- **Phase 1**: 1- (SSOT clarification)
- **Phase 2**: 1- (Router hardening - mostly preserving existing logic)
- **Phase 3**: 2- (Qwen provider integration)
- **Phase 4**: 2- (apps_* agent registry)
- **Phase 5**: 1- (Deterministic sovereignty - mostly validation)
- **Phase 6**:  (Audit trail - existing structure preserved)
- **Phase 7**: 2- (Comprehensive testing)
- **Total**: 10-

This hardened plan preserves the Zero-Loss Architecture while enabling Qwen integration and comprehensive agent coverage through sovereign tier routing.

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

