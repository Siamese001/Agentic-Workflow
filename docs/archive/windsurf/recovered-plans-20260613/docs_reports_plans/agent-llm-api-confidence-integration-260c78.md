# Agent LLM API Integration & Confidence-Based Healing Plan

This plan implements a comprehensive system to wire agents in apps_*, agentic_core, and other repo folders to call LLM APIs (Qwen or Gemini) based on confidence levels, using the agent_2x2_inventory.json as the Single Source of Truth (SSOT) for determining which agents need LLM API calls vs deterministic healing.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

### Existing Infrastructure
- **SovereignLLMGateway**: Unified LLM gateway supporting OpenAI, Anthropic, and Google providers
- **Healing Tier Router**: Centralized router with LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO tiers
- **Agent Registry**: Contains execution profiles with LLM_API vs DETERMINISTIC modes
- **Confidence Scoring**: heal_confidence thresholds (X=0.75, Y=0.40) for tier selection
- **Agent Inventory**: 23 total agents across apps_lic (8), apps_rg (8), and SSOT registry (7)

### Key Findings
1. **SSOT Registry Agents**: 7 agents with defined execution modes
   - LLM_API: ExecutiveStrategyAgent, ResumeAssemblyAgent, SovereignLLMGateway
   - DETERMINISTIC: ClassificationComplianceHealer, HybridRetrieverConfig, UnifiedWorkflowConfig, ValidationOrchestrator

2. **Missing Integration**: apps_* agents (16 total) lack execution mode definitions
3. **Confidence Gaps**: No systematic confidence-based routing for all agents
4. **Provider Mismatch**: Current gateway supports OpenAI/Anthropic/Google, but plan specifies Qwen/Gemini

## Implementation Plan

### Phase 1: SSOT Enhancement & Agent Classification
**Scope**: Extend agent_2x2_inventory.json and create execution mode mappings

**Files to Modify**:
- `artifacts/discovery/agent_2x2_inventory.json` - Add execution_mode for all 23 agents
- `agentic_core/agents/agent_registry.py` - Add confidence-based execution mode resolution
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` - Add Qwen provider support

**Key Changes**:
1. Enumerate all 23 agents with execution_mode (LLM_API vs DETERMINISTIC)
2. Add confidence_threshold mappings per agent type
3. Integrate Qwen provider alongside existing Gemini support
4. Create agent-to-provider mapping based on reasoning_intensity

### Phase 2: Confidence-Based Routing Enhancement
**Scope**: Enhance healing tier router to use agent-specific confidence thresholds

**Files to Modify**:
- `agentic_core/L2_execution/healers/healing_tier_router.py` - Agent-aware confidence scoring
- `agentic_core/L2_execution/healers/healing_tier_config.py` - Per-agent threshold configuration
- `agentic_core/L2_execution/types/heal_contract_types.py` - Add agent execution mode context

**Key Changes**:
1. Incorporate agent execution profiles into confidence calculation
2. Create agent-specific confidence thresholds (HIGH: 0.6+, MEDIUM: 0.4+, LOW: deterministic)
3. Add provider selection logic (Qwen for general tasks, Gemini for complex reasoning)
4. Enhance audit trail to include agent execution mode decisions

### Phase 3: apps_* Agent Integration
**Scope**: Wire apps_lic and apps_rg agents to use confidence-based LLM API calls

**Files to Modify**:
- `apps_lic/config/agent_specs.json` - Add execution_mode and confidence_threshold
- `apps_rg/config/agent_spec_config.py` - Add execution_mode field to AgentSpec
- `apps_lic/enforcement/ExecutiveStrategyAgent.py` - Confidence-based API routing
- `apps_rg/enforcement/ResumeAssemblyAgent.py` - Provider selection logic

**Key Changes**:
1. Add execution_mode field to all 16 apps_* agents
2. Implement confidence-based provider selection in agent execution
3. Add fallback logic from LLM_API to deterministic healing
4. Create agent-specific confidence calibration based on task complexity

### Phase 4: Deterministic Healing Integration
**Scope**: Ensure deterministic agents have proper healing pathways

**Files to Modify**:
- `agentic_core/L2_execution/healers/classification_compliance_healer.py` - Pure deterministic logic
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py` - Deterministic fallback routing
- `agentic_core/L2_execution/healers/hierarchy_compliance_healer.py` - Rule-based healing

**Key Changes**:
1. Strengthen deterministic healing capabilities for non-LLM agents
2. Add rule-based confidence scoring for deterministic tasks
3. Create hybrid healing paths (deterministic → LLM fallback)
4. Implement deterministic-only healing for low-risk violations

### Phase 5: Testing & Validation
**Scope**: Comprehensive test coverage for confidence-based routing

**Files to Create**:
- `tests/integration/test_confidence_based_llm_routing.py` - End-to-end routing tests
- `tests/unit/test_agent_execution_mode_resolution.py` - Registry resolution tests
- `tests/unit/test_qwen_provider_integration.py` - Qwen provider tests
- `tests/architecture/test_deterministic_healing_integrity.py` - Deterministic path validation

**Key Changes**:
1. Test all 23 agents with correct execution mode resolution
2. Validate confidence thresholds trigger appropriate healing tiers
3. Test provider selection (Qwen vs Gemini) based on agent profiles
4. Verify deterministic agents never trigger LLM API calls

## Detailed Implementation Diffs

### Phase 1.1: Enhanced Agent Inventory
```json
{
  "apps_lic_spec_keys": [...],
  "apps_rg_spec_keys": [...],
  "counts": {...},
  "ssot_registry_agents": [
    {
      "agent_id": "ExecutiveStrategyAgent",
      "execution_mode": "LLM_API",
      "confidence_threshold": 0.6,
      "preferred_provider": "qwen",
      "fallback_provider": "gemini",
      "reasoning_intensity": "HIGH"
    },
    {
      "agent_id": "ClassificationComplianceHealer",
      "execution_mode": "DETERMINISTIC",
      "confidence_threshold": null,
      "healing_strategy": "rule_based"
    }
  ],
  "apps_lic_agents": [
    {
      "agent_id": "profile_analysis_agent",
      "execution_mode": "LLM_API",
      "confidence_threshold": 0.5,
      "preferred_provider": "qwen"
    }
  ],
  "apps_rg_agents": [...]
}
```

### Phase 2.1: Agent-Aware Confidence Routing
```python
def calculate_heal_confidence(
    healing_input: HealingInput,
    agent_execution_profile: ExecutionProfile | None = None,
) -> float:
    """Calculate confidence score with agent-specific adjustments."""
    base_score = calculate_base_confidence(healing_input)

    if agent_execution_profile:
        if agent_execution_profile.execution_mode == ExecutionMode.DETERMINISTIC:
            # Deterministic agents get lower confidence for LLM healing
            base_score *= 0.5
        elif agent_execution_profile.reasoning_intensity == "HIGH":
            # High reasoning agents get higher confidence for complex tasks
            base_score *= 1.2

    return min(1.0, base_score)
```

### Phase 3.1: Qwen Provider Integration
```python
# In SovereignLLMGateway.py
from data.sdks_mcps.client_wrappers import create_qwen_client

def _get_provider_client(self, provider: Provider):
    if provider == "qwen":
        if self._qwen_client is None:
            self._qwen_client = create_qwen_client()
        return self._qwen_client
    # ... existing provider logic
```

### Phase 4.1: Deterministic Healing Strengthening
```python
class DeterministicHealingPath:
    """Pure deterministic healing for non-LLM agents."""

    def should_use_llm_healing(self, agent_id: str, failure_type: str) -> bool:
        """Deterministic agents should never use LLM healing."""
        profile = get_profile(agent_id)
        return profile.execution_mode == ExecutionMode.LLM_API
```

## Acceptance Criteria

1. **All 23 agents** have defined execution modes in agent inventory
2. **Confidence-based routing** works for all agents (LLM_API: 0.6+, deterministic: rule-based)
3. **Qwen provider** integrated and functional alongside Gemini
4. **Deterministic agents** never trigger LLM API calls
5. **Fallback paths** exist from LLM_API to deterministic healing
6. **Comprehensive test coverage** validates all routing scenarios
7. **Performance impact** minimal (confidence calculation < 10ms)
8. **Audit trail** captures all routing decisions with confidence scores

## Risk Mitigation

1. **Provider Availability**: Implement fallback chains (Qwen → Gemini → deterministic)
2. **Confidence Calibration**: Start with conservative thresholds, adjust based on success rates
3. **Performance Impact**: Cache execution profiles and confidence calculations
4. **Testing Gaps**: Use property-based testing for confidence edge cases
5. **Rollback Strategy**: Feature flags for new routing logic

## Timeline Estimate

- **Phase 1**: 2-TIME_REMOVED (SSOT enhancement + Qwen integration)
- **Phase 2**: 2-TIME_REMOVED (Confidence routing enhancement)
- **Phase 3**: 3-TIME_REMOVED (apps_* agent integration)
- **Phase 4**: 2-TIME_REMOVED (Deterministic healing integration)
- **Phase 5**: 2-TIME_REMOVED (Testing & validation)
- **Total**: 11-TIME_REMOVED

This plan ensures systematic, confidence-based LLM API integration across all agents while maintaining the integrity of deterministic healing pathways.

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

