# LLM Routing Final Converged Plan: Classification, Hardening, and Implementation

Perform a comprehensive agent classification scan, then implement a hardened LLM routing architecture with authority separation, L4-anchored policy, and deterministic defaults.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

This plan consolidates all previous work into a single implementation path:
1. **Phase 0**: Scan and classify all 200+ agents for LLM healing needs
2. **Phase 1-2**: Implement hardened gateway with split generation/healing paths
3. **Phase 3-6**: Apply classifications, migrate direct callers, enforce with CI

---

## Phase 0 — Agent Classification Scan (CRITICAL)

### 0.1 Scan Scope
```python
# Total agents to analyze:
- agentic_core/*Agent.py: 97 agents
- apps_rg/engines/*.py: 48 engines
- apps_lic/*Agent.py: 44 agents (mostly deprecated)
- apps_shared/*Agent.py: 11 agents
```

### 0.2 Classification Matrix

| Agent Type | LLM Healing? | ReasoningClass | Rationale |
|------------|--------------|---------------|-----------|
| Syntax fixers | NO | DETERMINISTIC | Simple regex/AST fixes |
| Structure validators | NO | DETERMINISTIC | Rule-based checks |
| Complex orchestrators | YES | STRATEGIC/ORCHESTRATOR | Need reasoning for coordination |
| Content generators | YES | LIGHT/STRATEGIC | Production generation |
| Threat analyzers | YES | STRATEGIC | Complex pattern recognition |
| File movers | NO | DETERMINISTIC | Simple deterministic ops |

### 0.3 Expected Results
- **agentic_core**: ~30 need LLM healing, ~67 deterministic
- **apps_rg**: ~5 need LLM generation, ~43 no LLM
- **apps_lic**: Mostly deprecated stubs
- **apps_shared**: Infrastructure only, no LLM

---

## Phase 1 — Core Infrastructure

### 1.1 L4-Anchored LLMRoutingPolicy
```python
# agentic_core/config/llm_routing_policy.py
@dataclass(frozen=True)
class LLMRoutingPolicy:
    # Generation routing
    generation_models: dict[ReasoningClass, str]
    generation_budgets: dict[ReasoningClass, int]

    # Healing routing (dynamic from L4)
    healing_confidence_x: float  # Read from L4 state
    healing_confidence_y: float  # Read from L4 state
    healing_max_retries: int

    @property
    def policy_hash(self) -> str:
        """SHA256 for L4 Merkle root anchoring"""
        return sha256(self.canonical_json())
```

### 1.2 Split Gateway Architecture
```python
class SovereignLLMGateway:
    async def route_generation(self, prompt: str, reasoning_class: ReasoningClass,
                             trace_id: str, replay_mode: bool = True) -> str:
        # Production inference: deterministic, budget enforced

    async def route_healing(self, failure_context: HealingInput,
                           trace_id: str) -> str:
        # Failure recovery: stochastic allowed, retry escalation
```

### 1.3 ReasoningClass Enum
```python
class ReasoningClass(Enum):
    DETERMINISTIC = 0   # No LLM
    LIGHT = 1           # Qwen, temp=0
    STRATEGIC = 2       # Gemini-2.5-pro, temp=0
    ORCHESTRATOR = 3    # Gemini-2.5-pro, temp=0 (deterministic!)
    HEALER = 4          # Healing path only
```

---

## Phase 2 — Determinism & Replay

### 2.1 Default Parameters (Generation)
```python
generation_params = {
    "temperature": 0.0,
    "top_p": 0.0,
    "replay_mode": True,
}
```

### 2.2 Stochastic Opt-In
```python
class SovereignBaseAgent:
    ALLOW_STOCHASTIC: bool = False  # Default deterministic
```

### 2.3 Canonical Replay Key
```python
replay_key = sha256(
    trace_id + prompt_hash + model_id + str(temperature) +
    str(top_p) + response_hash + provider_version +
    system_prompt_hash
)
```

---

## Phase 3 — Fix apps_rg Broken Path

### 3.1 Implement call_llm() in MCPOperationMixin
```python
class MCPOperationMixin:
    def __init__(self, gateway: SovereignLLMGateway | None = None):
        self.gateway = gateway or SovereignLLMGateway()

    async def call_llm(self, prompt: str, *,
                      reasoning_class: ReasoningClass | None = None,
                      trace_id: str | None = None) -> str:
        cls = reasoning_class or getattr(self, "AGENT_REASONING_CLASS", ReasoningClass.LIGHT)
        tid = trace_id or self._generate_trace_id()
        return await self.gateway.route_generation(prompt, cls, tid)
```

### 3.2 Configure apps_rg Engines
- `BulletGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.LIGHT`
- `MessageGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC`

---

## Phase 4 — Apply Classification Results

### 4.1 Update Agent Classes
Based on scan results from Phase 0:

```python
# Examples
class FissionManagerAgent(SovereignBaseAgent):
    AGENT_REASONING_CLASS = ReasoningClass.ORCHESTRATOR  # Complex orchestration

class NamingAgent(SovereignBaseAgent):
    AGENT_REASONING_CLASS = ReasoningClass.DETERMINISTIC  # Simple rules

class BulletGenerationTask(BaseRGEngine):
    AGENT_REASONING_CLASS = ReasoningClass.LIGHT  # Fast generation
```

### 4.2 Healing vs Generation Decision Matrix

| Use Case | Path | ReasoningClass | Notes |
|----------|------|---------------|-------|
| Fix syntax error | route_healing() | HEALER | Only for actual healing |
| Generate content | route_generation() | LIGHT/STRATEGIC | Production calls |
| Complex orchestration | route_generation() | ORCHESTRATOR | Planning/coordination |
| Simple validation | None | DETERMINISTIC | No LLM needed |

---

## Phase 5 — Migration & Deprecation

### 5.1 Migrate 3 Direct Callers
- `FissionManagerAgent`: Use `route_generation(reasoning_class=ORCHESTRATOR)`
- `CognitiveDispositionAgent`: Use `route_healing()` (actual healing path)
- `StructuredEngineAgent`: Use `route_generation(reasoning_class=STRATEGIC)`

### 5.2 Deprecate Direct Access
- Mark `llm_generate()` as `@deprecated` in `LLMProviderMixin`
- Add CI ban on direct usage

### 5.3 Wire apps_lic Stub
- Add placeholder `call_llm()` to prevent future bypass

---

## Phase 6 — CI Enforcement

### 6.1 Comprehensive Compliance Check
```python
# ops_scripts/ci/check_llm_routing_compliance.py
checks = [
    "all_agents_have_reasoning_class",
    "no_hardcoded_model_names",
    "no_direct_llm_generate",
    "no_temperature_outside_gateway",
    "no_top_p_outside_gateway",
    "no_provider_imports_in_agents",
    "all_gateway_calls_have_trace_id",
]
```

### 6.2 Budget Enforcement
```python
if estimated_tokens > policy.generation_budgets[reasoning_class]:
    raise BudgetExceededError(...)
```

---

## Implementation Sequence

1. **Run classification scan** → Generate agent classification table
2. **Review classifications** → Manual validation of edge cases
3. **Implement infrastructure** → Gateway, policy, L4 anchoring
4. **Activate CI enforcement** → Prevent drift during migration
5. **Apply classifications** → Update agent classes
6. **Migrate direct callers** → 3 specific agents
7. **Decompose old configs** → HealingTierConfig, RoutingTier

---

## Success Criteria

1. ✓ All 200+ agents classified with documented rationale
2. ✓ LLM healing only where genuinely needed (~30 agents)
3. ✓ Deterministic healing for simple cases (~67 agents)
4. ✓ Production generation properly separated (~5 apps_rg engines)
5. ✓ Policy hash anchored in L4 Merkle root
6. ✓ Budget enforcement inside gateway
7. ✓ CI enforces all invariants
8. ✓ Zero cost from unnecessary LLM calls

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Authority escalation | Separate generation/healing paths |
| Replay nondeterminism | Default temp=0, replay_mode=True |
| Policy drift | L4 hash anchoring + CI enforcement |
| Cost explosion | Budget enforcement + LIGHT default |
| apps_rg broken | Gateway injection + trace IDs |
| Future bypass | Stub wiring + CI bans |
| Threshold stagnation | Dynamic L4 state reads |

---

## Final Architecture Compliance

| Invariant | Implementation |
|-----------|----------------|
| L0 authority | Separated gateway methods, caller validation |
| L2 replay | Canonical replay_key with full parameters |
| L4 anchoring | policy_hash in Merkle root |
| L6 adaptation | Dynamic healing thresholds from state |

The architecture is governance-complete and ready for implementation.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

