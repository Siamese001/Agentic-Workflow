---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-converged-a1b2c3.md'
original_relative_path: 'llm-routing-converged-a1b2c3.md'
source_sha256: de6c9f9564f63f9168917dd06427b21d2e319dfcb4fb0bf0126a896bd4192bab
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing Converged Spec: Authority-Complete, Deterministic by Default

Implement a governance-complete LLM routing architecture with strict authority separation, L4-anchored policy, and deterministic replay guarantees that align with L0/L2/L4/L6 invariants.

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


## Core Architectural Principles

1. **Authority separation**: `route_generation()` (production) vs `route_healing()` (failure recovery)
2. **Deterministic by default**: All calls enforce `temp=0, top_p=0, replay_mode=True`
3. **L4-anchored policy**: `LLMRoutingPolicy` hashes into Merkle root for cryptographic verification
4. **Budget enforcement**: Token limits enforced inside gateway, not caller
5. **No drift**: CI bans all sampling parameters and provider imports outside gateway

---

## 1. Gateway Architecture

```
SovereignLLMGateway
    ├── route_generation(intent, reasoning_class, trace_id, replay_mode=True)
    │   └── Deterministic by default, budget enforced, no retry escalation
    └── route_healing(failure_context, confidence, retries, trace_id)
        └── Stochastic allowed, retry escalation, L2-coupled only
```

### Authority constraints
- `route_healing()` only callable from L2 Healer or agents with `reasoning_class=HEALER`
- Generation agents cannot access healing path (prevents authority escalation)

---

## 2. ReasoningClass Enum (Final)

```python
class ReasoningClass(Enum):
    DETERMINISTIC = 0   # No LLM
    LIGHT = 1           # Qwen, temp=0
    STRATEGIC = 2       # Gemini-2.5-pro, temp=0
    ORCHESTRATOR = 3    # Gemini-2.5-pro, temp=0 (deterministic!)
    HEALER = 4          # Healing path only
```

**Critical**: ORCHESTRATOR is deterministic by default. Stochastic requires explicit `ALLOW_STOCHASTIC=True`.

---

## 3. L4-Anchored LLMRoutingPolicy

```python
# agentic_core/config/llm_routing_policy.py
@dataclass(frozen=True)
class LLMRoutingPolicy:
    # Generation routing
    generation_models: dict[ReasoningClass, str]
    generation_budgets: dict[ReasoningClass, int]  # Enforced in gateway

    # Healing routing (dynamic from L4)
    healing_confidence_x: float  # Read from L4 state
    healing_confidence_y: float  # Read from L4 state
    healing_max_retries: int

    # Model registry
    model_qwen_id: str = "qwen2.5-coder-32b-instruct"
    model_gemini_pro_id: str = "gemini-2.5-pro"

    @property
    def policy_hash(self) -> str:
        """SHA256 hash for L4 Merkle root anchoring."""
        return sha256(self.canonical_json())
```

### L4 Integration
- L0 stamps `policy_hash` onto InstructionPacket
- L2 validates policy hash before execution
- ExecutionTrace stores policy hash for audit

---

## 4. Determinism & Replay Contract

### Default parameters (generation)
```python
generation_params = {
    "temperature": 0.0,
    "top_p": 0.0,
    "replay_mode": True,
}
```

### Stochastic opt-in
```python
class SovereignBaseAgent:
    ALLOW_STOCHASTIC: bool = False  # Default deterministic

    def _get_generation_params(self) -> dict:
        if not self.ALLOW_STOCHASTIC:
            return {"temperature": 0.0, "top_p": 0.0, "replay_mode": True}
        else:
            return {"temperature": 0.7, "top_p": 0.9, "replay_mode": False}
```

### Canonical replay_key
```python
replay_key = sha256(
    trace_id +
    prompt_hash +
    model_id +
    str(temperature) +
    str(top_p) +
    response_hash +
    provider_version +
    system_prompt_hash
)
```

---

## 5. Implementation Steps

### Phase 1 — Core Infrastructure

**Step 1.1**: Create L4-anchored `LLMRoutingPolicy`
- File: `agentic_core/config/llm_routing_policy.py`
- Include `policy_hash` property for Merkle anchoring

**Step 1.2**: Split gateway with authority enforcement
```python
class SovereignLLMGateway:
    async def route_generation(self, prompt: str, reasoning_class: ReasoningClass,
                             trace_id: str, replay_mode: bool = True) -> str:
        # Enforce budget, deterministic defaults, no healing path

    async def route_healing(self, failure_context: HealingInput,
                           trace_id: str) -> str:
        # Check caller authority, allow stochastic, retry escalation
```

**Step 1.3**: Add deterministic defaults to base agent
- `ALLOW_STOCHASTIC = False` by default
- `AGENT_REASONING_CLASS = ReasoningClass.DETERMINISTIC`

### Phase 2 — Fix apps_rg Broken Path

**Step 2.1**: Implement `call_llm()` with gateway injection
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

**Step 2.2**: Configure apps_rg engines
- `BulletGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.LIGHT`
- `MessageGenerationTask`: `AGENT_REASONING_CLASS = ReasoningClass.STRATEGIC`

### Phase 3 — Determinism Enforcement

**Step 3.1**: Expand replay logging
```python
CanonicalLog = {
    "trace_id": str,
    "prompt_hash": str,
    "model_id": str,
    "provider_version": str,
    "temperature": float,
    "top_p": float,
    "system_prompt_hash": str,
    "response_hash": str,
    "token_count": int,
    "policy_hash": str,
    "replay_key": str,
}
```

**Step 3.2**: Add budget enforcement in gateway
```python
if estimated_tokens > policy.generation_budgets[reasoning_class]:
    raise BudgetExceededError(
        f"Token estimate {estimated_tokens} exceeds budget "
        f"{policy.generation_budgets[reasoning_class]}"
    )
```

### Phase 4 — Migration & Deprecation

**Step 4.1**: Migrate 3 direct callers
- All go through `route_generation()` with appropriate reasoning class
- Deprecate direct `llm_generate()` with `@deprecated`

**Step 4.2**: Wire apps_lic stub
- Add placeholder `call_llm()` to prevent future bypass

### Phase 5 — CI Enforcement

**Step 5.1**: Comprehensive compliance check
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

**Step 5.2**: Add to CI workflow
- Fail PR if any violation detected

---

## 6. Dynamic Healing Thresholds

Healing thresholds are NOT static:

```python
# Read from L4 state store
healing_state = l4_state_store.get("healing_policy")
confidence_x = healing_state.confidence_x  # Adapts over time
confidence_y = healing_state.confidence_y  # Adapts over time
```

This enables L6 meta-learning to adjust thresholds based on success rates.

---

## 7. Migration Sequencing

1. **Deploy infrastructure** (policy, gateway, CI)
2. **Activate CI enforcement**
3. **Migrate agents** (apps_rg first, then agentic_core)
4. **Decompose old configs** (HealingTierConfig, RoutingTier)

Critical: CI must be active before migration to prevent drift re-entry.

---

## 8. Success Criteria

1. ✓ All LLM calls through single gateway with authority separation
2. ✓ Deterministic by default with explicit stochastic opt-in
3. ✓ Policy hash anchored in L4 Merkle root
4. ✓ Budget enforcement inside gateway
5. ✓ apps_rg engines functional with trace IDs
6. ✓ Zero hardcoded models or sampling params in agents
7. ✓ CI enforces all invariants
8. ✓ Healing thresholds adapt from L4 state

---

## 9. Risk Matrix

| Risk | Mitigation | Status |
|------|------------|--------|
| Authority escalation | Separate generation/healing paths | ✓ |
| Replay nondeterminism | Default temp=0, replay_mode=True | ✓ |
| Policy drift | L4 hash anchoring + CI enforcement | ✓ |
| Cost explosion | Budget enforcement + LIGHT default | ✓ |
| apps_rg broken | Gateway injection + trace IDs | ✓ |
| Future bypass | Stub wiring + CI bans | ✓ |
| Threshold stagnation | Dynamic L4 state reads | ✓ |

---

## 10. Final Architecture Compliance

| Invariant | Implementation |
|-----------|----------------|
| L0 authority | Separated gateway methods, caller validation |
| L2 replay | Canonical replay_key with full parameters |
| L4 anchoring | policy_hash in Merkle root |
| L6 adaptation | Dynamic healing thresholds from state |

The architecture is now governance-complete and ready for implementation.

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

