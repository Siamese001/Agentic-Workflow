# LLM Routing Hardening: Split Generation vs Healing, Deterministic by Default

Implement a hardened LLM routing architecture with separate paths for production generation and healing, deterministic replay guarantees, and a single source of truth for routing policy.

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


## Core Hardening Requirements

1. **Separate concerns**: `route_generation()` for production inference vs `route_healing()` for failure recovery
2. **Deterministic by default**: All calls enforce replay mode unless explicitly marked stochastic
3. **Single policy source**: One `LLMRoutingPolicy` replaces HealingTierConfig + RoutingTier
4. **Fine-grained reasoning classes**: Enum with 5 levels instead of HIGH/LOW binary
5. **No model literals**: Ban hardcoded model names in agent code

---

## 1. New Architecture: Split Gateway

```
SovereignLLMGateway
    ├── route_generation(intent, reasoning_class, replay_mode)  ← production inference
    └── route_healing(failure_context, confidence, retries)    ← escalation path
```

### Key distinction
- **Generation**: Primary inference path (apps_rg bullet writing, strategic planning)
- **Healing**: Failure recovery path (remediation, error correction)

Both use same underlying providers but with different policies:
- Generation: deterministic, no retry escalation, model selection by reasoning class
- Healing: stochastic, retry escalation, model selection by confidence

---

## 2. Hardened Reasoning Class Enum

```python
class ReasoningClass(Enum):
    DETERMINISTIC = 0   # No LLM
    LIGHT = 1           # Qwen (fast, cheap)
    STRATEGIC = 2       # Gemini-2.5-pro (quality)
    ORCHESTRATOR = 3    # Gemini-2.5-pro with higher budget
    HEALER = 4          # Healing path only
```

Maps to:
- Model tier
- Token budget
- Temperature policy
- Fallback ladder

---

## 3. Single LLMRoutingPolicy

Replace both `HealingTierConfig` and `RoutingTier`:

```python
# agentic_core/config/llm_routing_policy.py
@dataclass(frozen=True)
class LLMRoutingPolicy:
    # Generation routing
    generation_models: dict[ReasoningClass, str]
    generation_budgets: dict[ReasoningClass, int]

    # Healing routing
    healing_confidence_x: float  # LOCAL_AGENT threshold
    healing_confidence_y: float  # QWEN threshold
    healing_max_retries: int

    # Model registry
    model_qwen_id: str = "qwen2.5-coder-32b-instruct"
    model_gemini_pro_id: str = "gemini-2.5-pro"
```

---

## 4. Implementation Steps

### Phase 1 — Structural Foundation

**Step 1.1**: Create `LLMRoutingPolicy` single source of truth
- File: `agentic_core/config/llm_routing_policy.py`
- Deprecates: `HealingTierConfig`, `RoutingTier`

**Step 1.2**: Split gateway methods
- `SovereignLLMGateway.route_generation()` – production
- `SovereignLLMGateway.route_healing()` – failure recovery
- `dispatch_healing()` now calls `route_healing()`

**Step 1.3**: Add `ReasoningClass` enum to `SovereignBaseAgent`
- Default: `AGENT_REASONING_CLASS = ReasoningClass.DETERMINISTIC`
- Replaces string HIGH/LOW

### Phase 2 — Fix apps_rg Broken Path

**Step 2.1**: Implement `call_llm()` in `MCPOperationMixin`
```python
async def call_llm(self, prompt: str, *, reasoning_class: ReasoningClass | None = None) -> str:
    """Route to SovereignLLMGateway.route_generation()."""
    cls = reasoning_class or getattr(self, "AGENT_REASONING_CLASS", ReasoningClass.LIGHT)
    return await self.gateway.route_generation(prompt, cls, replay_mode=True)
```

**Step 2.2**: Add reasoning_class to apps_rg engines
- `BulletGenerationTask`: `LIGHT` (Qwen for speed)
- `MessageGenerationTask`: `STRATEGIC` (Gemini-2.5-pro for quality)

### Phase 3 — Determinism & Replay

**Step 3.1**: Enforce replay mode by default
- `route_generation()` defaults: `temp=0, top_p=0, replay_mode=True`
- Only agents with `ALLOW_STOCHASTIC=True` can use stochastic sampling

**Step 3.2**: Canonical transcript logging
- Every call logs: `trace_id, prompt_hash, model_id, temperature, response_hash`
- Enables replay verification across runs

### Phase 4 — Migrate Direct Callers

**Step 4.1**: Replace 3 direct `llm_generate()` calls
- `FissionManagerAgent`: Use `route_generation(reasoning_class=ORCHESTRATOR)`
- `CognitiveDispositionAgent`: Use `route_healing()` (actual healing path)
- `StructuredEngineAgent`: Use `route_generation(reasoning_class=STRATEGIC)`

**Step 4.2**: Deprecate direct `llm_generate()` access
- Mark as `@deprecated` in `LLMProviderMixin`
- Add CI ban on direct usage

### Phase 5 — Eliminate Config Duplication

**Step 5.1**: Bridge existing configs to `LLMRoutingPolicy`
- `healing_tier_config.py` → reads from `LLMRoutingPolicy`
- `routing_tier_config.py` → marked deprecated, points to new policy

**Step 5.2**: Wire apps_lic gateway stub
- Even though LIC reasoning is dormant, add placeholder `call_llm()` that routes to `route_generation()`
- Prevents future bypass

### Phase 6 — CI Enforcement

**Step 6.1**: Add comprehensive checks
```python
# ops_scripts/ci/check_llm_routing_compliance.py
- All agents define AGENT_REASONING_CLASS
- No hardcoded model names in agent files
- No direct llm_generate() calls
- All LLM calls go through gateway
```

**Step 6.2**: Add to CI workflow
- Fails PR if any violation detected

---

## 5. Scope Summary

| Phase | Files | N | Priority |
|-------|-------|---|----------|
| 1.1 | `llm_routing_policy.py` | 1 | CRITICAL |
| 1.2 | `SovereignLLMGateway.py` | 1 | CRITICAL |
| 1.3 | `SovereignBaseAgent.py` | 1 | HIGH |
| 2.1 | `mcp_operation_mixin.py` | 1 | **CRITICAL — fixes broken apps_rg** |
| 2.2 | 2 apps_rg engines | 2 | HIGH |
| 3.1 | Gateway + tests | 3 | HIGH |
| 4.1 | 3 agentic_core agents | 3 | HIGH |
| 5.1 | 2 config files | 2 | MEDIUM |
| 6.1 | CI script | 1 | MEDIUM |
| **Total** | | **~18** | |

---

## 6. Model Selection Policy

| ReasoningClass | Default Model | Temperature | Use Case |
|----------------|---------------|-------------|----------|
| DETERMINISTIC | None | N/A | Rule-based agents |
| LIGHT | Qwen2.5-coder-32b | 0 | Fast generation, bulk ops |
| STRATEGIC | Gemini-2.5-pro | 0 | Quality-critical tasks |
| ORCHESTRATOR | Gemini-2.5-pro | 0.7 | Creative planning |
| HEALER | Dynamic by confidence | 0.7 | Failure recovery |

---

## 7. Answers to Clarifying Questions

### Q1: apps_rg default model?
**Answer**: `LIGHT` (Qwen) for bullet generation, `STRATEGIC` (Gemini-2.5-pro) for message generation. Not Pro globally to control costs.

### Q2: Share thresholds?
**Answer**: NO. Healing thresholds (confidence-based) and generation thresholds (reasoning class-based) are separate. Share only model registry and cost policy.

### Q3: All 43 agents in one PR?
**Answer**: NO. Default all to `DETERMINISTIC`, then upgrade only agents that explicitly need LLM. CI will enforce going forward.

---

## 8. Migration Path

```python
# Before (broken)
await self.call_llm(prompt)  # Method doesn't exist!

# After (apps_rg)
response = await self.call_llm(prompt, reasoning_class=ReasoningClass.LIGHT)

# Before (hardcoded)
response = await self.llm_generate(prompt, provider="google", model="gemini-2.5-pro")

# After (agentic_core)
response = await self.gateway.route_generation(prompt, ReasoningClass.ORCHESTRATOR, replay_mode=True)
```

---

## 9. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Production calls inherit healing semantics | Split gateway methods |
| Model name drift | CI ban on literals |
| Replay nondeterminism | Default replay_mode=True |
| Config fragmentation | Single LLMRoutingPolicy |
| Cost explosion | ReasoningClass budgets + LIGHT default |
| Future LIC bypass | Stub gateway now |

---

## 10. Success Criteria

1. All LLM calls route through single gateway
2. Production and healing paths are separate
3. Deterministic replay works by default
4. apps_rg engines functional
5. Zero hardcoded model names in agents
6. CI enforces all invariants
7. Single source of truth for routing policy

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

